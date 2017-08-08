from flask import Flask, request, jsonify
from flask import render_template
from ai.PlayingAgent import PlayingAgent 
import numpy

app = Flask(__name__)

"""
The route should return the checkers game page"
"""
@app.route('/')
def get_game():
	return render_template("index.html")

"""
should return the best move.
Request is an ajax Get Request with the gameboard
"""
@app.route("/moves", methods=["POST"])
def get_move():
	
	# print "best player "+str(best_player_index)

	board = request.get_json()
	# print type(board['data'])
	gameboard = numpy.array(board['data'])
	# print gameboard
	# print type(gameboard[0][0])
	moves = ai_agent.minmax(gameboard,depth=2,player1=best_player_index,player2=best_player_index)
	moves = ai_agent.minmax(gameboard)
	nmoves ={"moves" : moves[1]}
	print nmoves
	return jsonify(nmoves)
	# return "Got Moves"

# app.debug = True
app.run(debug=True, use_reloader=False)