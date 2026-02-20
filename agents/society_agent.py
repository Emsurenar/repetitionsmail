"""
Samhälle & Historia agent.
Ämnen: nationalekonomi, svensk juridik, spelteori, geopolitik, historia.
"""

from crewai import Agent, Task, LLM
from typing import List
import config


SOCIETY_TOPIC_POOL = [
    # Nationalekonomi
    "Nash-jämvikt: definition, bevis för existens och tillämpningar",
    "Spelteori och fångarnas dilemma: upprepad interaktion och Folk-satsen",
    "Allmän jämviktsteori: Arrow-Debreu och välfärdsteorembegreppet",
    "Moralisk risk (moral hazard) och principalagentproblemet",
    "Adverse selection och signalering: Spences arbetsmarknadsmodell",
    "Keynesianisk multiplikator kontra ricardiansk ekvivalens",
    "Monetarism: kvantitetsteorin och Friedmans penningpolitikskritik",
    "Rationalitetsantagandet och beteendeekonomi: prospect theory",
    "Offentliga varor och Samuelsons betingelse",
    "Coase-teoremet och externaliters internalisering",
    # Spelteori
    "Bakåtinduktion i extensivformsspel",
    "Auktionsteori: first-price vs second-price och intäktsekvalens",
    "Förhandlingsteori: Nash-lösningen och Rubinsteins alternansmodell",
    "Bayesiansk Nash-jämvikt och ofullständig information",
    "Evolutionär spelteori: evolutionärt stabila strategier",
    # Geopolitik & Internationella relationer
    "Westfaliska systemet och statssuvereniteten som princip",
    "Realism i IR: Morgenthau, det nationella intresset och maktbalans",
    "Liberalism i IR: demokratisk fred och institutionalism",
    "Konstruktivism: Wendt och anarkismens sociala konstruktion",
    "Kärnvapenstrategi: MAD, first-strike-stabilitet och utvidgad avskräckning",
    "Konflikten mellan Indien och Pakistan: Kashmir, kärnvapen och Simla-avtalet",
    "Kinas uppgång och Thukydidesfällan: hegemonisk övergångsteori",
    "NATO:s kollektiva försvar: Artikel 5 och burden-sharing",
    # Historia
    "Leviathan – Hobbes statsfilosofi och kontraktsteorin",
    "Den westfaliska freden 1648 och den moderna statens framväxt",
    "Kolonialism och dess ekonomiska strukturer: beroendeteorin",
    "Kallt krigets logik: bipoläritet, proxykrig och avspänning",
    "Industrialiseringens genombrott och den enkuffenesiska omvandlingen",
    "Nationalsocialism och Förintelsen: ideologins genealogi",
    "Dekolonisering: Bandung-konferensen och Tredjevärldsprojektet",
    # Svensk juridik
    "Legalitetsprincipen i svensk straffrätt (1 kap. 1 § BrB)",
    "Proportionalitetsprincipen och dess roll i förvaltningsrätten",
    "RF 2 kap. och de grundlagsskyddade fri- och rättigheterna",
    "Culpabedömningen i skadeståndsrätten: Learned Hand-formeln",
    "Prejudikatvärdet och prejudikatlösning i HD och HFD",
    "Avtalsbundenhet: anbud-acceptmodellen och 1 § AvtL",
    "Oskälighetsrekvisitet och 36 § AvtL",
]


def create_society_agent(llm: LLM) -> Agent:
    return Agent(
        role="Professor i Statsvetenskap, Nationalekonomi och Historia",
        goal=(
            "Välj ett specifikt ämne inom nationalekonomi, juridik, spelteori, geopolitik eller historia "
            "och skriv en djupgående repetitionstext på 500 ord som integrerar teori med historisk/institutionell kontext."
        ),
        backstory=(
            "Du är en bred samhällsvetare med djup förankring i ekonomisk teori, juridik och historia. "
            "Du ser alltid institutioner och incitament som nycklar till förståelse. Du skriver på utmärkt "
            "svenska och antar att läsaren har fördjupade introduktionskurser bakom sig. Du blandar frimodigt "
            "formell teori (t.ex. spelteori) med historisk kontextualisering. "
            "VIKTIGT: För matematiska eller tekniska uttryck (t.ex. spelteoretiska matriser) använder du "
            "LaTeX-notation inom $$ ... $$. Dessa renderas som bilder i mailet."
        ),
        llm=llm,
        verbose=True,
    )


def create_society_task(agent: Agent, used_topics: List[str]) -> Task:
    used_str = "\n".join(f"- {t}" for t in used_topics) if used_topics else "Inga ännu."

    return Task(
        description=(
            f"ANVÄNDA ÄMNEN DE SENASTE 60 DAGARNA (undvik dessa):\n{used_str}\n\n"
            "DIN UPPGIFT:\n"
            "1. Välj ett ämne från din domän som INTE finns i listan ovan.\n"
            "2. Skriv en repetitionstext på exakt 500 ord på svenska.\n\n"
            "STRUKTUR:\n"
            "- Börja med raden: TOPIC: [ämnesnamn]\n"
            "- Sedan H2-rubrik med ämnet (##)\n"
            "- Presentera problemet/teorin med korrekt terminologi\n"
            "- Redovisa det formella/juridiska/teoretiska kärninnehållet (använd $$ [latex] $$ för formler)\n"
            "- Använd standard LaTeX-symboler som \\geq, \\leq, \\neq, \\approx.\n"
            "- Ge minst ett historiskt eller empiriskt exempel som belyser teorin\n"
            "- Diskutera en invändning eller ett alternativt perspektiv\n"
            "- Koppla till ett angränsande ämne i avslutningen\n\n"
            "FORMAT-REGLER:\n"
            "- Använd inline-latex ($...$) för enskilda variabler och korta uttryck i löptext. \n"
            "- Använd $$...$$ ENDAST för större, fristående formler på egna rader.\n"
            "LÄNGD: 500 ord.\n"
            "TON: Institutionell, analytisk, saklig."
        ),
        agent=agent,
        expected_output=(
            "En 500-ords repetitionstext på svenska med tekniska uttryck i LaTeX inom $$ ... $$."
        ),
    )
