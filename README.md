# Développeur LLM Junior

Parcours **Développeur IA Appliquée** — Étape 1  
Dossier : `01-Developpeur-LLM-Junior`  
Techno : LangChain

## Solution livrée

Assistant métier : mémoire de conversation + lecture PDF + page Streamlit.

## Fichiers de cette formation uniquement

| Fichier | Rôle |
|---|---|
| `premier_appel_nvidia.py` | Premier appel API |
| `chat_avec_memoire.py` | Conversation qui se souvient |
| `lecture_pdf.py` | Lire un PDF |
| `app_streamlit.py` | Interface |

## Lancer

```powershell
cd CHEMIN\Formation\01-Developpeur-LLM-Junior
py -3.13 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
copy .env.example .env
notepad .env
python premier_appel_nvidia.py
streamlit run app_streamlit.py
```

Ne mets ici **aucun** fichier de CrewAI, LlamaIndex ou Chat-API.
