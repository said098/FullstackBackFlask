import random
from bson import ObjectId
from mongo_client import Mongo2Client
from flask import Blueprint, request, jsonify, Flask

lanceur_blueprint = Blueprint('lanceur', __name__)

@lanceur_blueprint.route('/enregistrer_point', methods=['PUT'])
def enregistrer_point(id_match, equipe_id):
    mongo_client = Mongo2Client(db_name='pingpong')
    match = mongo_client.db['matchs'].find_one({'_id': ObjectId(id_match)})
    if not match:
        mongo_client.close()
        return jsonify({"succès": False, "message": "Match introuvable"}), 404
    
    if equipe_id not in match['equipes']:
        mongo_client.close()
        return jsonify({"succès": False, "message": "ID d'équipe invalide"}), 400

    equipe_index = match['equipes'].index(equipe_id)
    match['score'][equipe_index] += 1

    resultat = mongo_client.db['matchs'].update_one({'_id': ObjectId(id_match)}, {'$set': {'score': match['score']}})
    if resultat.modified_count > 0:
        mongo_client.close()
        return jsonify({"succès": True, "message": "Point enregistré"}), 200
    else:
        mongo_client.close()
        return jsonify({"succès": False, "message": "Erreur lors de l'enregistrement du point"}), 500
    

@lanceur_blueprint.route('/finir_match/<id_match>', methods=['PUT'])
def finir_match(id_match):
    mongo_client = Mongo2Client(db_name='pingpong')
    match = mongo_client.db['matchs'].find_one({'_id': ObjectId(id_match)})

    if not match:
        mongo_client.close()
        return jsonify({"succès": False, "message": "Match introuvable"}), 404
    
    score = match['score']
    if max(score) >= 10:  # Condition de victoire (un des scores atteint 10 points)
        equipe_gagnante_index = score.index(max(score))
        equipe_perdante_index = 1 - equipe_gagnante_index

        equipe_perdante_id = match['equipes'][equipe_perdante_index]

        mongo_client.db['equipes'].delete_one({'_id': equipe_perdante_id})

    else:
        mongo_client.close()
        return jsonify({"succès": False, "message": "Le match n'est pas terminé"}), 400

