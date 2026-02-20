"""
Main orchestrator for Repetitionsmail.
Runs three CrewAI agents in parallel, formats the output into a premium HTML email,
logs used topics to SQLite, and sends via Gmail.

Usage:
    python main.py           # Full run – sends email
    python main.py --test    # Saves HTML to logs/, does not send
"""

import sys
import re
import logging
import concurrent.futures
from datetime import datetime
from pathlib import Path

from crewai import Crew, LLM

import config
from database import TopicDatabase
from agents import (
    create_math_agent,       create_math_task,
    create_philosophy_agent, create_philosophy_task,
    create_society_agent,    create_society_task,
)
from tools.gmail_sender import GmailSender

# ── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s  %(levelname)-8s  %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_DIR / 'repetitionsmail.log'),
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)


# ── LLM factory ─────────────────────────────────────────────────────────────
def get_llm() -> LLM:
    if not config.ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY is not set")
    return LLM(
        model=config.LLM_MODEL,
        api_key=config.ANTHROPIC_API_KEY,
        temperature=0.75,
        max_tokens=4096,
    )


# ── Markdown → HTML ──────────────────────────────────────────────────────────
def _inline(text: str) -> str:
    """Convert inline markdown to HTML."""
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__(.+?)__',     r'<strong>\1</strong>', text)
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    # If agent used $...$ notation, wrap it in a code tag for better readability in light theme
    text = re.sub(r'\$([^$]+)\$', r'<code>\1</code>', text)
    return text


def md_to_html(text: str) -> str:
    """Convert a markdown string to HTML paragraphs/headings/lists."""
    # Pre-process code blocks (```math ... ```) to use our custom class
    # Handle both ```math and just ``` code blocks
    text = re.sub(r'```(?:math)?\s*\n(.*?)\n```', r'<div class="math-block">\1</div>', text, flags=re.DOTALL)
    
    lines = text.split('\n')
    out = []
    in_list = False
    in_math_block = False

    for line in lines:
        s = line.strip()
        
        # Check if we are inside a pre-processed math block from the regex above
        if '<div class="math-block">' in line:
            out.append(line)
            in_math_block = True
            if '</div>' in line: in_math_block = False
            continue
        if in_math_block:
            out.append(line)
            if '</div>' in line: in_math_block = False
            continue

        if not s:
            if in_list:
                out.append('</ul>')
                in_list = False
            out.append('')
            continue
            
        if s.startswith('### '):
            out.append(f'<h3 style="font-size:16px;font-weight:600;color:#1e293b;margin:18px 0 6px;">{_inline(s[4:])}</h3>')
        elif s.startswith('## '):
            out.append(f'<h2 style="font-size:18px;font-weight:700;color:#0f172a;margin:24px 0 8px;">{_inline(s[3:])}</h2>')
        elif s.startswith('# '):
            out.append(f'<h1 style="font-size:20px;font-weight:700;color:#0f172a;margin:24px 0 10px;">{_inline(s[2:])}</h1>')
        elif s.startswith('> '):
            out.append(f'<blockquote>{_inline(s[2:])}</blockquote>')
        elif re.match(r'^[\-\*]\s+', s):
            if not in_list:
                out.append('<ul style="color:#334155; margin:10px 0 16px; padding-left:22px;">')
                in_list = True
            content = re.sub(r'^[\-\*]\s+', '', s)
            out.append(f'<li style="margin-bottom:8px;">{_inline(content)}</li>')
        else:
            if in_list:
                out.append('</ul>')
                in_list = False
            out.append(f'<p style="margin-bottom:16px;">{_inline(s)}</p>')

    if in_list:
        out.append('</ul>')
    return '\n'.join(out)


# ── Topic extraction ─────────────────────────────────────────────────────────
def extract_topic_and_body(raw: str) -> tuple[str, str]:
    """
    Extract the TOPIC: line and return (topic, body_without_topic_line).
    Handles variations like **TOPIC:** or leading spaces.
    Falls back to 'Okänt ämne' if TOPIC: not found.
    """
    topic = 'Okänt ämne'
    lines = raw.strip().split('\n')
    body_lines = []
    
    # Regex to catch TOPIC:, **TOPIC:**, Topic: etc.
    topic_pattern = re.compile(r'^\s*\*?\*?TOPIC:\*?\*?\s*(.*)', re.IGNORECASE)
    
    for line in lines:
        match = topic_pattern.match(line.strip())
        if match:
            topic = match.group(1).strip()
            # Remove optional trailing bolding
            topic = re.sub(r'\*+\s*$', '', topic).strip()
        else:
            body_lines.append(line)
            
    body = '\n'.join(body_lines).strip()
    return topic, body


# ── Per-crew runner (for parallel execution) ─────────────────────────────────
def run_crew(label: str, crew: Crew) -> str:
    logger.info(f"[{label}] Starting crew…")
    result = crew.kickoff()
    text = str(result)
    logger.info(f"[{label}] Done – {len(text)} chars")
    return text


# ── HTML email assembly ───────────────────────────────────────────────────────
WEEKDAY_ACCENT = [
    "#4facfe",   # Måndag  – cyan-blue
    "#a78bfa",   # Tisdag  – purple
    "#34d399",   # Onsdag  – emerald
    "#fb923c",   # Torsdag – orange
    "#fbbf24",   # Fredag  – amber
    "#f472b6",   # Lördag  – pink
    "#64748b",   # Söndag  – slate
]

def accent_bg(color: str) -> str:
    return f"{color}14"


def build_html(
    math_topic: str,    math_html: str,
    phil_topic: str,    phil_html: str,
    society_topic: str, society_html: str,
    date_str: str,
    accent: str,
) -> str:
    template_path = config.TEMPLATE_DIR / 'email.html'
    tmpl = template_path.read_text(encoding='utf-8')

    tmpl = tmpl.replace('{{ date }}',           date_str)
    tmpl = tmpl.replace('{{ accent_color }}',   accent)
    tmpl = tmpl.replace('{{ accent_bg }}',      accent_bg(accent))
    tmpl = tmpl.replace('{{ math_topic }}',     math_topic)
    tmpl = tmpl.replace('{{ math_content }}',   math_html)
    tmpl = tmpl.replace('{{ phil_topic }}',     phil_topic)
    tmpl = tmpl.replace('{{ phil_content }}',   phil_html)
    tmpl = tmpl.replace('{{ society_topic }}',  society_topic)
    tmpl = tmpl.replace('{{ society_content }}',society_html)
    return tmpl


def swedish_date() -> str:
    today = datetime.now()
    day = ['Måndag','Tisdag','Onsdag','Torsdag','Fredag','Lördag','Söndag'][today.weekday()]
    month = ['januari','februari','mars','april','maj','juni',
             'juli','augusti','september','oktober','november','december'][today.month - 1]
    return f"{day} {today.day} {month} {today.year}"


# ── Main ─────────────────────────────────────────────────────────────────────
def run(test_mode: bool = False):
    logger.info("=== Repetitionsmail starting ===")

    if not config.validate_config():
        logger.error("Config validation failed – aborting")
        sys.exit(1)

    db  = TopicDatabase()
    llm = get_llm()

    # Load used topics per category
    math_used    = db.get_recent_topics('math',        days=60)
    phil_used    = db.get_recent_topics('philosophy',  days=60)
    soc_used     = db.get_recent_topics('society',     days=60)

    # Build agents & tasks
    math_agent    = create_math_agent(llm)
    phil_agent    = create_philosophy_agent(llm)
    soc_agent     = create_society_agent(llm)

    math_task     = create_math_task(math_agent,    math_used)
    phil_task     = create_philosophy_task(phil_agent, phil_used)
    soc_task      = create_society_task(soc_agent,  soc_used)

    # Three independent crews
    crew_math = Crew(agents=[math_agent], tasks=[math_task],  verbose=True)
    crew_phil = Crew(agents=[phil_agent], tasks=[phil_task],  verbose=True)
    crew_soc  = Crew(agents=[soc_agent],  tasks=[soc_task],   verbose=True)

    # Run in parallel
    logger.info("Launching three crews in parallel…")
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        futures = {
            pool.submit(run_crew, 'math',        crew_math): 'math',
            pool.submit(run_crew, 'philosophy',  crew_phil): 'philosophy',
            pool.submit(run_crew, 'society',     crew_soc):  'society',
        }
        results = {}
        for fut in concurrent.futures.as_completed(futures):
            label = futures[fut]
            try:
                results[label] = fut.result()
            except Exception as exc:
                logger.error(f"[{label}] crew failed: {exc}", exc_info=True)
                results[label] = f"TOPIC: Fel\n\nKunde inte generera innehåll: {exc}"

    # Extract topics + convert to HTML
    math_topic,    math_body    = extract_topic_and_body(results['math'])
    phil_topic,    phil_body    = extract_topic_and_body(results['philosophy'])
    society_topic, society_body = extract_topic_and_body(results['society'])

    math_html    = md_to_html(math_body)
    phil_html    = md_to_html(phil_body)
    society_html = md_to_html(society_body)

    # Build email
    today   = datetime.now()
    accent  = WEEKDAY_ACCENT[today.weekday()]
    date_sv = swedish_date()

    html = build_html(
        math_topic,    math_html,
        phil_topic,    phil_html,
        society_topic, society_html,
        date_sv, accent,
    )

    subject = f"Repetitionsmail · {math_topic.split(':')[0]} · {phil_topic.split(':')[0]} · {date_sv}"

    if test_mode:
        ts = today.strftime('%Y%m%d_%H%M%S')
        out = config.LOG_DIR / f"preview_{ts}.html"
        out.write_text(html, encoding='utf-8')
        logger.info(f"✅ TEST MODE – HTML saved to {out}")
        print(f"\n{'='*60}")
        print(f"Preview: {out}")
        print(f"Subjects: {subject}")
        print(f"Topics: Math={math_topic!r}, Phil={phil_topic!r}, Soc={society_topic!r}")
        print(f"{'='*60}\n")
    else:
        sender = GmailSender()
        ok = sender.send_email(
            recipient=config.GMAIL_RECIPIENT,
            subject=subject,
            html_content=html,
        )
        if ok:
            # Log topics to DB only after successful send
            db.log_topic('math',       math_topic)
            db.log_topic('philosophy', phil_topic)
            db.log_topic('society',    society_topic)
            logger.info("✅ Email sent and topics logged")
        else:
            logger.error("❌ Email send failed – topics NOT logged")
            sys.exit(1)


if __name__ == '__main__':
    test_mode = '--test' in sys.argv
    if test_mode:
        print("🧪 TEST MODE – saves HTML to logs/, does not send email")
    run(test_mode=test_mode)
