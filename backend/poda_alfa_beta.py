import time

tiempo_inicio = 0
TIEMPO_MAXIMO = 1.5

def decision_alfa_beta(estado, profundidad_maxima):
    """Retorna la mejor decisión para Pacman usando Poda Alfa-Beta"""
    global tiempo_inicio
    tiempo_inicio = time.time()
    
    mejor_valor = float('-inf')
    mejor_movimiento = None
    alfa = float('-inf')
    beta = float('inf')
    
    movimientos_validos = estado.obtener_movimientos_validos_pacman()
    
    if not movimientos_validos:
        return None
    
    if len(estado.pos_fantasmas) > 2 and profundidad_maxima > 2:
        profundidad_maxima = 2
    
    for movimiento in movimientos_validos:
        estado_siguiente = estado.clonar()
        estado_siguiente.mover_pacman(movimiento)
        
        # Si el juego terminó, evaluar directamente
        if estado_siguiente.juego_terminado:
            valor = estado_siguiente.evaluar()
        else:
            valor = valor_min_alfa_beta(estado_siguiente, profundidad_maxima - 1, 0, alfa, beta)
        
        if valor > mejor_valor:
            mejor_valor = valor
            mejor_movimiento = movimiento
        
        alfa = max(alfa, mejor_valor)
        
        if time.time() - tiempo_inicio > TIEMPO_MAXIMO:
            break
    
    return mejor_movimiento if mejor_movimiento else movimientos_validos[0]


def valor_max_alfa_beta(estado, profundidad, indice_fantasma, alfa, beta):
    """Calcula el valor MAX (turno de Pacman) con poda Alfa-Beta"""
    if time.time() - tiempo_inicio > TIEMPO_MAXIMO:
        return estado.evaluar()
    
    if estado.juego_terminado or profundidad == 0:
        return estado.evaluar()
    
    valor = float('-inf')
    movimientos_validos = estado.obtener_movimientos_validos_pacman()
    
    if not movimientos_validos:
        return estado.evaluar()
    
    for movimiento in movimientos_validos:
        estado_siguiente = estado.clonar()
        estado_siguiente.mover_pacman(movimiento)
        
        if estado_siguiente.juego_terminado:
            valor = max(valor, estado_siguiente.evaluar())
        else:
            valor = max(valor, valor_min_alfa_beta(estado_siguiente, profundidad - 1, 0, alfa, beta))
        
        if valor >= beta:
            return valor
        
        alfa = max(alfa, valor)
    
    return valor


def valor_min_alfa_beta(estado, profundidad, indice_fantasma, alfa, beta):
    """Calcula el valor MIN (turno de fantasmas) con poda Alfa-Beta"""
    if time.time() - tiempo_inicio > TIEMPO_MAXIMO:
        return estado.evaluar()
    
    if estado.juego_terminado or profundidad == 0:
        return estado.evaluar()
    
    # Si procesamos todos los fantasmas, turno de Pacman (MAX)
    if indice_fantasma >= len(estado.pos_fantasmas):
        return valor_max_alfa_beta(estado, profundidad, 0, alfa, beta)
    
    valor = float('inf')
    pos_fantasma = estado.pos_fantasmas[indice_fantasma]
    movimientos_validos = estado.obtener_movimientos_validos_fantasma(pos_fantasma)
    
    if not movimientos_validos:
        return valor_min_alfa_beta(estado, profundidad, indice_fantasma + 1, alfa, beta)
    
    for nueva_pos in movimientos_validos:
        estado_siguiente = estado.clonar()
        
        # Mover el fantasma actual
        estado_siguiente.pos_fantasmas[indice_fantasma] = nueva_pos
        
        # Verificar colisión DESPUÉS de mover este fantasma
        if estado_siguiente.pos_pacman in estado_siguiente.pos_fantasmas:
            if estado_siguiente.pacman_poderoso:
                # ⚡ Pacman come al fantasma
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
        
        # Continuar con el siguiente fantasma
        valor = min(valor, valor_min_alfa_beta(estado_siguiente, profundidad, indice_fantasma + 1, alfa, beta))
        
        if valor <= alfa:
            return valor
        
        beta = min(beta, valor)
    
    return valor