# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template, request, jsonify

# PAS besoin de dotenv là, on veut du brutal zebi

app = Flask(__name__)

# Mets la clé EN DUR (oui c’est sale, mais c’est pour debug la mif)
GROQ_API_KEY = "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"
if not GROQ_API_KEY:
    raise EnvironmentError("La clé d'API GROQ n'est pas définie. Mets-la en dur ou va fumer un chicha.")

MODEL_ID = "meta-llama/llama-4-scout-17b-16e-instruct"

def build_prompt(data):
    prompt = (
        "Tu es un assistant expert en excuses personnalisées, adapté à tout contexte. "
        "Format : {}. "
        "Intonations sélectionnées : {}. "
        "Affinement intonations : {}. "
        "Sujet principal : {}. "
        "Sous-sujet : {}. "
        "Sous-sous-sujet : {}. "
        "Contexte global : {}. "
        "Personnes impliquées : {}. "
        "Relation(s) : {}. "
        "Destinataire : {} (statut : {}). "
        "Autres options : {}. "
        "Répondre à ce message si précisé : {}. "
        "Adapte la longueur et le style à chaque choix, soit créatif, crédible, et drôle si possible."
    ).format(
        data.get('format', ''),
        ', '.join(data.get('intonations', [])),
        ', '.join(data.get('intonation_affinage', [])) if data.get('intonation_affinage') else 'aucun',
        data.get('sujet', ''),
        data.get('sous_sujet', ''),
        data.get('sous_sous_sujet', ''),
        data.get('contexte', ''),
        ', '.join(data.get('personnes', [])) if data.get('personnes') else 'aucune',
        ', '.join(data.get('relations', [])) if data.get('relations') else 'aucune',
        data.get('destinataire', ''),
        data.get('statut_destinataire', ''),
        ', '.join(data.get('options', [])) if data.get('options') else 'aucune',
        data.get('message_recu', '')
    )
    return prompt

def generate_excuse(data):
    import requests
    prompt = build_prompt(data)
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL_ID,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 1,
        "max_tokens": 500
    }
    print("DEBUG ENVOI :", headers, payload)  # Optionnel pour debug
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return "Erreur Groq : {}".format(e)

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
            jsonify({"error": "Champs manquants : {}".format(', '.join(missing))}),
            400,
        )

    excuse = generate_excuse(data)
    return jsonify({"excuse": excuse})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
