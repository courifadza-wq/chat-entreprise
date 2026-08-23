"""Étape 01 — Lire un PDF et poser des questions (Gemini, pas NVIDIA)."""

import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

LIMITE_CARACTERES = 18_000


def creer_modele() -> ChatOpenAI:
    gemini = os.getenv("GEMINI_API_KEY", "").strip()
    cerebras = os.getenv("CEREBRAS_API_KEY", "").strip()
    groq = os.getenv("GROQ_API_KEY", "").strip()
    if gemini:
        print("Fournisseur : Gemini")
        return ChatOpenAI(
            model="gemini-3.6-flash",
            api_key=gemini,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            temperature=0.1,
            max_completion_tokens=600,
        )
    if cerebras:
        print("Fournisseur : Cerebras")
        return ChatOpenAI(
            model="llama-3.3-70b",
            api_key=cerebras,
            base_url="https://api.cerebras.ai/v1",
            temperature=0.1,
            max_completion_tokens=600,
        )
    if groq:
        print("Fournisseur : Groq")
        return ChatOpenAI(
            model="llama-3.1-8b-instant",
            api_key=groq,
            base_url="https://api.groq.com/openai/v1",
            temperature=0.1,
            max_completion_tokens=600,
        )
    raise RuntimeError("Ajoutez GEMINI_API_KEY dans le .env")


def charger_pdf(chemin: Path) -> tuple[list, str]:
    documents = PyPDFLoader(str(chemin)).load()
    texte = "\n\n".join(
        f"--- PAGE {numero} ---\n{document.page_content}"
        for numero, document in enumerate(documents, start=1)
    )
    return documents, texte


def main() -> None:
    load_dotenv()
    analyseur = argparse.ArgumentParser(description="Questions sur un PDF")
    analyseur.add_argument("pdf", help="Chemin du PDF")
    arguments = analyseur.parse_args()

    chemin = Path(arguments.pdf)
    if not chemin.is_file():
        raise FileNotFoundError(f"Fichier introuvable : {chemin}")

    documents, texte_complet = charger_pdf(chemin)
    texte_utilise = texte_complet[:LIMITE_CARACTERES]

    print(f"PDF chargé : {chemin.name}")
    print(f"Nombre de pages : {len(documents)}")
    print(f"Caractères extraits : {len(texte_complet)}")

    modele = creer_modele()
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Tu réponds uniquement à partir du document fourni. "
                "Si la réponse n'est pas dans le document, dis clairement : "
                "Je ne trouve pas cette information dans le document. "
                "Lorsque c'est possible, indique le numéro de page.",
            ),
            ("human", "DOCUMENT :\n{document}\n\nQUESTION :\n{question}"),
        ]
    )
    chaine = prompt | modele | StrOutputParser()

    print("\nPosez vos questions. Commandes : /resume, /quit\n")
    while True:
        question = input("Vous : ").strip()
        if not question:
            continue
        if question.lower() == "/quit":
            print("Analyse terminée.")
            break
        if question.lower() == "/resume":
            question = (
                "Résume ce document : sujet, idées principales, conclusion."
            )
        try:
            reponse = chaine.invoke({"document": texte_utilise, "question": question})
            print(f"\nIA : {reponse}\n")
        except Exception as erreur:
            print(f"\nErreur API : {erreur}\n")


if __name__ == "__main__":
    main()
