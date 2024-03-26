from flask import Blueprint, request, jsonify
from bson import ObjectId
from mongo_client import Mongo2Client


equipes_blueprint = Blueprint('equipes', __name__)


@equipes_blueprint.route('/liste_equipes', methods=['GET'])
def get_all():
    mongo_client = Mongo2Client(db_name='pingpong')
    equipes_cursor = mongo_client.db['equipe'].find()
    equipes_liste = list(equipes_cursor)
    for equipe in equipes_liste:
        equipe['_id'] = str(equipe['_id'])
    mongo_client.close()
    return jsonify(equipes_liste)

# Ajouter une nouvelle équipe
@equipes_blueprint.route('/add_equipe', methods=['POST'])
def add_equipe():
    mongo_client = Mongo2Client(db_name='pingpong')
    data = request.get_json()
    resultat = mongo_client.db['equipe'].insert_one(data)
    if resultat.inserted_id:
        mongo_client.close()
        return jsonify({"succès": True, "id_insertion": str(resultat.inserted_id)}), 201
    else:
        mongo_client.close()
        return jsonify({"succès": False, "message": "Erreur lors de l'insertion"}), 500

# Mettre à jour une équipe
@equipes_blueprint.route('/update_equipe/<id>', methods=['PUT'])
def update_equipe(id):
    mongo_client = Mongo2Client(db_name='pingpong')
    data = request.get_json()
    mise_a_jour = {}
    for champ in ['joueurs', 'type']:
        if champ in data:
            mise_a_jour[champ] = data[champ]
    resultat = mongo_client.db['equipe'].update_one({'_id': ObjectId(id)}, {'$set': mise_a_jour})
    if resultat.modified_count > 0:
        mongo_client.close()
        return jsonify({"succès": True, "message": "L'équipe a été mise à jour"}), 200
    else:
        mongo_client.close()
        return jsonify({"succès": False, "message": "Aucune mise à jour effectuée ou équipe non trouvée"}), 404

# Supprimer une équipe
@equipes_blueprint.route('/delete_equipe/<id>', methods=['DELETE'])
def delete_equipe(id):
    mongo_client = Mongo2Client(db_name='pingpong')
    resultat = mongo_client.db['equipe'].delete_one({'_id': ObjectId(id)})
    if resultat.deleted_count > 0:
        mongo_client.close()
        return jsonify({"succès": True, "message": "L'équipe a été supprimée"}), 200
    else:
        mongo_client.close()
        return jsonify({"succès": False, "message": "Aucune équipe trouvée avec cet ID"}), 404
