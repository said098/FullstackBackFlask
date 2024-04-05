from flask import Blueprint, request, jsonify
from bson import ObjectId
from mongo_client import Mongo2Client

equipes_blueprint = Blueprint('equipes', __name__)
mongo_client = Mongo2Client(db_name='pingpong')

def serialize_doc(doc):
    if isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    elif isinstance(doc, dict):
        return {k: serialize_doc(v) for k, v in doc.items()}
    elif isinstance(doc, ObjectId):
        return str(doc)
    return doc

@equipes_blueprint.route('/', methods=['GET'])
def get_all_equipes():
    equipes_cursor = mongo_client.db['equipe'].find()
    equipes_liste = list(equipes_cursor)

    for equipe in equipes_liste:
        equipe['joueurs'] = [
            serialize_doc(mongo_client.db['joueur'].find_one({'_id': joueur['_id']}))
            for joueur in equipe['joueurs']
        ]
    equipes_liste = serialize_doc(equipes_liste)
    return jsonify(equipes_liste)

@equipes_blueprint.route('/', methods=['POST'])
def add_equipe():
    data = request.get_json()

    for i, joueur in enumerate(data['joueurs']):
        joueur_id = list(joueur.values())[0]
        try:
            document_joueur = mongo_client.db['joueur'].find_one({'_id': ObjectId(joueur_id)})
            if document_joueur:
                data['joueurs'][i] = document_joueur
            else:
                return jsonify({"succès": False, "message": f"Joueur avec l'ID {joueur_id} non trouvé"})
        except:
            return jsonify({'error': 'Mauvaise requête'})

    resultat = mongo_client.db['equipe'].insert_one(data)
    if resultat.inserted_id:
        return jsonify({"succès": True, "id_insertion": str(resultat.inserted_id)})
    else:
        return jsonify({'error': 'Erreur lors de l\'insertion'})

@equipes_blueprint.route('/<string:id>', methods=['PUT'])
def update_equipe(id):
    data = request.get_json()
    mise_a_jour = {}
    for champ in ['joueurs', 'type']:
        if champ in data:
            mise_a_jour[champ] = data[champ]
    resultat = mongo_client.db['equipe'].update_one({'_id': ObjectId(id)}, {'$set': mise_a_jour})
    if resultat.modified_count > 0:
        return 200
    else:
        return jsonify({'error': 'Equipe non trouvée'})

@equipes_blueprint.route('/<string:id>', methods=['DELETE'])
def delete_equipe(id):
    resultat = mongo_client.db['equipe'].delete_one({'_id': ObjectId(id)})
    if resultat.deleted_count > 0:
        return 200
    else:
        return jsonify({'error': 'Equipe non trouvée'})
