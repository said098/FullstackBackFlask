from bson import ObjectId
from flask import Blueprint, request, jsonify
from mongo_client import Mongo2Client

matchs_blueprint = Blueprint('matchs', __name__)
mongo_client = Mongo2Client(db_name='pingpong')

@matchs_blueprint.route('/', methods=['GET'])
def get_all_matchs():
    matchs_cursor = mongo_client.db['matchs'].find()
    matchs_liste = list(matchs_cursor)  
    for match in matchs_liste:
        match['_id'] = str(match['_id'])  
    return jsonify(matchs_liste)

@matchs_blueprint.route('/', methods=['POST'])
def add_match():
    data = request.get_json()
    equipe1_id = data.get('equipe1')
    equipe2_id = data.get('equipe2')

    equipe1 = mongo_client.db['equipe'].find_one({'_id': ObjectId(equipe1_id)})
    equipe2 = mongo_client.db['equipe'].find_one({'_id': ObjectId(equipe2_id)})

    if equipe1 and equipe2:
        data['equipe1'] = equipe1.get('nom')
        data['equipe2'] = equipe2.get('nom')

        resultat = mongo_client.db['matchs'].insert_one(data)
        if resultat.inserted_id:
            return jsonify({"succès": True, "id_insertion": str(resultat.inserted_id)})
        else:
            return jsonify({'error': 'Erreur lors de l\'insertion'})
    else:
        return 404

@matchs_blueprint.route('/<string:id>', methods=['PUT'])
def update_match(id):
    data = request.get_json()
    if not data:
        return 400
    mise_a_jour = {key: value for key, value in data.items() if
                   key in ['equipe1', 'equipe2', 'date', 'heure', 'score1', 'score2']}
    if mise_a_jour:
        resultat = mongo_client.db['matchs'].update_one({'_id': ObjectId(id)}, {'$set': mise_a_jour})
        if resultat.modified_count > 0:
            return 200
        else:
            return 404
    else:
        return 400

@matchs_blueprint.route('/<string:id>', methods=['DELETE'])
def supprimer_match(id):
    try:
        resultat = mongo_client.db['matchs'].delete_one({'_id': ObjectId(id)})
        if resultat.deleted_count > 0:
            return 200
        else:
            return 404
    except Exception as e:
        return 500
