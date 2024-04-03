from bson import ObjectId
from flask import Blueprint, request, jsonify
from mongo_client import Mongo2Client  # Assurez-vous que cela correspond à votre configuration

equipement_blueprint = Blueprint('equipement', __name__)

@equipement_blueprint.route('/affiche', methods=['GET'])
def get_equipements():

    mongo_client = Mongo2Client(db_name='pingpong')
    equipement = mongo_client.db['equipements'].find_one()
    mongo_client.close()
    if equipement is None:
            return jsonify({"error": "No equipment found"}), 404
    equipement["_id"] = str(equipement["_id"])

    return jsonify(equipement)
 

@equipement_blueprint.route('/ajouter_equipement', methods=['POST'])
def ajouter_equipement():
    mongo_client = Mongo2Client(db_name='pingpong')
    data = request.get_json()

    resultat = mongo_client.db['equipements'].insert_one(data)
    if resultat.inserted_id:
        mongo_client.close()
        return jsonify({"succès": True, "id_insertion": str(resultat.inserted_id)}), 201
    else:
        mongo_client.close()
        return jsonify({"succès": False, "message": "Erreur lors de l'ajout de l'équipement"}), 500

@equipement_blueprint.route('/modifier_equipement', methods=['PUT'])
def modifier_equipement():
    mongo_client = Mongo2Client(db_name='pingpong')
    data = request.get_json()
    if not data:
        mongo_client.close()
        return jsonify({"succès": False, "message": "Aucune donnée fournie"}), 400

    # Modifier le seul équipement sans spécifier l'ID
    resultat = mongo_client.db['equipements'].update_one({}, {'$set': data})

    if resultat.modified_count > 0:
        mongo_client.close()
        return jsonify({"succès": True, "message": "L'équipement a été modifié"}), 200
    else:
        mongo_client.close()
        return jsonify({"succès": False, "message": "Aucune modification effectuée"}), 404


@equipement_blueprint.route('/supprimer_equipement/<id>', methods=['DELETE'])
def supprimer_equipement(id):
    mongo_client = Mongo2Client(db_name='pingpong')
    try:
        resultat = mongo_client.db['equipements'].delete_one({'_id': ObjectId(id)})
        if resultat.deleted_count > 0:
            mongo_client.close()
            return jsonify({"succès": True, "message": "L'équipement a été supprimé"}), 200
        else:
            mongo_client.close()
            return jsonify({"succès": False, "message": "Aucun équipement trouvé avec cet ID"}), 404
    except Exception as e:
        mongo_client.close()
        return jsonify({"succès": False, "message": "Erreur lors de la suppression", "erreur": str(e)}), 500