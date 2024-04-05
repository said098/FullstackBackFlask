from bson import ObjectId
from flask import Blueprint, request, jsonify
from mongo_client import Mongo2Client

equipement_blueprint = Blueprint('equipement', __name__)
mongo_client = Mongo2Client(db_name='pingpong')

@equipement_blueprint.route('/', methods=['GET'])
def get_equipements():
    equipement = mongo_client.db['equipements'].find_one()
    if equipement is None:
        return jsonify({'error': 'Equipement non trouvé'})
    equipement["_id"] = str(equipement["_id"])
    return jsonify(equipement)


@equipement_blueprint.route('/', methods=['POST'])
def ajouter_equipement():
    data = request.get_json()
    resultat = mongo_client.db['equipements'].insert_one(data)
    if resultat.inserted_id:
        return jsonify({"succès": True, "id_insertion": str(resultat.inserted_id)})
    else:
        return jsonify({'error': 'Erreur lors de l\'insertion'})


@equipement_blueprint.route('/', methods=['PUT'])
def modifier_equipement():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Données manquantes'})

    resultat = mongo_client.db['equipements'].update_one({}, {'$set': data})
    if resultat.modified_count > 0:
        return 200
    else:
        return jsonify({'error': 'Equipement non trouvé'})


@equipement_blueprint.route('/<string:id>', methods=['DELETE'])
def supprimer_equipement(id):
    try:
        resultat = mongo_client.db['equipements'].delete_one({'_id': ObjectId(id)})
        if resultat.deleted_count > 0:
            return 200
        else:
            return jsonify({'error': 'Equipement non trouvé'})
    except Exception as e:
        return jsonify({'error': 'Erreur lors de la suppression'})
