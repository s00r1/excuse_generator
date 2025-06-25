# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from groq import Groq

app = Flask(__name__)
load_dotenv()  # Charge le .env à la racaille

def get_api_key():
    return os.environ.get("GROQ_API_KEY")  # Mets GROQ_API_KEY dans ton .env, pas GORQ, cousin

GROQ_API_KEY = get_api_key()
if not GROQ_API_KEY:
    raise EnvironmentError("La clé d'API n'est pas définie. Mets GROQ_API_KEY dans .env zebi.")

client = Groq(api_key=GROQ_API_KEY)

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
    prompt = build_prompt(data)
    try:
        completion = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",  # change le model si tu veux
            messages=[{
                "role": "user",
                "content": prompt
            }],
            temperature=1,
            max_completion_tokens=500,
            top_p=1,
            stream=False  # On prend la réponse complète d'un coup (stream=True ça marche que si tu veux du streaming)
        )
        # Version sans stream :
        return completion.choices[0].message.content
    except Exception as e:
        return f"Erreur API Groq: {e}"

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
        return jsonify({"error": "Champs manquants : {}".format(', '.join(missing))}), 400

    excuse = generate_excuse(data)
    return jsonify({"excuse": excuse})

if __name__ == "__main__":
    app.run()


