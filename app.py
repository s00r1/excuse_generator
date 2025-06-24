import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

GORQ_API_KEY = "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"

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
    excuse = generate_excuse(data)
    return jsonify({"excuse": excuse})

if __name__ == "__main__":
    app.run()
