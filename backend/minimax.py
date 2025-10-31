import time

# Variable global para controlar tiempo
tiempo_inicio = 0
TIEMPO_MAXIMO = 1.5  # Reducido de 2.0 a 1.5 segundos

def decision_minimax(estado, profundidad_maxima):
    """
    Retorna la mejor decisión para Pacman usando Minimax
    """
    global tiempo_inicio
    tiempo_inicio = time.time()
    
    mejor_valor = float('-inf')
    mejor_movimiento = None
    
    movimientos_validos = estado.obtener_movimientos_validos_pacman()
    
    if not movimientos_validos:
        return None
    
    # Si hay muchos fantasmas, reducir profundidad
    if len(estado.pos_fantasmas) > 2 and profundidad_maxima > 2:
        profundidad_maxima = 2
    
    for movimiento in movimientos_validos:
        # Simular movimiento
        estado_siguiente = estado.clonar()
        estado_siguiente.mover_pacman(movimiento)
        
        # Obtener valor usando minimax (turno MIN para fantasmas)
        valor = valor_min_minimax(estado_siguiente, profundidad_maxima - 1, 0)
        
        if valor > mejor_valor:
            mejor_valor = valor
            mejor_movimiento = movimiento
        
        # Verificar timeout
        if time.time() - tiempo_inicio > TIEMPO_MAXIMO:
            break
    
    return mejor_movimiento if mejor_movimiento else movimientos_validos[0]


def valor_max_minimax(estado, profundidad, indice_fantasma):
    """
    Calcula el valor MAX (turno de Pacman)
    """
    # Verificar timeout
    if time.time() - tiempo_inicio > TIEMPO_MAXIMO:
        return estado.evaluar()
    
    # Condiciones de término
    if estado.juego_terminado or profundidad == 0:
        return estado.evaluar()
    
    valor = float('-inf')
    movimientos_validos = estado.obtener_movimientos_validos_pacman()
    
    if not movimientos_validos:
        return estado.evaluar()
    
    for movimiento in movimientos_validos:
        estado_siguiente = estado.clonar()
        estado_siguiente.mover_pacman(movimiento)
        
        # Después de mover Pacman, turno de fantasmas (MIN)
        valor = max(valor, valor_min_minimax(estado_siguiente, profundidad - 1, 0))
    
    return valor


def valor_min_minimax(estado, profundidad, indice_fantasma):
    """
    Calcula el valor MIN (turno de fantasmas)
    Simula el movimiento de todos los fantasmas
    """
    # Verificar timeout
    if time.time() - tiempo_inicio > TIEMPO_MAXIMO:
        return estado.evaluar()
    
    # Condiciones de término
    if estado.juego_terminado or profundidad == 0:
        return estado.evaluar()
    
    # Si procesamos todos los fantasmas, turno de Pacman (MAX)
    if indice_fantasma >= len(estado.pos_fantasmas):
        return valor_max_minimax(estado, profundidad, 0)
    
    valor = float('inf')
    pos_fantasma = estado.pos_fantasmas[indice_fantasma]
    movimientos_validos = estado.obtener_movimientos_validos_fantasma(pos_fantasma)
    
    if not movimientos_validos:
        # Si no hay movimientos, pasar al siguiente fantasma
        return valor_min_minimax(estado, profundidad, indice_fantasma + 1)
    
    for nueva_pos in movimientos_validos:
        estado_siguiente = estado.clonar()
        estado_siguiente.pos_fantasmas[indice_fantasma] = nueva_pos
        
        # Verificar colisión después de mover fantasma
        if estado_siguiente.pos_pacman in estado_siguiente.pos_fantasmas:
            estado_siguiente.juego_terminado = True
            estado_siguiente.mensaje = "¡Pacman fue capturado!"
            estado_siguiente.puntuacion -= 100
        
        # Continuar con el siguiente fantasma
        valor = min(valor, valor_min_minimax(estado_siguiente, profundidad, indice_fantasma + 1))
    
    return valor