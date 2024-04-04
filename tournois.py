from datetime import datetime

from bson import ObjectId
from flask import Blueprint, request, jsonify, Flask
from flask_cors import CORS

from mongo_client import Mongo2Client

tournois_blueprint = Blueprint('tournois', __name__)


@tournois_blueprint.route('/', methods=['POST'])
def add_tournoi():
    mongo_client = Mongo2Client(db_name='pingpong')
    data = request.get_json()

    matchs_cursor = mongo_client.db['matchs'].find()
    matchs_ids = [str(match['_id']) for match in matchs_cursor]

    data['match'] = matchs_ids

    # Initialise le tournoi avec une ronde actuelle
    data['ronde_actuelle'] = 1  # Commence à la première ronde

    try:
        resultat = mongo_client.db['tournoi'].insert_one(data)
        mongo_client.close()
        return jsonify({"succès": True, "id_insertion": str(resultat.inserted_id)}), 201
    except Exception as e:
        mongo_client.close()
        return '', 500



@tournois_blueprint.route('/', methods=['GET'])
def get_tournois():
    mongo_client = Mongo2Client(db_name='pingpong')
    try:
        tournois_cursor = mongo_client.db['tournoi'].find()
        tournois_liste = list(tournois_cursor)
        for tournoi in tournois_liste:
            tournoi['_id'] = str(tournoi['_id'])
            if 'match' in tournoi:
                for match in tournoi['match']:
                    if '_id' in match:
                        match['_id'] = str(match['_id'])
        mongo_client.close()
        return jsonify(tournois_liste)
    except Exception as e:
        mongo_client.close()
        return '', 500





@tournois_blueprint.route('/<id>', methods=['DELETE'])
def delete_tournoi(id):
    mongo_client = Mongo2Client(db_name='pingpong')
    try:
        oid = ObjectId(id)
        resultat = mongo_client.db['tournoi'].delete_one({'_id': oid})
        if resultat.deleted_count > 0:
            mongo_client.close()
            return '',200
        else:
            mongo_client.close()
            return 404
    except Exception as e:
        mongo_client.close()
        return '', 500

@tournois_blueprint.route('/equipes_gagnants', methods=['GET'])
def get_equipes_gagnants():
    mongo_client = Mongo2Client(db_name='pingpong')
    try:
        matchs = mongo_client.db['matchs'].find()
        equipes_gagnantes = []
        for match in matchs:
            # Convertissez les scores en entiers avant de les comparer
            score1 = int(match['score1'])
            score2 = int(match['score2'])
            if score1 > score2:
                equipes_gagnantes.append({"_id": str(match["_id"]), "equipeGagnante": match["equipe1"]})
            elif score2 > score1:
                equipes_gagnantes.append({"_id": str(match["_id"]), "equipeGagnante": match["equipe2"]})
        print("les qui ont gagner ",equipes_gagnantes)
        return jsonify(equipes_gagnantes), 200
    finally:
        mongo_client.close()






@tournois_blueprint.route('/matchs_dans_tounoi', methods=['GET'])
def get_matchs_premier_tournoi():
    mongo_client = Mongo2Client(db_name='pingpong')
    try:
        tournoi = mongo_client.db['tournoi'].find_one()

        if not tournoi:
            mongo_client.close()
            return '', 404

        matchs_ids = tournoi.get('match', [])
        matchs_ids = [ObjectId(id) for id in matchs_ids]
        matchs_cursor = mongo_client.db['matchs'].find({'_id': {'$in': matchs_ids}})
        matchs = list(matchs_cursor)
        for match in matchs:
            match['_id'] = str(match['_id'])

        mongo_client.close()
        return jsonify(matchs)
    except Exception as e:
        mongo_client.close()
        return '', 500


@tournois_blueprint.route('/avancer_ronde', methods=['POST'])
def avancer_ronde():
    mongo_client = Mongo2Client(db_name='pingpong')
    try:
        tournoi = mongo_client.db['tournoi'].find_one()
        if not tournoi:
            return '',404

        matchs_ids = [ObjectId(id) for id in tournoi['match']]  # Convertit les ID de string à ObjectId

        # Récupérer les matchs basés sur les ID
        matchs = mongo_client.db['matchs'].find({'_id': {'$in': matchs_ids}})
        print("matach", matchs)
        equipes_gagnantes = []
        for match in matchs:
            score1 = int(match['score1'])
            score2 = int(match['score2'])
            if score1 > score2:
                equipes_gagnantes.append(match['equipe1'])
            elif score2 > score1:
                equipes_gagnantes.append(match['equipe2'])

        # Vérification pour un nombre pair d'équipes gagnantes

        print("equipe gagnge ", equipes_gagnantes[0])
        print("equipe gaga longeur", len(equipes_gagnantes))

        if len(equipes_gagnantes) == 1:
            equipe_gagnante = mongo_client.db['equipe'].find_one({'nom': equipes_gagnantes[0]})
            print("equipe gaga", equipe_gagnante)
            print("equipe 1 ", match['equipe1'])
            print("equip2", match['equipe2'])
            if equipe_gagnante:
                equipe_gagnante['_id'] = str(equipe_gagnante['_id'])  # Convertit ObjectId en string
                for joueur in equipe_gagnante.get('joueurs', []):
                    joueur['_id'] = str(joueur['_id'])
                return jsonify({"succès": True, "equipe_gagnante": equipe_gagnante}), 200

        if len(equipes_gagnantes) % 2 != 0:
            return '', 400

        nouveaux_matchs_ids = []
        for i in range(0, len(equipes_gagnantes), 2):
            date_actuelle = datetime.now().strftime("%d/%m/%Y")
            heure_actuelle = datetime.now().strftime("%H:%M")
            nouveau_match = {
                "equipe1": equipes_gagnantes[i],
                "equipe2": equipes_gagnantes[i + 1],
                "score1": 0,  # Initialisation des scores à 0
                "score2": 0,
                "date": date_actuelle,  # Ajout de la date
                "heure": heure_actuelle
            }
            print("nouveau_match", nouveaux_matchs_ids)
            resultat = mongo_client.db['matchs'].insert_one(nouveau_match)
            nouveaux_matchs_ids.append(str(resultat.inserted_id))

        mongo_client.db['tournoi'].update_one(
            {'_id': tournoi['_id']},
            {'$set': {'match': nouveaux_matchs_ids}}  # Remplacez ou ajoutez les nouveaux matchs selon votre logique
        )

        return jsonify({"succès": True, "message": "Ronde avancée avec succès et nouveaux matchs créés.",
                        "nouveaux_matchs_ids": nouveaux_matchs_ids})
    except Exception as e:
        return '', 500