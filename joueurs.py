from flask import Blueprint, request, jsonify
from mongo_client import Mongo2Client
import csv
import io

joueurs_blueprint = Blueprint('joueurs', __name__)
mongo_client = Mongo2Client(db_name='pingpong')

@joueurs_blueprint.route('/', methods=['GET'])
def get_all():
    joueurs_cursor = mongo_client.db['joueur'].find()
    joueurs_liste = list(joueurs_cursor)
    for joueur in joueurs_liste:
        joueur['_id'] = str(joueur['_id'])
    return jsonify(joueurs_liste)

@joueurs_blueprint.route('/', methods=['POST'])
def add_joueur():
    data = request.get_json()
    resultat = mongo_client.db['joueur'].insert_one(data)
    if resultat.inserted_id:
        return jsonify({"succès": True, "id_insertion": str(resultat.inserted_id)})
    else:
        return 500

@joueurs_blueprint.route('/<string:id>', methods=['PUT'])
def update_joueur(id):
    data = request.get_json()
    if not data:
        return 400

    mise_a_jour = {}
    for champ in ['nom', 'prenom', 'categorie', 'sexe', 'point']:
        if champ in data:
            mise_a_jour[champ] = data[champ]

    if mise_a_jour:
        resultat = mongo_client.db['joueur'].update_one({'_id': ObjectId(id)}, {'$set': mise_a_jour})
        if resultat.modified_count > 0:
            return '', 200
        else:
            return 404
    else:
        return 400

@joueurs_blueprint.route('/<string:id>', methods=['DELETE'])
def supprimer_joueur(id):
    try:
        resultat = mongo_client.db['joueur'].delete_one({'_id': ObjectId(id)})
        if resultat.deleted_count > 0:
            return 200
        else:
            return 404
    except Exception as e:
        return 500

@joueurs_blueprint.route('/add_fichier', methods=['POST'])
def add_joueurs_fichier():
    fichier = request.files['fichier']
    if not fichier:
        return 400

    try:
        if not fichier.filename.endswith('.csv'):
            return 400

        fichier.seek(0)
        joueurs = []
        for row in csv.DictReader(io.StringIO(fichier.read().decode('utf-8'))):
            categorie = [{'age': row['Age']}, {'niveau': row['Niveau']}]

            joueur = {
                'prenom': row['Prénom'],
                'nom': row['Nom'],
                'sexe': row['Sexe'],
                'categorie': categorie,
                'point': 0
            }
            joueurs.append(joueur)
    except Exception as e:
        return 400

    try:
        if joueurs:
            resultat = mongo_client.db['joueur'].insert_many(joueurs)
            ids_insertion = [str(id_) for id_ in resultat.inserted_ids]
            return jsonify({"succès": True, "ids_insertion": ids_insertion})
        else:
            return 400
    except Exception as e:
        return 500
