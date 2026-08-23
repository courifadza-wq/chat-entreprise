"""Étape 01 — Chat interactif LangChain. Gemini en premier (NVIDIA chat = 403 chez toi)."""

import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

SYSTEME = (
    "Tu es un assistant IA pédagogique, précis et bienveillant. "
    "Tu réponds en français. Tu structures clairement les réponses et "
    "tu signales honnêtement toute incertitude."
)


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
            temperature=0.3,
            max_completion_tokens=600,
        )
    if cerebras:
        print("Fournisseur : Cerebras")
        return ChatOpenAI(
            model="llama-3.3-70b",
            api_key=cerebras,
            base_url="https://api.cerebras.ai/v1",
            temperature=0.3,
            max_completion_tokens=600,
        )
    if groq:
        print("Fournisseur : Groq")
        return ChatOpenAI(
            model="llama-3.1-8b-instant",
            api_key=groq,
            base_url="https://api.groq.com/openai/v1",
            temperature=0.3,
            max_completion_tokens=600,
        )
    raise RuntimeError(
        "Aucune clé utilisable. Ajoutez GEMINI_API_KEY (ou CEREBRAS / GROQ) dans le .env"
    )


def afficher_aide() -> None:
    print(
        "\nCommandes disponibles :\n"
        "  /aide        afficher les commandes\n"
        "  /historique  afficher la conversation\n"
        "  /reset       effacer la conversation\n"
        "  /save        sauvegarder la conversation en JSON\n"
        "  /quit        quitter le programme\n"
    )


def sauvegarder(messages: list) -> Path:
    dossier = Path("conversations")
    dossier.mkdir(exist_ok=True)
    horodatage = datetime.now().strftime("%Y%m%d_%H%M%S")
    chemin = dossier / f"conversation_{horodatage}.json"
    donnees = [
        {"role": message.type, "content": str(message.content)}
        for message in messages
        if message.type != "system"
    ]
    chemin.write_text(json.dumps(donnees, ensure_ascii=False, indent=2), encoding="utf-8")
    return chemin


def main() -> None:
    load_dotenv()
    modele = creer_modele()
    messages = [SystemMessage(content=SYSTEME)]

    print("=" * 55)
    print(" CHAT INTERACTIF — LANGCHAIN")
    print("=" * 55)
    print("Tapez /aide pour afficher les commandes.\n")

    while True:
        question = input("Vous : ").strip()
        if not question:
            continue

        commande = question.lower()
        if commande == "/quit":
            print("À bientôt !")
            break
        if commande == "/aide":
            afficher_aide()
            continue
        if commande == "/reset":
            messages = [SystemMessage(content=SYSTEME)]
            print("Mémoire effacée.\n")
            continue
        if commande == "/historique":
            print("\n--- HISTORIQUE ---")
            for message in messages:
                if message.type != "system":
                    auteur = "Vous" if message.type == "human" else "IA"
                    print(f"{auteur} : {message.content}")
            print("------------------\n")
            continue
        if commande == "/save":
            print(f"Conversation sauvegardée : {sauvegarder(messages)}\n")
            continue

        messages.append(HumanMessage(content=question))
        morceaux: list[str] = []
        print("IA : ", end="", flush=True)
        try:
            for fragment in modele.stream(messages):
                contenu = fragment.content
                texte = contenu if isinstance(contenu, str) else str(contenu)
                print(texte, end="", flush=True)
                morceaux.append(texte)
            print("\n")
            messages.append(AIMessage(content="".join(morceaux)))
        except Exception as erreur:
            messages.pop()
            print(f"\nErreur API : {erreur}\n")


if __name__ == "__main__":
    main()
