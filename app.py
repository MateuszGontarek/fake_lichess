import chess
import chess.engine
from flask import Flask, render_template, request, redirect, session

board = chess.Board()
engine = chess.engine.SimpleEngine.popen_uci("./stockfish-windows-2022-x86-64.exe")

app = Flask(__name__)
app.secret_key = 'super secret key'

board = chess.Board()
chess_history = []
# chess sprite from https://comamons.wikimedia.org/wiki/Template:SVG_chess_pieces#/media/File:Chess_Pieces_Sprite.svg

def board_to_html() -> str:
    board_html = '<table class="chessboard">'
    for col in range(7, -1, -1):
        board_html += '<tr>'
        for row in range(8):
            square = chess.square(row, col)
            piece = board.piece_at(square)
            background_color = '#b58863' if (col + row) % 2 else '#f0d9b5'
            piece_position = chess.square_name(square)
            if piece:
                color = 'black' if str(piece).islower() else 'white'
                board_html += f'''<td style="background-color: {background_color}" ><button name="position" value="{piece_position}">
                        <img src="/static/images/{piece}_{color}.png" width="60px" height="60px" /></button></td>'''
            else:
                board_html += f'''<td style="background-color: {background_color}" ><button name="position" value="{piece_position}"></td>'''
        board_html += '</tr>'
    board_html += '</table>'
    return board_html

def chess_history_to_html() -> str:
    history_html = '<table class="chess_history">'
    for row in chess_history:
        history_html += '<tr>'
        for col in row:
            history_html += f'<td>{col}</td>'
        history_html += '</tr>'
    history_html += '</table>'
    return history_html

@app.route('/reset', methods=['GET', 'POST'])
def reset() -> render_template:
    global board
    global chess_history
    board = chess.Board()
    chess_history = []
    return redirect('/')



@app.route('/move', methods=['GET', 'POST'])
def move() -> render_template:
    if 'piece' not in session: 
        session['piece'] = request.form['position']
        return redirect('/')

    row_history = [len(chess_history) + 1]
    if not request.form['position'] == session['piece']:
        piece_position = session.pop('piece', None) 
        destination = request.form['position']

        move = chess.Move.from_uci(piece_position + destination) 
        if move in board.legal_moves:
            board.push(move)
            row_history.append(piece_position + destination)

            if board.is_game_over():
                return render_template('index.hbs', board=board_to_html(), result=board.result(), history = chess_history_to_html())
                
            result = engine.play(board, chess.engine.Limit(time=0.01, depth=3))
            board.push(result.move)
            row_history.append(str(result.move))

            chess_history.append(row_history)
            if board.is_game_over():
                return render_template('index.hbs', board=board_to_html(), result=board.result(), history = chess_history_to_html())    
        else:
            session['piece'] = request.form['position']  

    return render_template('index.hbs', board=board_to_html(), history = chess_history_to_html())

@app.route('/', methods=['GET', 'POST'])
def index() -> render_template:
    return render_template('index.hbs', board=board_to_html(), history = chess_history_to_html())

if __name__ == '__main__':
    app.run(debug=True)