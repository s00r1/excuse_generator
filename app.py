# -*- coding: utf-8 -*-
import os
import sys
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()

def get_api_key():
    return os.environ.get("GORQ_API_KEY")

GORQ_API_KEY = get_api_key()
print("========= DEBUG INIT =========", file=sys.stderr)
print("GORQ_API_KEY récupérée ? {}".format("OUI" if GORQ_API_KEY else "NON"), file=sys.stderr)
print("GORQ_API_KEY VALUE : {}".format(GORQ_API_KEY), file=sys.stderr)
print("==============================", file=sys.stderr)
if not GORQ_API_KEY:
    raise EnvironmentError(
        "La clé d'API n'est pas définie. Merci de définir la variable d'environnement GORQ_API_KEY"
    )

def build_prompt(data):
    prompt = (
        u"Tu es un assistant expert en excuses personnalisées, adapté à tout contexte. "
        u"Format : {}. "
        u"Intonations sélectionnées : {}. "
        u"Affinement intonations : {}. "
        u"Sujet principal : {}. "
        u"Sous-sujet : {}. "
        u"Sous-sous-sujet : {}. "
        u"Contexte global : {}. "
        u"Personnes impliquées : {}. "
        u"Relation(s) : {}. "
        u"Destinataire : {} (statut : {}). "
        u"Autres options : {}. "
        u"Répondre à ce message si précisé : {}. "
        u"Adapte la longueur et le style à chaque choix, soit créatif, crédible, et drôle si possible."
    ).format(
        data['format'],
        ', '.join(data['intonations']),
        ', '.join(data['intonation_affinage']) if data['intonation_affinage'] else 'aucun',
        data['sujet'],
        data['sous_sujet'],
        data['sous_sous_sujet'],
        data['contexte'],
        ', '.join(data['personnes']) if data['personnes'] else 'aucune',
        ', '.join(data['relations']) if data['relations'] else 'aucune',
        data['destinataire'],
        data['statut_destinataire'],
        ', '.join(data['options']) if data['options'] else 'aucune',
        data['message_recu']
    )
    return prompt

def generate_excuse(data):
    prompt = build_prompt(data)
    url = "https://api.gorq.cloud/v1/chat/completions"
    headers = {
        "Authorization": "Bearer {}".format(GORQ_API_KEY),
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mixtral-8x7b",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 1.0,
        "max_tokens": 500
    }

    # LOG DEBILE
    print("========= DEBUG RACAILLE =========", file=sys.stderr)
    print("API_KEY présent : {}".format("OUI" if GORQ_API_KEY else "NON"), file=sys.stderr)
    print("Payload envoyé : {}".format(payload), file=sys.stderr)
    print("Headers envoyés : {}".format(headers), file=sys.stderr)
    print("==================================", file=sys.stderr)

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
    except requests.RequestException as e:
        print("Erreur de connexion à l'API : {}".format(str(e)), file=sys.stderr)
        return u"Erreur de connexion à l'API"
    print("Status code : {}".format(resp.status_code), file=sys.stderr)
    print("Réponse texte : {}".format(resp.text), file=sys.stderr)
    if resp.status_code == 200:
        try:
            output = resp.json()["choices"][0]["message"]["content"]
            print("Réponse finale API : {}".format(output), file=sys.stderr)
            return output
        except Exception as e:
            print("Erreur de parsing JSON : {}".format(str(e)), file=sys.stderr)
            return u"L'IA a buggé, zebi. Réessaie."
    else:
        return u"Erreur Gorq ({}) : {}".format(resp.status_code, resp.text)

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    print("DATA RECUE dans /generate : {}".format(data), file=sys.stderr)
    if not isinstance(data, dict):
        return jsonify({"error": u"Données manquantes"}), 400

    required_fields = [
        "format", "intonations", "intonation_affinage", "sujet",
        "sous_sujet", "sous_sous_sujet", "contexte", "personnes",
        "relations", "destinataire", "statut_destinataire", "options",
        "message_recu",
    ]
    missing = [f for f in required_fields if f not in data]
    if missing:
        return (
            jsonify({"error": u"Champs manquants : {}".format(', '.join(missing))}),
            400,
        )

    excuse = generate_excuse(data)
    return jsonify({"excuse": excuse})

if __name__ == "__main__":
    app.run()

