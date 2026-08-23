"""Étape 0 — Une interface, plusieurs API, les LLM de chacune."""

from __future__ import annotations

import json
import os
from typing import Iterator

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

SYSTEME = (
    "Tu es un assistant professionnel. Réponds en français, clairement. "
    "Si tu ne sais pas, dis-le."
)

def nettoyer(valeur: str) -> str:
    """Enlève les crochets Markdown souvent collés depuis le chat."""
    t = (valeur or "").strip()
    t = t.replace("[", "").replace("]", "")
    if t.startswith("http") and ")http" in t:
        t = t.split(")", 1)[0]
    if "(" in t and t.endswith(")"):
        t = t.split("(", 1)[0]
    return t.strip().rstrip("/")


FOURNISSEURS = {
    "OrcaRouter": {
        "base_url": "https://api.orcarouter.ai/v1",
        "env": "ORCAROUTER_API_KEY",
        "extra_headers": {},
    },
    "Gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "env": "GEMINI_API_KEY",
        "extra_headers": {},
    },
    "Cerebras": {
        "base_url": "https://api.cerebras.ai/v1",
        "env": "CEREBRAS_API_KEY",
        "extra_headers": {},
    },
    "NVIDIA": {
        "base_url": "https://integrate.api.nvidia.com/v1",
        "env": "NVIDIA_API_KEY",
        "extra_headers": {},
    },
    "OpenRouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "env": "OPENROUTER_API_KEY",
        "extra_headers": {
            "HTTP-Referer": "http://localhost:8501",
            "X-Title": "Chat entreprise",
        },
    },
    "Hugging Face": {
        "base_url": "https://router.huggingface.co/v1",
        "env": "HF_TOKEN",
        "extra_headers": {},
    },
    "Groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "env": "GROQ_API_KEY",
        "extra_headers": {},
    },
    "Mistral": {
        "base_url": "https://api.mistral.ai/v1",
        "env": "MISTRAL_API_KEY",
        "extra_headers": {},
    },
}

SECOURS = {
    "OrcaRouter": [
        "orcarouter/auto",
        "orcarouter/free",
        "deepseek/deepseek-v4-flash-free",
        "openai/gpt-4o-mini",
    ],
    "Gemini": [
        "gemini-3.6-flash",
        "gemini-3.7-flash",
        "gemini-2.0-flash",
    ],
    "Cerebras": [
        "llama-3.3-70b",
        "llama3.1-8b",
        "gpt-oss-120b",
        "qwen-3-32b",
    ],
    "NVIDIA": [
        "meta/llama-3.1-8b-instruct",
        "meta/llama-3.1-70b-instruct",
        "mistralai/mistral-nemotron",
        "google/gemma-2-9b-it",
    ],
    "OpenRouter": [
        "openai/gpt-4o-mini",
        "anthropic/claude-3.5-sonnet",
        "meta-llama/llama-3.1-8b-instruct",
        "google/gemini-flash-1.5",
    ],
    "Hugging Face": [
        "openai/gpt-oss-20b",
        "Qwen/Qwen2.5-7B-Instruct",
        "meta-llama/Meta-Llama-3.1-8B-Instruct",
    ],
    "Groq": [
        "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile",
        "mixtral-8x7b-32768",
    ],
    "Mistral": [
        "mistral-small-latest",
        "mistral-medium-latest",
        "open-mistral-nemo",
    ],
}


def cle_fournisseur(nom: str, personnalise_cle: str = "") -> str:
    if nom == "Personnalisée":
        return nettoyer(personnalise_cle or os.getenv("CUSTOM_API_KEY") or "")
    return nettoyer(os.getenv(FOURNISSEURS[nom]["env"]) or "")


def base_fournisseur(nom: str, personnalise_url: str = "") -> str:
    if nom == "Personnalisée":
        return nettoyer(personnalise_url or os.getenv("CUSTOM_API_BASE") or "")
    return FOURNISSEURS[nom]["base_url"]


def en_tetes(nom: str, cle: str) -> dict:
    headers = {
        "Authorization": f"Bearer {cle}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if nom in FOURNISSEURS:
        headers.update(FOURNISSEURS[nom].get("extra_headers") or {})
    return headers


def est_modele_chat(identifiant: str) -> bool:
    t = identifiant.lower()
    interdits = (
        "embed", "rerank", "reranker", "whisper", "tts", "image",
        "vision-only", "antigravity", "imagen", "veo", "lyria",
    )
    return not any(mot in t for mot in interdits)


def ranger_modeles(nom: str, ids: list[str]) -> list[str]:
    preferes = SECOURS.get(nom, [])
    tete = [m for m in preferes if m in ids]
    reste = [m for m in ids if m not in tete]
    return tete + reste


@st.cache_data(ttl=600, show_spinner=False)
def charger_modeles(nom: str, base_url: str, cle: str) -> tuple[list[str], str | None]:
    if not base_url or not cle:
        return SECOURS.get(nom, []), "Clé ou URL absente — liste de secours."
    try:
        reponse = requests.get(
            f"{base_url}/models",
            headers=en_tetes(nom, cle),
            timeout=20,
        )
        reponse.raise_for_status()
        donnees = reponse.json().get("data", [])
        ids = sorted({item.get("id") for item in donnees if item.get("id") and est_modele_chat(item["id"])})
        if not ids:
            raise RuntimeError("Catalogue vide")
        return ranger_modeles(nom, ids), None
    except Exception as erreur:
        return SECOURS.get(nom, []), str(erreur)


def flux_reponse(
    nom: str,
    base_url: str,
    cle: str,
    modele: str,
    messages: list[dict],
    temperature: float,
    max_tokens: int,
    delai: int,
) -> Iterator[str]:
    reponse = requests.post(
        f"{base_url}/chat/completions",
        headers=en_tetes(nom, cle),
        json={
            "model": modele,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        },
        stream=True,
        timeout=delai,
    )
    if reponse.status_code >= 400:
        raise RuntimeError(f"HTTP {reponse.status_code} : {reponse.text[:500]}")

    for brut in reponse.iter_lines(decode_unicode=True):
        if not brut:
            continue
        ligne = brut.strip()
        if ligne.startswith("data:"):
            ligne = ligne[5:].strip()
        if ligne == "[DONE]":
            break
        try:
            paquet = json.loads(ligne)
        except json.JSONDecodeError:
            continue
        choix = paquet.get("choices") or []
        if not choix:
            continue
        delta = choix[0].get("delta") or {}
        texte = delta.get("content")
        if texte:
            yield texte


st.set_page_config(page_title="Chat multi-API", layout="centered")
st.title("Chat multi-API")
st.caption("Choisissez d'abord le fournisseur, puis un de ses LLM. Même geste que ChatGPT.")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "fournisseur_actif" not in st.session_state:
    st.session_state.fournisseur_actif = "NVIDIA"

noms = [*FOURNISSEURS.keys(), "Personnalisée"]

with st.sidebar:
    st.header("Fournisseur")
    fournisseur = st.selectbox("API", noms, index=noms.index(st.session_state.fournisseur_actif))

    url_perso = ""
    cle_perso = ""
    if fournisseur == "Personnalisée":
        st.info("Pour MonkeyCode ou tout service compatible OpenAI : collez l'URL …/v1 et la clé.")
        url_perso = st.text_input("URL de base", os.getenv("CUSTOM_API_BASE", "https://exemple.com/v1"))
        cle_perso = st.text_input("Clé API", type="password")

    if fournisseur != st.session_state.fournisseur_actif:
        st.session_state.fournisseur_actif = fournisseur
        st.session_state.messages = []
        charger_modeles.clear()
        st.rerun()

    cle = cle_fournisseur(fournisseur, cle_perso)
    base = base_fournisseur(fournisseur, url_perso)

    st.subheader("Clés détectées")
    for nom, conf in FOURNISSEURS.items():
        ok = bool(os.getenv(conf["env"]))
        st.write(f"{'●' if ok else '○'} {nom}")
    st.caption("Ajoutez les clés manquantes dans le fichier .env du dossier -0-Chat-API.")

    if not cle:
        st.error(f"Pas de clé pour {fournisseur}.")
    else:
        modeles, erreur_cat = charger_modeles(fournisseur, base, cle)
        if erreur_cat:
            st.warning(f"Catalogue incomplet : {erreur_cat}")

        filtre = st.text_input("Filtrer les modèles", "")
        visibles = [m for m in modeles if filtre.lower() in m.lower()]
        if not visibles:
            visibles = modeles[:1] or ["(aucun)"]
        modele = st.selectbox(f"LLM ({len(modeles)} disponibles)", visibles)
        st.caption(f"{len(modeles)} modèles chargés depuis {base}")
        if fournisseur == "Gemini":
            st.info("Modèle à utiliser : gemini-3.6-flash (pas 2.5).")
        if fournisseur == "NVIDIA":
            st.warning(
                "Si tu as un 403 au chat alors que le catalogue répond : "
                "le compte n'a pas le droit « Public API Endpoints ». "
                "Passe sur Gemini, Cerebras ou Groq."
            )

        temperature = st.slider("Température", 0.0, 1.0, 0.2, 0.1)
        max_tokens = st.slider("Tokens maximum", 100, 4000, 800, 50)
        delai = st.slider("Délai (secondes)", 30, 180, 90, 15)

        if st.button("Actualiser le catalogue", use_container_width=True):
            charger_modeles.clear()
            st.rerun()

    if st.button("Nouvelle conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

saisie = st.chat_input("Écrivez votre message…")

if saisie:
    if not cle:
        st.warning("Configurez d'abord la clé de cette API.")
        st.stop()
    if not modele or modele.startswith("("):
        st.warning("Aucun modèle disponible.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": saisie})
    with st.chat_message("user"):
        st.markdown(saisie)

    messages_api = [{"role": "system", "content": SYSTEME}, *st.session_state.messages]

    try:
        with st.chat_message("assistant"):
            texte = st.write_stream(
                flux_reponse(
                    fournisseur, base, cle, modele,
                    messages_api, temperature, max_tokens, delai,
                )
            )
        st.session_state.messages.append({"role": "assistant", "content": texte or ""})
    except Exception as erreur:
        st.error("L'API n'a pas répondu.")
        st.code(str(erreur))
        if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
            st.session_state.messages.pop()
