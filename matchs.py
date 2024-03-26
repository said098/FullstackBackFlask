from bson import ObjectId
from flask import Blueprint, request, jsonify

# Créer un blueprint pour les matchs
matchs_blueprint = Blueprint('matchs', __name__)

from mongo_client import Mongo2Client  # Assurez-vous que cela correspond à votre configuration

@matchs_blueprint.route('/liste_matchs', methods=['GET'])
def get_all_matchs():
    mongo_client = Mongo2Client(db_name='pingpong')
    matchs_cursor = mongo_client.db['matchs'].find()  # Cela retourne un curseur
    matchs_liste = list(matchs_cursor)  # Convertit le curseur en liste
    for match in matchs_liste:
        match['_id'] = str(match['_id'])  # Convertit ObjectId en str
    mongo_client.close()
    return jsonify(matchs_liste)

@matchs_blueprint.route('/add_match', methods=['POST'])
def add_match():
    mongo_client = Mongo2Client(db_name='pingpong')
    data = request.get_json()
    print(data)

    resultat = mongo_client.db['matchs'].insert_one(data)
    if resultat.inserted_id:
        mongo_client.close()
        return jsonify({"succès": True, "id_insertion": str(resultat.inserted_id)}), 201
    else:
        mongo_client.close()
        return jsonify({"succès": False, "message": "Erreur lors de l'insertion"}), 500

@matchs_blueprint.route('/update_match/<id>', methods=['PUT'])
def update_match(id):
    mongo_client = Mongo2Client(db_name='pingpong')
    data = request.get_json()
    print(data)
    if not data:
        mongo_client.close()
        return jsonify({"succès": False, "message": "Aucune donnée fournie"}), 400

    mise_a_jour = {key: value for key, value in data.items() if key in ['equipes', 'table', 'date', 'heure', 'resultat']}
    if mise_a_jour:
        resultat = mongo_client.db['matchs'].update_one({'_id': ObjectId(id)}, {'$set': mise_a_jour})
        if resultat.modified_count > 0:
            mongo_client.close()
            return jsonify({"succès": True, "message": "Le match a été mis à jour"}), 200
        else:
            mongo_client.close()
            return jsonify({"succès": False, "message": "Aucune mise à jour effectuée"}), 404
    else:
        mongo_client.close()
        return jsonify({"succès": False, "message": "Aucune donnée valide pour la mise à jour"}), 400

@matchs_blueprint.route('/supprimer_match/<id>', methods=['DELETE'])
def supprimer_match(id):
    mongo_client = Mongo2Client(db_name='pingpong')
    try:
        resultat = mongo_client.db['matchs'].delete_one({'_id': ObjectId(id)})
        if resultat.deleted_count > 0:
            mongo_client.close()
            return jsonify({"succès": True, "message": "Le match a été supprimé"}), 200
        else:
            mongo_client.close()
            return jsonify({"succès": False, "message": "Aucun match trouvé avec cet ID"}), 404
    except Exception as e:
        mongo_client.close()
        return jsonify({"succès": False, "message": "Erreur lors de la suppression", "erreur": str(e)}), 500