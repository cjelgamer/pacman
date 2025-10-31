from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

from backend.juego import EstadoJuego
from backend.minimax import decision_minimax
from backend.poda_alfa_beta import decision_alfa_beta

app = Flask(__name__)
CORS(app)

juego_actual = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/iniciar', methods=['POST'])
def iniciar_juego():
    global juego_actual
    datos = request.json
    algoritmo = datos.get('algoritmo', 'minimax')
    
    juego_actual = EstadoJuego()
    juego_actual.algoritmo = algoritmo
    juego_actual.profundidad_maxima = 2  # Fija en 2
    
    print(f"🎮 Juego iniciado: {algoritmo}")
    print(f"📍 Pacman en: {juego_actual.pos_pacman}")
    print(f"👻 Fantasmas en: {juego_actual.pos_fantasmas}")
    print(f"💊 Cápsulas totales: {len(juego_actual.capsulas)}")
    
    return jsonify({
        'estado': juego_actual.obtener_estado_json(),
        'mensaje': f'Juego iniciado con {algoritmo}'
    })

@app.route('/api/siguiente_turno', methods=['POST'])
def siguiente_turno():
    global juego_actual
    
    if juego_actual is None:
        return jsonify({'error': 'No hay juego iniciado'}), 400
    
    if juego_actual.juego_terminado:
        return jsonify({
            'estado': juego_actual.obtener_estado_json(),
            'terminado': True
        })
    
    # Turno de Pacman (MAX)
    if juego_actual.algoritmo == 'minimax':
        mejor_movimiento = decision_minimax(juego_actual, juego_actual.profundidad_maxima)
    else:
        mejor_movimiento = decision_alfa_beta(juego_actual, juego_actual.profundidad_maxima)
    
    if mejor_movimiento is None:
        juego_actual.juego_terminado = True
        juego_actual.mensaje = "Sin movimientos válidos"
        return jsonify({
            'estado': juego_actual.obtener_estado_json(),
            'terminado': True
        })
    
    juego_actual.mover_pacman(mejor_movimiento)
    
    # Turno de fantasmas (MIN)
    if not juego_actual.juego_terminado:
        juego_actual.mover_fantasmas()
    
    return jsonify({
        'estado': juego_actual.obtener_estado_json(),
        'terminado': juego_actual.juego_terminado,
        'movimiento_pacman': mejor_movimiento
    })

@app.route('/api/estado', methods=['GET'])
def obtener_estado():
    global juego_actual
    
    if juego_actual is None:
        return jsonify({'error': 'No hay juego iniciado'}), 400
    
    return jsonify({
        'estado': juego_actual.obtener_estado_json()
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)