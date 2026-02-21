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
    "Riemannsummor och integrationens rigorösa definition",
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
        role="Universitetslektor i Matematik och Datalogi",
        goal=(
            "Välj ett centralt och något mer avancerat ämne från universitetskurser i matematik eller datalogi "
            "(t.ex. Riemannsummor framför enklare derivata) "
            "och skriv en pedagogisk, men matematiskt rigorös repetitionstext på 500 ord."
        ),
        backstory=(
            "Du är en pedagogisk universitetslektor som undervisar i de grundläggande kurserna: "
            "envariabelanalys, linjär algebra, flervariabelanalys, statistik och datalogi. "
            "Din styrka är att förklara de matematiska grundpelarna på ett sätt som känns "
            "substantiellt men aldrig förutsätter kunskap utöver dessa grundkurser. "
            "Du skriver alltid på utmärkt svenska. "
            "VIKTIGT: För matematiska formler använder du enbart LaTeX-notation inom $$ ... $$. "
            "Exempel: Använd $$\\det(A) = ad - bc$$ för formler på egna rader. "
            "Dessa kommer att renderas som bilder i mailet, så var noga med att syntaxen är korrekt."
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
            "- Presentera centrala formler i fristående block med $$ [latex] $$\n"
            "- Gå igenom ett konkret exempel eller ett beräkningssteg\n"
            "- Lyft en vanlig fallgrop eller ett viktigt observation\n"
            "- Avsluta med en kort koppling till nästa steg i ämnet\n\n"
            "FORMAT-REGLER:\n"
            "- Använd inline-latex ($...$) för enskilda variabler och korta uttryck i löptext. \n"
            "- Använd $$...$$ ENDAST för större, fristående formler på egna rader.\n"
            "LÄNGD: 500 ord (viktigt).\n"
            "TON: Pedagogisk, tydlig, på introducerande universitetsnivå (grundkurs)."
        ),
        agent=agent,
        expected_output=(
            "En 500-ords repetitionstext på svenska med korrekt LaTeX-notation inom $$ ... $$ för formler."
        ),
    )
