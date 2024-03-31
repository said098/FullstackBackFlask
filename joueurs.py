import csv
import io

from bson import ObjectId
from flask import Blueprint, request, jsonify, Flask


# Créer un blueprint pour les joueurs
joueurs_blueprint = Blueprint('joueurs', __name__)


from mongo_client import Mongo2Client




@joueurs_blueprint.route('/liste_joueurs', methods=['GET'])
def get_all():
    mongo_client = Mongo2Client(db_name='pingpong')
    joueurs_cursor = mongo_client.db['joueur'].find()  # Cela retourne un curseur
    joueurs_liste = list(joueurs_cursor)  # Convertit le curseur en liste
    for joueur in joueurs_liste:
        joueur['_id'] = str(joueur['_id'])  # Convertit ObjectId en str
    mongo_client.close()
    return jsonify(joueurs_liste)



@joueurs_blueprint.route('/add_joueur', methods=['POST'])
def add_joueur():
    mongo_client = Mongo2Client(db_name='pingpong')
    data = request.get_json()
    print(data)


    resultat = mongo_client.db['joueur'].insert_one(data)
    if resultat.inserted_id:
        mongo_client.close()
        return jsonify({"succès": True, "id_insertion": str(resultat.inserted_id)}), 201
    else:
        mongo_client.close()
        return jsonify({"succès": False, "message": "Erreur lors de l'insertion"}), 500


@joueurs_blueprint.route('/update_joueur/<id>', methods=['PUT'])
def update_joueur(id):
    mongo_client = Mongo2Client(db_name='pingpong')
    data = request.get_json()
    print(data)
    if not data:
        mongo_client.close()
        return jsonify({"succès": False, "message": "Aucune donnée fournie"}), 400

    mise_a_jour = {}
    for champ in ['nom', 'prenom', 'categorie', 'sexe', 'point']:
        if champ in data:
            mise_a_jour[champ] = data[champ]

    if mise_a_jour:
        resultat = mongo_client.db['joueur'].update_one({'_id': ObjectId(id)}, {'$set': mise_a_jour})
        if resultat.modified_count > 0:
            mongo_client.close()
            return jsonify({"succès": True, "message": "Le joueur a été mis à jour"}), 200
        else:
            mongo_client.close()
            return jsonify({"succès": False, "message": "Aucune mise à jour effectuée"}), 404
    else:
        mongo_client.close()
        return jsonify({"succès": False, "message": "Aucune donnée valide pour la mise à jour"}), 400




@joueurs_blueprint.route('/supprimer_joueur/<id>', methods=['DELETE'])
def supprimer_joueur(id):
    mongo_client = Mongo2Client(db_name='pingpong')
    try:
        # Convertir l'ID de la chaîne à ObjectId pour la recherche dans MongoDB
        resultat = mongo_client.db['joueur'].delete_one({'_id': ObjectId(id)})
        if resultat.deleted_count > 0:
            mongo_client.close()
            return jsonify({"succès": True, "message": "Le joueur a été supprimé"}), 200
        else:
            mongo_client.close()
            return jsonify({"succès": False, "message": "Aucun joueur trouvé avec cet ID"}), 404
    except Exception as e:
        mongo_client.close()
        return jsonify({"succès": False, "message": "Erreur lors de la suppression", "erreur": str(e)}), 500



@joueurs_blueprint.route('/add_fichier', methods=['PUT'])
def add_joueurs_fichier():
    # Obtenir l'instance du client MongoDB
    print("Fichier reçu:", "fichier" in request.files)
    mongo_client = Mongo2Client(db_name='pingpong')
    fichier = request.files['fichier']

    if not fichier:
        mongo_client.close()
        return jsonify({"succès": False, "message": "Aucun fichier fourni"}), 400
    try:
        if not fichier.filename.endswith('.csv'):
            mongo_client.close()
            return jsonify({"succès": False, "message": "Le fichier n'est pas un CSV"}), 400


        fichier.seek(0)
        joueurs = []
        for row in csv.DictReader(io.StringIO(fichier.read().decode('utf-8'))):
            categorie = [{'age': row['Age']}, {'niveau': row['Niveau']}]
            try:
                points = int(row['Points'])
            except ValueError:
                points = 0
            joueur = {
                'prenom': row['Prénom'],
                'nom': row['Nom'],
                'sexe': row['Sexe'],
                'categorie': categorie,
                'point': 0
            }
            joueurs.append(joueur)

    except Exception as e:
        mongo_client.close()
        return jsonify({"succès": False, "message": "Erreur lors de la lecture du fichier", "erreur": str(e)}), 400


    try:
        if joueurs:
            resultat = mongo_client.db['joueur'].insert_many(joueurs)
            ids_insertion = [str(id_) for id_ in resultat.inserted_ids]
            mongo_client.close()
            return jsonify({"succès": True, "ids_insertion": ids_insertion}), 201
        else:
            mongo_client.close()
            return jsonify({"succès": False, "message": "Le fichier CSV est vide"}), 400
    except Exception as e:
        mongo_client.close()
        return jsonify({"succès": False, "message": "Erreur lors de l'insertion des joueurs", "erreur": str(e)}), 500
