from bson import ObjectId
from flask import Blueprint, request, jsonify, Flask
from flask_cors import CORS

from mongo_client import Mongo2Client

tournois_blueprint = Blueprint('tournois', __name__)




@tournois_blueprint.route('/add_tournoi', methods=['POST'])
def add_tournoi():
    mongo_client = Mongo2Client(db_name='pingpong')
    data = request.get_json()

    if not all(key in data for key in ['format', 'niveau', 'date', 'duree', 'lieu']):
        mongo_client.close()
        return jsonify({"succès": False, "message": "Données manquantes ou incorrectes"}), 400

    try:
        resultat = mongo_client.db['tournoi'].insert_one(data)
        mongo_client.close()
        return jsonify({"succès": True, "id_insertion": str(resultat.inserted_id)}), 201
    except Exception as e:
        mongo_client.close()
        return jsonify({"succès": False, "message": "Erreur lors de l'insertion", "erreur": str(e)}), 500


@tournois_blueprint.route('/liste_tournois', methods=['GET'])

def get_tournois():
    mongo_client = Mongo2Client(db_name='pingpong')
    try:
        tournois_cursor = mongo_client.db['tournoi'].find()
        tournois_liste = list(tournois_cursor)
        for tournoi in tournois_liste:
            tournoi['_id'] = str(tournoi['_id'])
        mongo_client.close()
        return jsonify(tournois_liste)
    except Exception as e:
        mongo_client.close()
        return jsonify({"succès": False, "message": "Erreur lors de la récupération des tournois", "erreur": str(e)}), 500






@tournois_blueprint.route('/update_tournoi/<id>', methods=['PUT'])
def update_tournoi(id):
    mongo_client = Mongo2Client(db_name='pingpong')
    data = request.get_json()
    if not data:
        mongo_client.close()
        return jsonify({"succès": False, "message": "Aucune donnée fournie"}), 400

    mise_a_jour = {}
    for champ in ['format', 'niveau', 'date', 'duree', 'lieu', 'match', 'equipement_tournois']:
        if champ in data:
            mise_a_jour[champ] = data[champ]

    if mise_a_jour:
        try:
            oid = ObjectId(id)
            resultat = mongo_client.db['tournoi'].update_one({'_id': oid}, {'$set': mise_a_jour})
            if resultat.modified_count > 0:
                mongo_client.close()
                return jsonify({"succès": True, "message": "Le tournoi a été mis à jour"}), 200
            else:
                mongo_client.close()
                return jsonify({"succès": False, "message": "Aucune mise à jour effectuée"}), 404
        except Exception as e:
            mongo_client.close()
            return jsonify({"succès": False, "message": "Erreur lors de la mise à jour", "erreur": str(e)}), 500
    else:
        mongo_client.close()
        return jsonify({"succès": False, "message": "Aucune donnée valide pour la mise à jour"}), 400




@tournois_blueprint.route('/delete_tournoi/<id>', methods=['DELETE'])
def delete_tournoi(id):
    mongo_client = Mongo2Client(db_name='pingpong')
    try:
        oid = ObjectId(id)
        resultat = mongo_client.db['tournoi'].delete_one({'_id': oid})
        if resultat.deleted_count > 0:
            mongo_client.close()
            return jsonify({"succès": True, "message": "Le tournoi a été supprimé"}), 200
        else:
            mongo_client.close()
            return jsonify({"succès": False, "message": "Aucun tournoi trouvé avec cet ID"}), 404
    except Exception as e:
        mongo_client.close()
        return jsonify({"succès": False, "message": "Erreur lors de la suppression", "erreur": str(e)}), 500





















