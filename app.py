from flask import Flask, jsonify, request


from joueurs import joueurs_blueprint
from tournois import tournois_blueprint;
from matchs  import matchs_blueprint;

app = Flask(__name__)



app.register_blueprint(joueurs_blueprint, url_prefix='/joueurs')
app.register_blueprint(tournois_blueprint, url_prefix='/tournois')
app.register_blueprint(matchs_blueprint, url_prefix='/matchs')




@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

if __name__ == '__main__':
    app.run(hostname='localhost', port=5000)

