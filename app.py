import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

GORQ_API_KEY = os.environ.get("GORQ_API_KEY")
if not GORQ_API_KEY:
    raise EnvironmentError(
        "La clé d'API n'est pas définie. Merci de définir la variable d'environnement GORQ_API_KEY"
    )

def build_prompt(data):
    prompt = (
        f"Tu es un assistant expert en excuses personnalisées, adapté à tout contexte. "
        f"Format : {data['format']}. "
        f"Intonations sélectionnées : {', '.join(data['intonations'])}. "
        f"Affinement intonations : {', '.join(data['intonation_affinage']) if data['intonation_affinage'] else 'aucun'}. "
        f"Sujet principal : {data['sujet']}. "
        f"Sous-sujet : {data['sous_sujet']}. "
        f"Sous-sous-sujet : {data['sous_sous_sujet']}. "
        f"Contexte global : {data['contexte']}. "
        f"Personnes impliquées : {', '.join(data['personnes']) if data['personnes'] else 'aucune'}. "
        f"Relation(s) : {', '.join(data['relations']) if data['relations'] else 'aucune'}. "
        f"Destinataire : {data['destinataire']} (statut : {data['statut_destinataire']}). "
        f"Autres options : {', '.join(data['options']) if data['options'] else 'aucune'}. "
        f"Répondre à ce message si précisé : {data['message_recu']}. "
        f"Adapte la longueur et le style à chaque choix, soit créatif, crédible, et drôle si possible."
    )
    return prompt

def generate_excuse(data):
    prompt = build_prompt(data)
    url = "https://api.gorq.cloud/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GORQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mixtral-8x7b",  # tu peux changer par 'gpt-3.5-turbo', 'zephyr-7b-beta', etc
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 1.0,
        "max_tokens": 500
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    if resp.status_code == 200:
        try:
            output = resp.json()["choices"][0]["message"]["content"]
            return output
        except Exception:
            return "L'IA a buggé, zebi. Réessaie."
    else:
        return f"Erreur Gorq ({resp.status_code}) : {resp.text}"

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({"error": "Données manquantes"}), 400

    required_fields = [
        "format", "intonations", "intonation_affinage", "sujet",
        "sous_sujet", "sous_sous_sujet", "contexte", "personnes",
        "relations", "destinataire", "statut_destinataire", "options",
        "message_recu",
    ]
    missing = [f for f in required_fields if f not in data]
    if missing:
        return (
            jsonify({"error": f"Champs manquants : {', '.join(missing)}"}),
            400,
        )

    excuse = generate_excuse(data)
    return jsonify({"excuse": excuse})

if __name__ == "__main__":
    app.run()
