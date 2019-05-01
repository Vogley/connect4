from flask import Flask, request, session, render_template, abort, redirect, url_for, flash, make_response
from flask_restful import reqparse, abort, Api, Resource, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from models import db, Player, Game
from datetime import datetime
import os

app = Flask(__name__)
api = Api(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    app.root_path, "connect4.db"
)
# Suppress deprecation warning
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)




'''*****RESTful Resources*****'''
parser = reqparse.RequestParser()
parser.add_argument('Info')


# Game Resource
# Creates Games and Deletes Games
class MyGame(Resource):
    '''def get(self, game_id):
        headers = {'Content-Type': 'text/html'}
        game = db.session.query(Game).get(game_id)
        return make_response(render_template('gametemp.html', game=game),200,headers)'''

    def delete(self, game_id):
        Game.query.filter_by(id=game_id).delete()
        db.session.commit()
        return '', 204

    def put(self, game_id):
        args = parser.parse_args()
        info = args['Info'].split(';') 
        
        playerID = info[0]
        turns = info[1]
        game = Game.query.filter_by(id=game_id).first()
        game.winner_id = playerID
        game.turn = turns
        db.session.commit()

        return '', 201

# GameList
# shows a list of all games, and lets you POST to add new games
class GameList(Resource):
    def get(self):
        GAMES = [g for g in Game.query.all()]
        username = session["username"]
       
        player = Player.query.get(1)
        for p in Player.query.all():
            if p.username == username:
                player = p
        
        if(len(GAMES) != 0):
            playerGames = [g for g in GAMES if g.player_one == player or g.player_two == player]

            if(len(playerGames) != 0):
                gamelist = []
                for g in playerGames:
                    #Gamelist has all the necessary items to check who created the game, where the game is located, and what the game is called. 
                    gamelist.append(g.game_title())     #First item is game_title
                    gamelist.append(g.id)               #Second item is game_id 
                    gamelist.append(g.player_one.username)       #Third item is the creator of the game
                return gamelist
            else:
                return None
        else:
            return None
        

    def post(self):
        args = parser.parse_args() 
        names = args['Info'].split(';')        
        player1Name = names[0]
        player2Name = names[1]

        # Check if user is in the game.
        username = session["username"]
        if(username == player1Name):
            # Find the Players
            p1 = Player.query.get(1)
            p2 = Player.query.get(1)
            for x in Player.query.all():
                if x.username == player1Name:
                    p1 = x
                elif x.username == player2Name:
                    p2 = x
        
            #Add Game to Session
            tempGame = Game(player_one_id=p1.id, player_two_id=p2.id, winner_id=None)
            db.session.add(tempGame)
            db.session.commit()

            return tempGame.game_title(), 201

        # User not included in game
        else:
            return '', 201


##
## Actually setup the Api resource routing here
##
api.add_resource(GameList, '/games')
api.add_resource(MyGame, '/games/<game_id>')






'''*****Webpage Functions*****'''
# by default, direct to login
@app.route("/")
def default():
        return redirect(url_for("home"))

#Login Function     
@app.route("/home/", methods=["GET", "POST"])
def home():
    #Find the topGames
    allGames = [game for game in db.session.query(Game).all() if game.winner_id != None]
    if allGames != None:
                
        # Top 10 of All Players
        topGames = [None, None, None, None, None, None, None, None, None, None]
        for z in allGames:
            if topGames[0] == None:
                topGames[0] = z

            else:
                for j in range(10):
                    if topGames[j] == None:
                        topGames[j] = z
                        break

                    elif z.turn < topGames[j].turn:
                        topGames.insert(j, z)
                        topGames.remove(topGames[len(topGames)-1])
                        break



    # first check if the user is already logged in
    if "username" in session:
        playersUsernames = [x.username for x in Player.query.all()]
        thisUsername = session["username"]
        if thisUsername in playersUsernames:
            
            player = Player.query.get(1)
            for p in Player.query.all():
                if p.username == thisUsername:
                    player = p
            
            playerGames = player.games()
            if playerGames != None:
                wonGames = [g for g in playerGames if g.winner_id == player.id]
                
                # Top 10 for Player
                topPlayerGames = [None, None, None, None, None, None, None, None, None, None]
                for y in wonGames:
                    if topPlayerGames[0] == None:
                        topPlayerGames[0] = y

                    else:
                        for i in range(10):
                            if topPlayerGames[i] == None:
                                topPlayerGames[i] = y
                                break

                            elif y.turn < topPlayerGames[i].turn:
                                topPlayerGames.insert(i, y)
                                topPlayerGames.remove(topPlayerGames[len(topPlayerGames)-1])
                                break

            return render_template("landing.html", topPlayerGames=topPlayerGames, topGames=topGames, games=playerGames, player=player)
    # if not, and the incoming request is via POST try to log them in
    elif request.method == "POST":

        playersUsernames = [x.username for x in Player.query.all()]
        thisUsername = request.form["user"]
        if thisUsername in playersUsernames:
            session["username"] = thisUsername
            
            player = Player.query.get(1)
            for p in Player.query.all():
                if p.username == thisUsername:
                    player = p
            

            playerGames = player.games()
            if playerGames != None:
                wonGames = [g for g in playerGames if g.winner_id == player.id]
                
                # Top 10 for Player
                topPlayerGames = [None, None, None, None, None, None, None, None, None, None]
                for y in wonGames:
                    if topPlayerGames[0] == None:
                        topPlayerGames[0] = y

                    else:
                        for i in range(10):
                            if topPlayerGames[i] == None:
                                topPlayerGames[i] = y
                                break

                            elif y.turn < topPlayerGames[i].turn:
                                topPlayerGames.insert(i, y)
                                topPlayerGames.remove(topPlayerGames[len(topPlayerGames)-1])
                                break

            return render_template("landing.html", topPlayerGames=topPlayerGames, topGames=topGames, games=playerGames, player=player)
        else:

            return render_template("landing.html", topGames=topGames)
    else:
        # if all else fails, offer to log them in
        return render_template("landing.html", topGames=topGames)

@app.route("/logout/")
def unlogger():
    # if logged in, log out, otherwise offer to log in
    if "username" in session:
        session.clear()
        return redirect(url_for("home"))
    else:
        return redirect(url_for("home"))

# Add User
@app.route("/add_user/", methods=["POST"])
def add_user():
        username = request.form.get("newUser")
        bday = request.form.get("bday")
        print(bday)
        birthday = datetime.strptime(bday ,'%Y-%m-%d')
        print(birthday)
        db.session.add(Player(username=username, birthday=birthday))
        db.session.commit()

        
        flash('New Patron Added.')
        return redirect(url_for("home"))

# Go to Game
@app.route("/game/<game_id>/", methods=["GET", "POST"])
def game(game_id=None):
    if "username" in session:
        if game_id:
            game = db.session.query(Game).get(game_id)
            return render_template("game.html", game=game, key='key')   #Key is just there to validate the request is coming from a valid source
        return abort(404)

    else:
        return redirect(url_for("home"))
















# CLI Commands
@app.cli.command("initdb")
def init_db():
    """Initializes database and any model objects necessary for assignment"""
    db.drop_all()
    db.create_all()

    print("Initialized Connect 4 Database.")


@app.cli.command("devinit")
def init_dev_data():
    """Initializes database with data for development and testing"""
    db.drop_all()
    db.create_all()
    print("Initialized Connect 4 Database.")

    g1 = Game()
    g2 = Game()
    g3 = Game()
    g4 = Game()
    g5 = Game()
    g6 = Game()

    db.session.add(g1)
    db.session.add(g2)
    db.session.add(g3)
    db.session.add(g4)
    db.session.add(g5)
    db.session.add(g6)

    p1 = Player(username="John", birthday=datetime.strptime('12/06/1992', '%m/%d/%Y').date())
    p2 = Player(username="Tom", birthday=datetime.strptime('01/14/1998', '%m/%d/%Y').date())
    p3 = Player(username="Kate", birthday=datetime.strptime('11/13/1997', '%m/%d/%Y').date())
    p4 = Player(username="Julia", birthday=datetime.strptime('04/18/1999', '%m/%d/%Y').date())
    p5 = Player(username="Tyler", birthday=datetime.strptime('07/04/1995', '%m/%d/%Y').date())
    p6 = Player(username="Tess", birthday=datetime.strptime('02/05/2001', '%m/%d/%Y').date())
    p7 = Player(username="Jack", birthday=datetime.strptime('10/12/1998', '%m/%d/%Y').date())
    p8 = Player(username="Jordon", birthday=datetime.strptime('03/14/1993', '%m/%d/%Y').date())


    db.session.add(p1)
    print("Created %s" % p1.username)
    db.session.add(p2)
    print("Created %s" % p2.username)
    db.session.add(p3)
    print("Created %s" % p3.username)
    db.session.add(p4)
    print("Created %s" % p4.username)
    db.session.add(p5)
    print("Created %s" % p5.username)
    db.session.add(p6)
    print("Created %s" % p6.username)
    db.session.add(p7)
    print("Created %s" % p7.username)
    db.session.add(p8)
    print("Created %s" % p8.username) 

    g1.player_one = p1
    g1.player_two = p2

    g2.player_one = p1
    g2.player_two = p4

    g3.player_one = p3
    g3.player_two = p6

    g4.player_one = p7
    g4.player_two = p8

    g5.player_one = p6
    g5.player_two = p5

    g6.player_one = p2
    g6.player_two = p5

    db.session.commit()
    print("Added dummy data.")


# needed to use sessions
# note that this is a terrible secret key
app.secret_key = "mySecret"

if __name__ == "__main__":
    app.run(threaded=True)
