import requests
import json

LLM_URL = "http://127.0.0.1:9999/completion"

TEMPLATE = """
Tu es un assistant d'analyse tactique militaire. Tu reçois des messages radio courts, parfois bruyants ou imprécis.

Ta mission :
- EXTRAIRE les informations tactiques utiles
- RECONSTRUIRE la phrase si elle est incomplète
- GARDER un style concis, militaire
- NE JAMAIS inventer d'informations non présentes dans le message
- Résoudre les abréviations (ex : "N", "S", "NE", "CTC", etc.)

Identifie :
- unit : nom d’unité (ex : "Alpha 2", "Bravo 1", "GIGN", "patrouille Sierra 3") ou null
- alert : true si mots comme “contact”, “tir”, “otage”, “blessé”, “danger”, “urgence”, “ennemi”, “grenade”, “explosion”
- intent : action verbale (ex : “avance”, “repli”, “engage”, “couvre”, “demande renfort”, “arrive”, “tient position”)
- direction : nord / sud / est / ouest / NE / NW / SE / SW ou null
- coordinates : si coordonnées GPS détectées (formats acceptés : "48.7092, 2.4029", "N48°15.32 E2°19.33", "WP12", "point rouge", etc.)
- keywords : liste des mots tactiques importants
- urgency : score entre 0 et 5 (0 = calme, 5 = situation critique)
- summary : résumé de la situation en UNE phrase claire

Répond STRICTEMENT en JSON valide.
Message à analyser :
"{msg}"
"""


def analyze_text(msg: str) -> dict:
    prompt = TEMPLATE.format(msg=msg)

    try:
        response = requests.post(
            LLM_URL,
            json={
                "prompt": prompt,
                "n_predict": 200,
                "temperature": 0.2
            },
            timeout=8
        )

       
        raw = response.json().get("content", "").strip()

        return json.loads(raw)

    except Exception as e:
        print("[LLM ERROR]", e)
        return {
            "unit": None,
            "alert": False,
            "intent": None,
            "direction": None,
            "coordinates": None,
            "keywords": [],
            "urgency": 0,
            "summary": ""
        }
