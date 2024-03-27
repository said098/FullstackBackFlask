import random
from bson import ObjectId
from mongo_client import Mongo2Client
from flask import Blueprint, request, jsonify, Flask

lanceur_blueprint = Blueprint('lanceur', __name__)

@lanceur_blueprint.route('/', methods=['POST'])
def lancer_match():
    mongo_client = Mongo2Client(db_name='pingpong')
    equipes = mongo_client.db['equipes'].find()  
    equipes_liste = list(equipes)
    if len(equipes_liste) < 2:
        mongo_client.close()
        return jsonify({"succès": False, "message": "Nombre insuffisant d'équipes pour lancer un match"}), 400

    table_disponible = get_table_disponible()  

    if not table_disponible:
        mongo_client.close()
        return jsonify({"succès": False, "message": "Aucune table disponible pour lancer un match"}), 400

    equipe_1, equipe_2 = choisir_equipes(equipes_liste)  

    nouveau_match = {
        "equipes": [equipe_1['_id'], equipe_2['_id']],
        "table": table_disponible,
        "score": [0, 0],  # Score initial à zéro pour chaque équipe
        "date": "",  
        "heure": "",
        "resultat": ""
    }

    resultat = mongo_client.db['matchs'].insert_one(nouveau_match)
    if resultat.inserted_id:
        mongo_client.close()
        return jsonify({"succès": True, "id_match": str(resultat.inserted_id)}), 201
    else:
        mongo_client.close()
        return jsonify({"succès": False, "message": "Erreur lors du lancement du match"}), 500


def get_table_disponible():
    mongo_client = Mongo2Client(db_name='pingpong')
    match_en_cours = mongo_client.db['matchs'].find_one({'date': {'$ne': ''}, 'heure': {'$ne': ''}})  

    if match_en_cours:
        table_match = match_en_cours['table']
        equipement_associé = mongo_client.db['equipement'].find_one({'table_tenis.disponibilité': 'occupé', 'table_tenis.numéro': table_match})
        mongo_client.close()
        if equipement_associé:
            return "La table est occupée par un match"
        else:
            return table_match
    else:
        mongo_client.close()
        return "Il n'y a pas de match en cours"

 
def choisir_equipes(equipes_liste):

    equipe_1 = random.choice(equipes_liste)
    equipe_2 = random.choice(equipes_liste)
    return equipe_1, equipe_2


@lanceur_blueprint.route('/enregistrer_point/<id_match>/<equipe_id>', methods=['PUT'])
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

        equipe_gagnante_id = match['equipes'][equipe_gagnante_index]
        equipe_perdante_id = match['equipes'][equipe_perdante_index]

        # Supprimer l'équipe perdante de la collection des équipes
        mongo_client.db['equipes'].delete_one({'_id': equipe_perdante_id})

        # Relancer un nouveau match avec l'équipe gagnante
        nouvelle_partie = {
            "equipes": [equipe_gagnante_id],
            "table": get_table_disponible(),
            "score": [0],  # Score initial à zéro pour l'équipe gagnante
            "date": "",
            "heure": "",
            "resultat": ""
        }

        # Insérer le nouveau match dans la collection des matchs
        resultat = mongo_client.db['matchs'].insert_one(nouvelle_partie)
        if resultat.inserted_id:
            mongo_client.close()
            return jsonify({"succès": True, "id_nouveau_match": str(resultat.inserted_id)}), 201
        else:
            mongo_client.close()
            return jsonify({"succès": False, "message": "Erreur lors du lancement du nouveau match"}), 500
    else:
        mongo_client.close()
        return jsonify({"succès": False, "message": "Le match n'est pas terminé"}), 400

