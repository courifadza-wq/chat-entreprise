"""Phase 1 — Étape 2 : conversation avec mémoire et API NVIDIA."""

import os
from dotenv import load_dotenv
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_nvidia_ai_endpoints import ChatNVIDIA

load_dotenv()

if not os.getenv("NVIDIA_API_KEY"):
    raise RuntimeError(
        "Clé absente : créez un fichier .env contenant "
        "NVIDIA_API_KEY=nvapi-votre_cle"
    )

# Une mémoire distincte sera conservée pour chaque session.
sessions: dict[str, InMemoryChatMessageHistory] = {}


def obtenir_historique(session_id: str) -> InMemoryChatMessageHistory:
    """Crée ou récupère l'historique d'une conversation."""
    if session_id not in sessions:
        historique = InMemoryChatMessageHistory()
        historique.add_message(
            SystemMessage(
                content=(
                    "Tu es un assistant pédagogique. Réponds en français, "
                    "simplement et avec des exemples courts."
                )
            )
        )
        sessions[session_id] = historique
    return sessions[session_id]


modele = ChatNVIDIA(
    model="meta/llama-3.1-8b-instruct",
    temperature=0.2,
    max_tokens=400,
)

# Cette enveloppe ajoute automatiquement les anciens messages à chaque appel.
chat_avec_memoire = RunnableWithMessageHistory(
    modele,
    obtenir_historique,
)

session_id = "utilisateur-1"
config = {"configurable": {"session_id": session_id}}

print("Chat NVIDIA avec mémoire")
print("Commandes : /historique, /reset, /quit\n")

while True:
    question = input("Vous : ").strip()

    if not question:
        continue
    if question.lower() == "/quit":
        print("Conversation terminée.")
        break
    if question.lower() == "/reset":
        sessions.pop(session_id, None)
        print("Mémoire effacée.\n")
        continue
    if question.lower() == "/historique":
        historique = obtenir_historique(session_id)
        print("\n--- HISTORIQUE ---")
        for message in historique.messages:
            print(f"{message.type.upper()} : {message.content}")
        print("------------------\n")
        continue

    try:
        reponse = chat_avec_memoire.invoke(
            [HumanMessage(content=question)],
            config=config,
        )
        print(f"IA : {reponse.content}\n")
    except Exception as erreur:
        print(f"Erreur pendant l'appel NVIDIA : {erreur}\n")
