"""Étape 01 — Assistant Streamlit LangChain (Gemini / Cerebras / Groq)."""

import os

import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

SYSTEME = (
    "Tu es un assistant IA pédagogique, précis et bienveillant. "
    "Réponds en français avec une structure claire."
)

FOURNISSEURS = {
    "Gemini": {
        "env": "GEMINI_API_KEY",
        "base": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "modele": "gemini-3.6-flash",
    },
    "Cerebras": {
        "env": "CEREBRAS_API_KEY",
        "base": "https://api.cerebras.ai/v1",
        "modele": "llama-3.3-70b",
    },
    "Groq": {
        "env": "GROQ_API_KEY",
        "base": "https://api.groq.com/openai/v1",
        "modele": "llama-3.1-8b-instant",
    },
}

st.set_page_config(page_title="Assistant métier", layout="centered")
st.title("Assistant métier")
st.caption("Étape 01 — Développeur LLM Junior · LangChain")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("Compte")
    nom = st.selectbox("Fournisseur", list(FOURNISSEURS))
    conf = FOURNISSEURS[nom]
    cle = (os.getenv(conf["env"]) or "").strip()
    st.caption(f"Modèle : {conf['modele']}")
    if not cle:
        st.error(f"Clé {conf['env']} absente du .env")
    temperature = st.slider("Température", 0.0, 1.0, 0.2, 0.1)
    if st.button("Nouvelle conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

saisie = st.chat_input("Votre message…")
if saisie:
    if not cle:
        st.warning("Ajoutez la clé dans le .env de ce dossier.")
        st.stop()
    st.session_state.messages.append({"role": "user", "content": saisie})
    with st.chat_message("user"):
        st.markdown(saisie)

    historique = [{"role": "system", "content": SYSTEME}, *st.session_state.messages]
    try:
        llm = ChatOpenAI(
            model=conf["modele"],
            api_key=cle,
            base_url=conf["base"],
            temperature=temperature,
            max_completion_tokens=600,
        )

        def flux():
            for fragment in llm.stream(historique):
                yield fragment.content if isinstance(fragment.content, str) else str(fragment.content)

        with st.chat_message("assistant"):
            texte = st.write_stream(flux())
        st.session_state.messages.append({"role": "assistant", "content": texte or ""})
    except Exception as erreur:
        st.error(f"Erreur API : {erreur}")
        st.session_state.messages.pop()
