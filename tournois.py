from datetime import datetime

from bson import ObjectId
from flask import Blueprint, request, jsonify
from mongo_client import Mongo2Client

tournois_blueprint = Blueprint('tournois', __name__)
mongo_client = Mongo2Client(db_name='pingpong')

@tournois_blueprint.route('/', methods=['POST'])
def add_tournoi():
    data = request.get_json()

    matchs_cursor = mongo_client.db['matchs'].find()
    matchs_ids = [str(match['_id']) for match in matchs_cursor]

    data['match'] = matchs_ids

    data['ronde_actuelle'] = 1  

    try:
        resultat = mongo_client.db['tournoi'].insert_one(data)
        return jsonify({"succès": True, "id_insertion": str(resultat.inserted_id)})
    except Exception as e:
        return jsonify({"error": "Erreur lors de l'insertion du tournoi", "details": str(e)})

@tournois_blueprint.route('/', methods=['GET'])
def get_tournois():
    try:
        tournois_cursor = mongo_client.db['tournoi'].find()
        tournois_liste = list(tournois_cursor)
        for tournoi in tournois_liste:
            tournoi['_id'] = str(tournoi['_id'])
            if 'match' in tournoi:
                for match in tournoi['match']:
                    if '_id' in match:
                        match['_id'] = str(match['_id'])
        return jsonify(tournois_liste)
    except Exception as e:
        return jsonify({"error": "Erreur lors de la récupération des tournois", "details": str(e)})

@tournois_blueprint.route('/', methods=['DELETE'])
def delete_tournoi():
    try:
        premier_tournoi = mongo_client.db['tournoi'].find_one({}, sort=[('_id', 1)])

        if premier_tournoi:
            resultat = mongo_client.db['tournoi'].delete_one({'_id': premier_tournoi['_id']})
            if resultat.deleted_count > 0:
                return 200
            else:
                return 404
        else:
            return 404
    except Exception as e:
        return jsonify({"error": "Erreur lors de la suppression du premier tournoi", "details": str(e)})

@tournois_blueprint.route('/equipes_gagnants', methods=['GET'])
def get_equipes_gagnants():
    try:
        matchs = mongo_client.db['matchs'].find()
        equipes_gagnantes = []
        for match in matchs:
            score1 = int(match['score1'])
            score2 = int(match['score2'])
            if score1 > score2:
                equipes_gagnantes.append({"_id": str(match["_id"]), "equipeGagnante": match["equipe1"]})
            elif score2 > score1:
                equipes_gagnantes.append({"_id": str(match["_id"]), "equipeGagnante": match["equipe2"]})
        return jsonify(equipes_gagnantes)
    except Exception as e:
        return jsonify({"error": "Erreur lors de la récupération des équipes gagnantes", "details": str(e)})

@tournois_blueprint.route('/matchs_dans_tounoi', methods=['GET'])
def get_matchs_premier_tournoi():
    try:
        tournoi = mongo_client.db['tournoi'].find_one()

        if not tournoi:
            return 404

        matchs_ids = tournoi.get('match', [])
        matchs_ids = [ObjectId(id) for id in matchs_ids]
        matchs_cursor = mongo_client.db['matchs'].find({'_id': {'$in': matchs_ids}})
        matchs = list(matchs_cursor)
        for match in matchs:
            match['_id'] = str(match['_id'])

        return jsonify(matchs)
    except Exception as e:
        return jsonify({"error": "Erreur lors de la récupération des matchs du premier tournoi", "details": str(e)})

@tournois_blueprint.route('/avancer_ronde', methods=['POST'])
def avancer_ronde():
    try:
        tournoi = mongo_client.db['tournoi'].find_one()
        if not tournoi:
            return 404

        matchs_ids = [ObjectId(id) for id in tournoi['match']]

        matchs = mongo_client.db['matchs'].find({'_id': {'$in': matchs_ids}})
        equipes_gagnantes = []
        for match in matchs:
            score1 = int(match['score1'])
            score2 = int(match['score2'])
            if score1 > score2:
                equipes_gagnantes.append(match['equipe1'])
            elif score2 > score1:
                equipes_gagnantes.append(match['equipe2'])

        if len(equipes_gagnantes) == 1:
            equipe_gagnante = mongo_client.db['equipe'].find_one({'nom': equipes_gagnantes[0]})
            if equipe_gagnante:
                equipe_gagnante['_id'] = str(equipe_gagnante['_id'])
                for joueur in equipe_gagnante.get('joueurs', []):
                    joueur['_id'] = str(joueur['_id'])
                return jsonify({"succès": True, "equipe_gagnante": equipe_gagnante})

        if len(equipes_gagnantes) % 2 != 0:
            return 400

        nouveaux_matchs_ids = []
        for i in range(0, len(equipes_gagnantes), 2):
            date_actuelle = datetime.now().strftime("%d/%m/%Y")
            heure_actuelle = datetime.now().strftime("%H:%M")
            nouveau_match = {
                "equipe1": equipes_gagnantes[i],
                "equipe2": equipes_gagnantes[i + 1],
                "score1": 0,
                "score2": 0,
                "date": date_actuelle,
                "heure": heure_actuelle
            }
            resultat = mongo_client.db['matchs'].insert_one(nouveau_match)
            nouveaux_matchs_ids.append(str(resultat.inserted_id))

        mongo_client.db['tournoi'].update_one(
            {'_id': tournoi['_id']},
            {'$set': {'match': nouveaux_matchs_ids}}
        )

        return jsonify({"succès": True, "message": "Ronde avancée avec succès et nouveaux matchs créés.",
                        "nouveaux_matchs_ids": nouveaux_matchs_ids})
    except Exception as e:
        return jsonify({"error": "Erreur lors de l'avancement de la ronde", "details": str(e)})
