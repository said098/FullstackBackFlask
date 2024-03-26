from bson import ObjectId
from flask import Blueprint, request, jsonify, Flask
from flask_cors import CORS

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
        # Gestion des erreurs (par exemple, ID invalide)
        mongo_client.close()
        return jsonify({"succès": False, "message": "Erreur lors de la suppression", "erreur": str(e)}), 500








'''
    if not all(key in data for key in ['nom', 'prenom', 'categorie', 'sexe', 'point']):
        mongo_client.close()
        return jsonify({"succès": False, "message": "Données manquantes"}), 400
'''
