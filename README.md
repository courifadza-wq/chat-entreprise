# Chat entreprise

Parcours **Développeur IA Appliquée** — Étape 0  
Intitulé : **Technicien en Intelligence Artificielle**  
Nom pédagogique : *L'IA qui répond*

Application Streamlit type ChatGPT. Vous choisissez un fournisseur (Gemini, Cerebras ou Groq), puis un modèle. La clé reste dans un fichier `.env` local, jamais dans le code.

## Ce que fait l'application

- Dialogue en bulles, comme ChatGPT
- Historique de conversation
- Réponse en flux (le texte s'affiche au fur et à mesure)
- Trois comptes dans **un seul** `.env` : on n'utilise qu'une clé à la fois
- Message d'erreur lisible (401, 402, 403, 429) au lieu d'un écran rouge brut

## Prérequis

- Windows
- Python 3.12 ou 3.13
- Un compte GitHub
- **Au moins une** clé parmi : Gemini, Cerebras, Groq

## Installation

```powershell
git clone https://github.com/VOTRE-COMPTE/chat-entreprise.git
cd chat-entreprise
py -3.13 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
copy .env.example .env
notepad .env
```

Dans `.env`, une ligne par compte que vous avez vraiment (sans guillemets, sans espaces autour du `=`) :

```env
GEMINI_API_KEY=AIzaSy...
CEREBRAS_API_KEY=csk-...
GROQ_API_KEY=gsk_...
```

Vous n'êtes pas obligé d'avoir les trois. Une clé qui fonctionne suffit.

## Lancer

```powershell
.\venv\Scripts\Activate.ps1
streamlit run app_multi_api.py
```

1. Menu **Gemini** → modèle `gemini-3.6-flash` → « bonjour »
2. Si Gemini refuse : menu **Cerebras** → `llama-3.3-70b`
3. Secours : menu **Groq** → `llama-3.1-8b-instant`

Vérifier les clés sans les afficher :

```powershell
python tester_cles.py
```

## Technique des 3 comptes

Le `.env` est un trousseau. L'écran ne lit **qu'une** ligne, celle du menu choisi.

| Rang | Menu | Modèle sûr | Quand l'utiliser |
|---|---|---|---|
| 1 | Gemini | `gemini-3.6-flash` | Quotidien |
| 2 | Cerebras | `llama-3.3-70b` | Gemini saturé ou 404 |
| 3 | Groq | `llama-3.1-8b-instant` | Secours rapide |

Ne collez pas la clé dans le chat, ni dans un e-mail, ni dans GitHub.

## Structure du dépôt

```text
chat-entreprise/
  app_multi_api.py      interface Streamlit
  tester_cles.py        test des clés (n'affiche pas les secrets)
  tester_orca.py        optionnel
  requirements.txt
  .env.example          modèle, sans vraies clés
  .gitignore            ignore .env et venv
  README.md
```

## Règle GitHub

| Fichier | Sur GitHub ? |
|---|---|
| `app_multi_api.py` | oui |
| `.env.example` | oui |
| `README.md` | oui |
| `.env` | **non** |
| `venv/` | **non** |

## Démo de fin d'étape (5 minutes)

1. Montrer le `.env` **fermé** : « les clés ne sont pas dans le code ».
2. Lancer l'app, 3 messages de suite (la mémoire tient).
3. Changer de fournisseur, reposer la même question.
4. Couper volontairement une clé : un message clair s'affiche.

## Erreurs fréquentes

| Code | Sens | Que faire |
|---|---|---|
| 401 | Mauvaise clé | Recréer la clé, vérifier le nom de la ligne |
| 402 | Quota / modèle payant | Autre modèle ou autre menu |
| 403 | Compte non autorisé | Changer de fournisseur |
| 404 | Modèle retiré | Ex. plus `gemini-2.5-flash` → `gemini-3.6-flash` |
| 429 | Trop d'appels | Attendre ou passer à Cerebras / Groq |

## Suite du parcours

| Étape | Métier | Dossier |
|---|---|---|
| 0 (ici) | Technicien IA | `-0-Chat-API` |
| 1 | Développeur LLM Junior | `-1-LangChain` |
| 2 | Spécialiste Applications IA | `-2-LlamaIndex` |
| 3 | Intégrateur de Solutions IA | `-3-CrewAI` |

## Licence pédagogique

Usage formation / démonstration. Chaque stagiaire fork ou copie le dépôt et met **ses** clés dans son `.env` local.
