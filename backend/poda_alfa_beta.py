import time

# Variables globales para control
tiempo_inicio = 0
TIEMPO_MAXIMO = 2.5
nodos_explorados = 0
nodos_podados = 0  # Contador de podas

def decision_alfa_beta(estado, profundidad_maxima):
    """
    ALGORITMO MINIMAX CON PODA ALFA-BETA
    
    Retorna la mejor decisión para Pacman (MAX) explorando el árbol de juego
    pero PODANDO ramas que no pueden afectar la decisión final.
    
    MÁS EFICIENTE que Minimax clásico - explora menos nodos.
    
    Args:
        estado: Estado actual del juego
        profundidad_maxima: Profundidad máxima del árbol a explorar
    
    Returns:
        str: Mejor movimiento ('arriba', 'abajo', 'izquierda', 'derecha')
    """
    global tiempo_inicio, nodos_explorados, nodos_podados
    tiempo_inicio = time.time()
    nodos_explorados = 0
    nodos_podados = 0
    
    mejor_valor = float('-inf')
    mejor_movimiento = None
    alfa = float('-inf')  # Mejor valor garantizado para MAX
    beta = float('inf')   # Mejor valor garantizado para MIN
    
    movimientos_validos = estado.obtener_movimientos_validos_pacman()
    
    if not movimientos_validos:
        print(f"[ALFA-BETA] Sin movimientos válidos")
        return None
    
    print(f"[ALFA-BETA] Explorando con profundidad: {profundidad_maxima}")
    
    for movimiento in movimientos_validos:
        # Simular el movimiento de Pacman
        estado_siguiente = estado.clonar()
        estado_siguiente.mover_pacman(movimiento)
        nodos_explorados += 1
        
        # Si el juego terminó, evaluar directamente
        if estado_siguiente.juego_terminado:
            valor = estado_siguiente.evaluar()
        else:
            # Llamar a MIN con alfa y beta
            valor = valor_min_alfa_beta(estado_siguiente, profundidad_maxima - 1, 0, alfa, beta)
        
        if valor > mejor_valor:
            mejor_valor = valor
            mejor_movimiento = movimiento
        
        # Actualizar alfa (mejor valor para MAX)
        alfa = max(alfa, mejor_valor)
        
        # Timeout de seguridad
        if time.time() - tiempo_inicio > TIEMPO_MAXIMO:
            print(f"[ALFA-BETA] Timeout alcanzado")
            break
    
    tiempo_total = time.time() - tiempo_inicio
    print(f"[ALFA-BETA] Nodos explorados: {nodos_explorados}, Podados: {nodos_podados} en {tiempo_total:.3f}s")
    print(f"[ALFA-BETA] Mejor movimiento: {mejor_movimiento} (valor: {mejor_valor:.2f})")
    
    return mejor_movimiento if mejor_movimiento else movimientos_validos[0]


def valor_max_alfa_beta(estado, profundidad, indice_fantasma, alfa, beta):
    """
    Función MAX con Poda Alfa-Beta
    
    Pacman (MAX) busca maximizar utilidad.
    PODA: Si valor >= beta, no explorar más (poda beta).
    
    Args:
        estado: Estado actual
        profundidad: Profundidad restante
        indice_fantasma: No usado en MAX
        alfa: Mejor valor garantizado para MAX
        beta: Mejor valor garantizado para MIN
    
    Returns:
        float: Valor de utilidad
    """
    global nodos_explorados, nodos_podados
    
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
        nodos_explorados += 1
        
        if estado_siguiente.juego_terminado:
            valor = max(valor, estado_siguiente.evaluar())
        else:
            valor = max(valor, valor_min_alfa_beta(estado_siguiente, profundidad - 1, 0, alfa, beta))
        
        # PODA BETA: Si valor >= beta, MIN no elegirá esta rama
        if valor >= beta:
            nodos_podados += 1
            return valor
        
        # Actualizar alfa
        alfa = max(alfa, valor)
    
    return valor


def valor_min_alfa_beta(estado, profundidad, indice_fantasma, alfa, beta):
    """
    Función MIN con Poda Alfa-Beta
    
    Fantasmas (MIN) buscan minimizar utilidad de Pacman.
    PODA: Si valor <= alfa, no explorar más (poda alfa).
    
    Args:
        estado: Estado actual
        profundidad: Profundidad restante
        indice_fantasma: Índice del fantasma actual
        alfa: Mejor valor garantizado para MAX
        beta: Mejor valor garantizado para MIN
    
    Returns:
        float: Valor de utilidad
    """
    global nodos_explorados, nodos_podados
    
    if time.time() - tiempo_inicio > TIEMPO_MAXIMO:
        return estado.evaluar()
    
    if estado.juego_terminado or profundidad == 0:
        return estado.evaluar()
    
    # Si procesamos todos los fantasmas, vuelve a MAX
    if indice_fantasma >= len(estado.pos_fantasmas):
        return valor_max_alfa_beta(estado, profundidad, 0, alfa, beta)
    
    valor = float('inf')
    pos_fantasma = estado.pos_fantasmas[indice_fantasma]
    movimientos_validos = estado.obtener_movimientos_validos_fantasma(pos_fantasma)
    
    if not movimientos_validos:
        return valor_min_alfa_beta(estado, profundidad, indice_fantasma + 1, alfa, beta)
    
    for nueva_pos in movimientos_validos:
        estado_siguiente = estado.clonar()
        estado_siguiente.pos_fantasmas[indice_fantasma] = nueva_pos
        nodos_explorados += 1
        
        # Verificar colisión
        if estado_siguiente.pos_pacman in estado_siguiente.pos_fantasmas:
            if estado_siguiente.pacman_poderoso:
                estado_siguiente.pos_fantasmas.remove(estado_siguiente.pos_pacman)
                estado_siguiente.puntuacion += 200
                
                if len(estado_siguiente.pos_fantasmas) == 0:
                    estado_siguiente.juego_terminado = True
                    estado_siguiente.mensaje = "¡Pacman ganó! ¡Comió todos los fantasmas!"
                    estado_siguiente.puntuacion += 500
            else:
                estado_siguiente.juego_terminado = True
                estado_siguiente.mensaje = "¡Pacman fue capturado!"
                estado_siguiente.puntuacion -= 100
        
        # Procesar siguiente fantasma
        valor = min(valor, valor_min_alfa_beta(estado_siguiente, profundidad, indice_fantasma + 1, alfa, beta))
        
        # PODA ALFA: Si valor <= alfa, MAX no elegirá esta rama
        if valor <= alfa:
            nodos_podados += 1
            return valor
        
        # Actualizar beta
        beta = min(beta, valor)
    
    return valor