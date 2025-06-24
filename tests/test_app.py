from app import build_prompt
import requests

sample_data = {
    'format': 'sms',
    'intonations': ['excuse', 'gentil'],
    'intonation_affinage': ['sarcastique'],
    'sujet': 'retard',
    'sous_sujet': 'embouteillage',
    'sous_sous_sujet': 'accident',
    'contexte': 'route bloquee',
    'personnes': ['collegue'],
    'relations': ['professionnelle'],
    'destinataire': 'Paul',
    'statut_destinataire': 'chef',
    'options': ['emoji'],
    'message_recu': 'Pourquoi es-tu en retard ?'
}


def test_build_prompt():
    expected = (
        "Tu es un assistant expert en excuses personnalisées, adapté à tout contexte. "
        "Format : sms. "
        "Intonations sélectionnées : excuse, gentil. "
        "Affinement intonations : sarcastique. "
        "Sujet principal : retard. "
        "Sous-sujet : embouteillage. "
        "Sous-sous-sujet : accident. "
        "Contexte global : route bloquee. "
        "Personnes impliquées : collegue. "
        "Relation(s) : professionnelle. "
        "Destinataire : Paul (statut : chef). "
        "Autres options : emoji. "
        "Répondre à ce message si précisé : Pourquoi es-tu en retard ?. "
        "Adapte la longueur et le style à chaque choix, soit créatif, crédible, et drôle si possible."
    )
    assert build_prompt(sample_data) == expected


def test_generate_route(client, monkeypatch):
    class DummyResp:
        status_code = 200
        def json(self):
            return {"choices": [{"message": {"content": "excuse générée"}}]}
    def fake_post(*args, **kwargs):
        return DummyResp()

    monkeypatch.setattr('app.requests.post', fake_post)
    resp = client.post('/generate', json=sample_data)
    assert resp.status_code == 200
    assert resp.get_json() == {'excuse': 'excuse générée'}


def test_generate_route_network_error(client, monkeypatch):
    def fake_post(*args, **kwargs):
        raise requests.RequestException

    monkeypatch.setattr('app.requests.post', fake_post)
    resp = client.post('/generate', json=sample_data)
    assert resp.status_code == 200
    assert resp.get_json() == {'excuse': "Erreur de connexion à l'API"}
