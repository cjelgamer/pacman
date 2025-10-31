import time

# Variables globales para control
tiempo_inicio = 0
TIEMPO_MAXIMO = 2.5  # Más tiempo para explorar
nodos_explorados = 0  # Contador de nodos

def decision_minimax(estado, profundidad_maxima):
    """
    ALGORITMO MINIMAX CLÁSICO
    
    Retorna la mejor decisión para Pacman (MAX) explorando TODOS los nodos
    del árbol de juego hasta la profundidad especificada.
    
    NO realiza podas - explora exhaustivamente todas las posibilidades.
    
    Args:
        estado: Estado actual del juego
        profundidad_maxima: Profundidad máxima del árbol a explorar
    
    Returns:
        str: Mejor movimiento ('arriba', 'abajo', 'izquierda', 'derecha')
    """
    global tiempo_inicio, nodos_explorados
    tiempo_inicio = time.time()
    nodos_explorados = 0
    
    mejor_valor = float('-inf')
    mejor_movimiento = None
    
    movimientos_validos = estado.obtener_movimientos_validos_pacman()
    
    if not movimientos_validos:
        print(f"[MINIMAX] Sin movimientos válidos")
        return None
    
    # MINIMAX: NO reduce profundidad - explora completamente
    print(f"[MINIMAX] Explorando con profundidad: {profundidad_maxima}")
    
    for movimiento in movimientos_validos:
        # Simular el movimiento de Pacman
        estado_siguiente = estado.clonar()
        estado_siguiente.mover_pacman(movimiento)
        nodos_explorados += 1
        
        # Si el juego terminó inmediatamente, evaluar
        if estado_siguiente.juego_terminado:
            valor = estado_siguiente.evaluar()
        else:
            # Llamar a MIN (turno de fantasmas)
            valor = valor_min_minimax(estado_siguiente, profundidad_maxima - 1, 0)
        
        if valor > mejor_valor:
            mejor_valor = valor
            mejor_movimiento = movimiento
        
        # Timeout de seguridad
        if time.time() - tiempo_inicio > TIEMPO_MAXIMO:
            print(f"[MINIMAX] Timeout alcanzado")
            break
    
    tiempo_total = time.time() - tiempo_inicio
    print(f"[MINIMAX] Nodos explorados: {nodos_explorados} en {tiempo_total:.3f}s")
    print(f"[MINIMAX] Mejor movimiento: {mejor_movimiento} (valor: {mejor_valor:.2f})")
    
    return mejor_movimiento if mejor_movimiento else movimientos_validos[0]


def valor_max_minimax(estado, profundidad, indice_fantasma):
    """
    Función MAX del algoritmo Minimax
    
    Pacman (jugador MAX) busca MAXIMIZAR la utilidad.
    Explora TODOS los movimientos posibles sin podar.
    
    Args:
        estado: Estado actual del juego
        profundidad: Profundidad restante
        indice_fantasma: Índice del fantasma actual (no usado en MAX)
    
    Returns:
        float: Valor de utilidad del estado
    """
    global nodos_explorados
    
    # Condición de término
    if time.time() - tiempo_inicio > TIEMPO_MAXIMO:
        return estado.evaluar()
    
    if estado.juego_terminado or profundidad == 0:
        return estado.evaluar()
    
    valor = float('-inf')
    movimientos_validos = estado.obtener_movimientos_validos_pacman()
    
    if not movimientos_validos:
        return estado.evaluar()
    
    # EXPLORAR TODOS LOS MOVIMIENTOS (sin podar)
    for movimiento in movimientos_validos:
        estado_siguiente = estado.clonar()
        estado_siguiente.mover_pacman(movimiento)
        nodos_explorados += 1
        
        if estado_siguiente.juego_terminado:
            valor = max(valor, estado_siguiente.evaluar())
        else:
            # Después de MAX viene MIN (fantasmas)
            valor = max(valor, valor_min_minimax(estado_siguiente, profundidad - 1, 0))
    
    return valor


def valor_min_minimax(estado, profundidad, indice_fantasma):
    """
    Función MIN del algoritmo Minimax
    
    Los fantasmas (jugadores MIN) buscan MINIMIZAR la utilidad de Pacman.
    Se procesan secuencialmente (multi-agente).
    Explora TODOS los movimientos sin podar.
    
    Args:
        estado: Estado actual del juego
        profundidad: Profundidad restante
        indice_fantasma: Índice del fantasma actual (0, 1, 2...)
    
    Returns:
        float: Valor de utilidad del estado
    """
    global nodos_explorados
    
    # Condición de término
    if time.time() - tiempo_inicio > TIEMPO_MAXIMO:
        return estado.evaluar()
    
    if estado.juego_terminado or profundidad == 0:
        return estado.evaluar()
    
    # Si ya procesamos todos los fantasmas, vuelve a MAX
    if indice_fantasma >= len(estado.pos_fantasmas):
        return valor_max_minimax(estado, profundidad, 0)
    
    valor = float('inf')
    pos_fantasma = estado.pos_fantasmas[indice_fantasma]
    movimientos_validos = estado.obtener_movimientos_validos_fantasma(pos_fantasma)
    
    if not movimientos_validos:
        # Si este fantasma no puede moverse, pasar al siguiente
        return valor_min_minimax(estado, profundidad, indice_fantasma + 1)
    
    # EXPLORAR TODOS LOS MOVIMIENTOS DEL FANTASMA (sin podar)
    for nueva_pos in movimientos_validos:
        estado_siguiente = estado.clonar()
        estado_siguiente.pos_fantasmas[indice_fantasma] = nueva_pos
        nodos_explorados += 1
        
        # Verificar colisión después de mover el fantasma
        if estado_siguiente.pos_pacman in estado_siguiente.pos_fantasmas:
            if estado_siguiente.pacman_poderoso:
                # Pacman come al fantasma
                estado_siguiente.pos_fantasmas.remove(estado_siguiente.pos_pacman)
                estado_siguiente.puntuacion += 200
                
                if len(estado_siguiente.pos_fantasmas) == 0:
                    estado_siguiente.juego_terminado = True
                    estado_siguiente.mensaje = "¡Pacman ganó! ¡Comió todos los fantasmas!"
                    estado_siguiente.puntuacion += 500
            else:
                # Pacman es capturado
                estado_siguiente.juego_terminado = True
                estado_siguiente.mensaje = "¡Pacman fue capturado!"
                estado_siguiente.puntuacion -= 100
        
        # Procesar el siguiente fantasma
        valor = min(valor, valor_min_minimax(estado_siguiente, profundidad, indice_fantasma + 1))
    
    return valor