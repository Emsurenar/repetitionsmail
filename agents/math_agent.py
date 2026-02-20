"""
Matematik & Datalogi agent.
Ämnen: envariabelanalys, linjär algebra, flervariabelanalys, statistik/sannolikhetsteori, datalogi.
"""

from crewai import Agent, Task, LLM
from typing import List
import config


# Pool of topics the agent can draw from
MATH_TOPIC_POOL = [
    # Envariabelanalys
    "Taylors formel och Lagranges restterm",
    "L'Hôpitals regel och indeterminate former",
    "Riemannsintegralens definition och konvergenskrav",
    "Medelvärdessatsen och dess konsekvenser",
    "Cauchykriteriet för konvergens av serier",
    "Likformig kontinuitet contra punktvis kontinuitet",
    # Linjär algebra
    "Spektralsatsen för symmetriska matriser",
    "Singulärvärdessönderfallet (SVD) och dess tillämpningar",
    "Jordannormalformen och invarianta delrum",
    "Minsta kvadratmetoden och pseudoinvers",
    "Gram-Schmidt och QR-faktorisering",
    "Egenvärden, diagonalisering och diagonaliserbarhetskriterier",
    "Determinantens geometriska tolkning och multilinearitet",
    # Flervariabelanalys
    "Greens formel och plana flöden",
    "Stokes sats: koppling mellan kurv- och ytintegral",
    "Divergenssatsen (Gauss sats) i R³",
    "Implicita funktionssatsen och inversa funktionssatsen",
    "Jacobianmatrisen: kedjeregeln i flera variabler",
    "Lagranges multiplikatorer: villkorlig optimering",
    "Dubbelintegral och variabelsubstitution med Jacobian",
    # Statistik & Sannolikhetsteori
    "Stora talens lag: svag och stark form",
    "Centrala gränsvärdessatsen och Gaussfördelningens dominans",
    "Bayesiansk inferens och Bayess teorem",
    "Markovkedjor och stationär fördelning",
    "Hypotesprövning: typ I- och typ II-fel, p-värde",
    "Maximum likelihood-skattning (MLE)",
    "Betingad förväntning och martingaler",
    # Datalogi
    "Sökteorier i grafer: BFS, DFS och deras komplexitet",
    "Dijkstras algoritm och kortaste vägar",
    "Dynamisk programmering: princip och Bellmansekvationen",
    "P, NP och beräkningskomplexitet",
    "Rödsvarta träd och balanserade sökträd",
    "Hashfunktioner och kollisionshantering",
    "Turingmaskiner och haltningsproblemet",
]


def create_math_agent(llm: LLM) -> Agent:
    return Agent(
        role="Professor i Matematik och Datalogi",
        goal=(
            "Välj ett specifikt matematiskt eller datalogikal ämne och skriv en djupgående, "
            "rigorös repetitionstext på 500 ord för en student som redan har grundläggande förståelse."
        ),
        backstory=(
            "Du är en erfaren matematikprofessor med djup expertis inom analys, linjär algebra, "
            "statistik och datalogi. Du älskar att exponera de subtila, icke-uppenbara aspekterna "
            "av välkända satser och bevis. Du skriver alltid på utmärkt svenska med korrekt "
            "matematisk notation (LaTeX-format inom $...$). Du antar att läsaren känner till "
            "grunderna men vill fördjupa sig. Du fokuserar på nyckelsatser, bevisteknik och "
            "kopplingar till annat material."
        ),
        llm=llm,
        verbose=True,
    )


def create_math_task(agent: Agent, used_topics: List[str]) -> Task:
    used_str = "\n".join(f"- {t}" for t in used_topics) if used_topics else "Inga ännu."

    return Task(
        description=(
            f"ANVÄNDA ÄMNEN DE SENASTE 60 DAGARNA (undvik dessa):\n{used_str}\n\n"
            "DIN UPPGIFT:\n"
            "1. Välj ett ämne från din domän (matematik/datalogi) som INTE finns i listan ovan.\n"
            "2. Skriv en repetitionstext på exakt 500 ord på svenska.\n\n"
            "STRUKTUR:\n"
            "- Börja med raden: TOPIC: [ämnesnamn]\n"
            "- Därefter en H2-rubrik med ämnet (##)\n"
            "- Sätt in kontexten: var passar detta i den matematiska helheten?\n"
            "- Formulera satsens/teoremets exakta statement med matematisk notation\n"
            "- Gå igenom bevisets nyckelsteg (fullständigt bevis behövs ej, men logiken ska vara tydlig)\n"
            "- Lyft minst ett icke-uppenbart korollarium eller tillämpning\n"
            "- Avsluta med en koppling till ett angränsande ämne\n\n"
            "TON: Exakt, rigorös, universitetsanpassad. Anta fördjupade introduktionskurser.\n"
            "LÄNGD: 500 ord (viktigt).\n"
            "FORMAT: Markdown med LaTeX inom $...$ för formler."
        ),
        agent=agent,
        expected_output=(
            "Raden 'TOPIC: [ämnesnamn]' på första raden, sedan en 500-ords repetitionstext "
            "på svenska med korrekt matematisk notation, tydlig struktur och djup analys."
        ),
    )
