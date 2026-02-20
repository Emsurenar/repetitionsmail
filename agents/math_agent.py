"""
Matematik & Datalogi agent.
Ämnen: envariabelanalys, linjär algebra, flervariabelanalys, statistik/sannolikhetsteori, datalogi.
Nivå: Grundkurser vid universitet (Introductory university level).
"""

from crewai import Agent, Task, LLM
from typing import List
import config


# Pool of topics focused on introductory university courses
MATH_TOPIC_POOL = [
    # Envariabelanalys (Calculus I)
    "Taylors formel och linjär approximation",
    "L'Hôpitals regel och gränsvärden",
    "Integralkalkylens fundamentalsats",
    "Medelvärdessatsen för derivator",
    "Partiell integration och variabelsubstitution",
    "Konvergens av serier: kvotkriteriet och jämförelsekriteriet",
    # Linjär algebra (Linear Algebra)
    "Linjära ekvationssystem och Gauss-elimination",
    "Matrisinverser och determinanter",
    "Vektorrum, baser och dimension",
    "Linjära avbildningar och matrisrepresentation",
    "Egenvärden och diagonalisering av matriser",
    "Minsta kvadratmetoden och projektioner",
    "Gram-Schmidt-processen och ortogonalitet",
    # Flervariabelanalys (Calculus II/Multivariable)
    "Partiella derivator och differentierbarhet",
    "Gradienten, riktningsderivata och tangentplan",
    "Kedjeregeln i flera variabler",
    "Optimering: stationära punkter och extremvärden",
    "Lagranges multiplikatorer för villkorlig optimering",
    "Dubbelintegraler över rektangulära och allmänna områden",
    "Variabelsubstitution i dubbelintegraler (polära koordinater)",
    # Statistik & Sannolikhetsteori (Probability & Stats)
    "Sannolikhetslära: betingad sannolikhet och oberoende",
    "Diskreta och kontinuerliga slumpvariabler",
    "Väntevärde, varians och standardavvikelse",
    "Normalfördelningen och Centrala gränsvärdessatsen",
    "Hypotesprövning: p-värden och signifikansnivåer",
    "Konfidensintervall för medelvärden",
    "Enkel linjär regression",
    # Datalogi (Intro CS / Algorithms)
    "Sökningsalgoritmer: Binärsökning och linjärsökning",
    "Sorteringsalgoritmer: Quicksort och Mergesort",
    "Asymptotisk komplexitet: Big O-notation",
    "Listor, stackar och köer",
    "Binära sökträd: struktur och operationer",
    "Hash-tabeller: princip och kollisionshantering",
    "Grundläggande grafteori: representationer (matris/lista)",
]


def create_math_agent(llm: LLM) -> Agent:
    return Agent(
        role="Grundkurs-pedagog i Matematik och Datalogi",
        goal=(
            "Välj ett centralt ämne från de grundläggande universitetskurserna i matematik eller datalogi "
            "och skriv en pedagogisk, men tekniskt korrekt, repetitionstext på 500 ord."
        ),
        backstory=(
            "Du är en pedagogisk universitetslektor som undervisar i de grundläggande kurserna: "
            "envariabelanalys, linjär algebra, flervariabelanalys, statistik och datalogi. "
            "Din styrka är att förklara de matematiska grundpelarna på ett sätt som känns "
            "substantiellt men aldrig förutsätter kunskap utöver dessa grundkurser. "
            "Du skriver alltid på utmärkt svenska. "
            "VIKTIGT: Du använder ALDRIG LaTeX-syntax (som \\begin{pmatrix} eller $...$). "
            "Istället använder du lättläst 'textboksnotation' (ASCII-math) i kodblock (```math). "
            "Exempel: Använd det(A) = ad - bc istället för matriser, eller [ [a, b], [c, d] ] för matriser. "
            "Använd integraler(f(x)dx) istället för komplexa symboler. Målet är att det ska vara läsbart i e-post."
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
            "1. Välj ett ämne från din domän (introducerande matematiska grundkurser) som INTE finns i listan ovan.\n"
            "2. Skriv en repetitionstext på exakt 500 ord på svenska.\n\n"
            "STRUKTUR:\n"
            "- Börja med raden: TOPIC: [ämnesnamn]\n"
            "- Därefter en H2-rubrik med ämnet (##)\n"
            "- Sätt in kontexten: varför är detta viktigt i grundutbildningen?\n"
            "- Förklara huvudkonceptet/satsen pedagogiskt med teknisk stringens\n"
            "- Gå igenom ett konkret exempel eller ett beräkningssteg i ett ```math kodblock\n"
            "- Lyft en vanlig fallgrop eller ett viktigt observation\n"
            "- Avsluta med en kort koppling till nästa steg i ämnet\n\n"
            "FORMAT-REGLER:\n"
            "- ANVÄND ALDRIG LaTeX (inga dollartecken, inga backslashes som \\det eller \\begin).\n"
            "- Använd ASCII-math i kodblock (```math) för alla formler. Exempel:\n"
            "  - det(A) = ad - bc\n"
            "  - sqrt(x^2 + y^2)\n"
            "  - f'(x) = 2x\n"
            "  - Matriser: [ [1, 2], [3, 4] ]\n"
            "LÄNGD: 500 ord (viktigt).\n"
            "TON: Pedagogisk, tydlig, på introducerande universitetsnivå (grundkurs)."
        ),
        agent=agent,
        expected_output=(
            "En 500-ords repetitionstext på svenska med ASCII-math i kodblock (ingen LaTeX!), "
            "pedagogiskt anpassad för grundkursnivå."
        ),
    )
