from flask import Flask, jsonify, request
from flask_cors import CORS


from joueurs import joueurs_blueprint;
from tournois import tournois_blueprint;
from matchs  import matchs_blueprint;
from equipes import equipes_blueprint;
from equipement import equipement_blueprint


app = Flask(__name__)
cors = CORS(app)


app.register_blueprint(joueurs_blueprint, url_prefix='/joueurs')
app.register_blueprint(tournois_blueprint, url_prefix='/tournois')
app.register_blueprint(matchs_blueprint, url_prefix='/matchs')
app.register_blueprint(equipes_blueprint, url_prefix='/equipes')
app.register_blueprint(equipement_blueprint, url_prefix='/equipement')



if __name__ == '__main__':
    app.run(debug=True)
