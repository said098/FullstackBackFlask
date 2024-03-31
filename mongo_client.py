from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


class Mongo2Client:
     def __init__(self, host='localhost', port=27017, db_name='pingpong', username='user_name', password=None):
        try:
            if username and password:
                uri = f"mongodb://{username}:{password}@{host}:{port}/{db_name}"
                self.client = MongoClient(uri)
            else:
                self.client = MongoClient(host, port)
            self.db = self.client[db_name]
        except ConnectionFailure as e:
            print("Erreur de connexion à la base de données MongoDB:", e)

     def close(self):
         self.client.close()


if __name__ == '__main__':
    mongo_client = Mongo2Client(db_name='pingpong')
    joueurs = mongo_client.db['joueur'].find()
    for indice, joueur in enumerate(joueurs):
        print(f"{indice+1} : {joueur} \n")

    dict_joueur = {
        'nom': 'Shinwari',
        'prenom': 'Said kamal',
        'categorie': [
            {
                'age': '30'
            },
            {
                'niveau': 'Débutant'
            }
        ],
        'sexe': 'Homme',
        'point': '-1'
    }

    test_insert = mongo_client.db['joueur'].insert_one(dict_joueur)

    print(test_insert)