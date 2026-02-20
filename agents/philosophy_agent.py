"""
Filosofi & Logik agent.
Ämnen: politisk teori, etik, metaetik, logik, metalogik, metafysik, vetenskapsteori, epistemologi.
"""

from crewai import Agent, Task, LLM
from typing import List
import config


PHILOSOPHY_TOPIC_POOL = [
    # Logik & Metalogik
    "Gödels fullständighetssats: bevisstruktur och semantisk konsekvens",
    "Gödels första ofullständighetssats: oavgörbara satser i PA",
    "Gödels andra ofullständighetssats: konsistens och självreferers",
    "Löwenheim-Skolems sats och relativiteten hos 'oräknbar mängd'",
    "Tarskis odefinierbarhetssats för sanning",
    "Churchs tes och beräkningsbarhet",
    "Intuitionistisk logik: BHK-tolkningen och konstruktivism",
    "Modellteori: kompakthetssatsen och dess konsekvenser",
    # Epistemologi
    "Agrippas trilemma: regress, cirkel eller grundläggning",
    "Gettierproblemet och villkoren för kunskap",
    "Kontextualism om kunskap: indexikala attributioner",
    "Eksternalism vs internalism om mentalt innehåll",
    "Reliabilism: Goldman och det processuella kunskapsbegreppet",
    "Fallibilism och skepticismens gräns",
    # Vetenskapsteori
    "Paradigmskiften och Kuhns normalvetenskap",
    "Poppers falsifikationism och demarkationsproblemet",
    "Quine-Duhem-tesen: teorinedbestämning av evidens",
    "Quine-Putnams oumbärlighetsargument för matematisk realism",
    "Bayesiansk bekräftelseteori",
    "Strukturell realism om vetenskapliga teorier",
    # Metafysik
    "Substans och egenskap: universaliernas problem",
    "Möjliga världar: Lewis modalrealism vs ersatzism",
    "Personlig identitet: psykologisk kontinuitet och Parfits reduktionism",
    "Fri vilja: kompatibilism, inkompatibilism och Frankfurts hierarkiska modell",
    "Tid och kausalitet: Humeansk och anti-Humeansk orsak",
    "Grounding-relationen och metafysisk prioritet",
    # Etik & Metaetik
    "Emotivism (Ayer, Stevenson) och kritiken från Hare",
    "Moralisk realism: Mackie och queernessargumentet",
    "Kontraktarism: Scanlon och 'what we owe to each other'",
    "Konsekventialismens demandingness-invändning",
    "Dygdetik: Aristoteles fronesis och modern neoaristotelism",
    "Metaetisk expressivism: Blackburns quasi-realism",
    # Politisk teori
    "Rawls rättviseteori: okunnighetens slöja och differensprincipen",
    "Nozicks rättighetsteori och det minimala staten",
    "Habermas kommunikativa rationalitet och diskursetik",
    "Republicanism: Philip Pettit och frihet som icke-dominans",
]


def create_philosophy_agent(llm: LLM) -> Agent:
    return Agent(
        role="Analytisk Filosof och Logiker",
        goal=(
            "Välj ett specifikt filosofiskt problem, argument eller sats och skriv en djupgående "
            "repetitionstext på 500 ord som exponerar argumentets logiska struktur, styrka och svagheter."
        ),
        backstory=(
            "Du är en skarp analytisk filosof med specialisering i logik, epistemologi och metaetik. "
            "Du är känd för att aldrig kompromissa med precision – varje distinktion du gör är genomtänkt. "
            "Du skriver på utmärkt svenska och anpassar din ton efter en läsare som har grundläggande "
            "filosofikunskaper men vill nå kandidat- eller masternivå. Du är aldrig banal och undviker "
            "plattityder som 'filosofi handlar om de stora frågorna'. Du formulerar alltid argument "
            "i explicita premissform när det är lämpligt."
        ),
        llm=llm,
        verbose=True,
    )


def create_philosophy_task(agent: Agent, used_topics: List[str]) -> Task:
    used_str = "\n".join(f"- {t}" for t in used_topics) if used_topics else "Inga ännu."

    return Task(
        description=(
            f"ANVÄNDA ÄMNEN DE SENASTE 60 DAGARNA (undvik dessa):\n{used_str}\n\n"
            "DIN UPPGIFT:\n"
            "1. Välj ett ämne från din domän (filosofi/logik) som INTE finns i listan ovan.\n"
            "2. Skriv en repetitionstext på exakt 500 ord på svenska.\n\n"
            "STRUKTUR:\n"
            "- Börja med raden: TOPIC: [ämnesnamn]\n"
            "- Sedan H2-rubrik med ämnet (##)\n"
            "- Presentera det specifika problemet/argumentet/satsen med korrekt terminologi\n"
            "- Exponera argumentets logiska struktur steg för steg (gärna P1, P2, … C)\n"
            "- Redovisa minst en invändning och svaret på den\n"
            "- Om tillämpligt: koppla till en angränsande tes eller sats\n"
            "- Avsluta med en öppen fråga som driver vidare reflektion\n\n"
            "TON: Analytisk, precis, universitetsanpassad. "
            "Anta att läsaren har fördjupade introduktionskurser bakom sig.\n"
            "LÄNGD: 500 ord.\n"
            "FORMAT: Markdown."
        ),
        agent=agent,
        expected_output=(
            "Raden 'TOPIC: [ämnesnamn]' på första raden, sedan en 500-ords repetitionstext "
            "på svenska med rigorös argumentationsstruktur, minst en invändning, och en "
            "avslutande öppen fråga."
        ),
    )
