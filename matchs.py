from bson import ObjectId
from flask import Blueprint, request, jsonify

# Créer un blueprint pour les matchs
matchs_blueprint = Blueprint('matchs', __name__)

from mongo_client import Mongo2Client  # Assurez-vous que cela correspond à votre configuration


@matchs_blueprint.route('/', methods=['GET'])
def get_all_matchs():
    mongo_client = Mongo2Client(db_name='pingpong')
    matchs_cursor = mongo_client.db['matchs'].find()  # Cela retourne un curseur
    matchs_liste = list(matchs_cursor)  # Convertit le curseur en liste
    for match in matchs_liste:
        match['_id'] = str(match['_id'])  # Convertit ObjectId en str
    mongo_client.close()
    return jsonify(matchs_liste)


@matchs_blueprint.route('/', methods=['POST'])
def add_match():
    mongo_client = Mongo2Client(db_name='pingpong')
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
            mongo_client.close()
            return jsonify({"succès": True, "id_insertion": str(resultat.inserted_id)}), 201
        else:
            mongo_client.close()
            return '', 500
    else:
        mongo_client.close()
        return '', 404


@matchs_blueprint.route('/<id>', methods=['PUT'])
def update_match(id):
    mongo_client = Mongo2Client(db_name='pingpong')
    data = request.get_json()
    print(data)
    if not data:
        mongo_client.close()
        return 400
    mise_a_jour = {key: value for key, value in data.items() if
                   key in ['equipe1', 'equipe2', 'date', 'heure', 'score1', 'score2']}
    if mise_a_jour:
        resultat = mongo_client.db['matchs'].update_one({'_id': ObjectId(id)}, {'$set': mise_a_jour})
        if resultat.modified_count > 0:
            mongo_client.close()
            return '', 200
        else:
            mongo_client.close()
            return '', 404
    else:
        mongo_client.close()
        return '', 400


@matchs_blueprint.route('/<id>', methods=['DELETE'])
def supprimer_match(id):
    mongo_client = Mongo2Client(db_name='pingpong')
    try:
        resultat = mongo_client.db['matchs'].delete_one({'_id': ObjectId(id)})
        if resultat.deleted_count > 0:
            mongo_client.close()
            return '', 200
        else:
            mongo_client.close()
            return '', 404
    except Exception as e:
        mongo_client.close()
        return '', 500
