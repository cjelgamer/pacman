import random
import copy

class EstadoJuego:
    def __init__(self):
        self.filas = 15
        self.columnas = 19
        
        # Crear laberinto predefinido
        self.tablero = self._crear_laberinto()
        
        # Generar posiciones aleatorias
        self.pos_pacman = self._generar_posicion_aleatoria()
        self.pos_fantasmas = self._generar_posiciones_fantasmas(3)
        
        # Generar cápsulas en espacios vacíos
        self.capsulas = self._generar_capsulas()
        
        # Generar power-ups (cápsulas especiales)
        self.power_ups = self._generar_power_ups()
        
        # Estado del juego
        self.puntuacion = 0
        self.capsulas_recogidas = 0
        self.movimientos = 0
        self.turnos_totales = 0  # Contador global de turnos
        self.juego_terminado = False
        self.mensaje = ""
        self.num_fantasmas = len(self.pos_fantasmas)
        
        # Sistema de power-up
        self.pacman_poderoso = False
        self.turnos_poder_restantes = 0
        
        # Configuración de algoritmo
        self.algoritmo = 'minimax'
        self.profundidad_maxima = 2
        
        # Sistema de velocidad (probabilidad de movimiento por turno)
        self.velocidad_pacman = 1.0  # 100% - siempre se mueve
        self.velocidad_fantasma_normal = 0.90  # 90% - se mueve 9 de cada 10 turnos
        self.velocidad_fantasma_asustado = 0.50  # 50% - se mueve 1 de cada 2 turnos
        
    def _crear_laberinto(self):
        """Crea un laberinto estilo Pacman clásico"""
        # 0 = pared, 1 = espacio libre
        mapa = [
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,0],
            [0,1,0,0,1,0,0,0,1,0,1,0,0,0,1,0,0,1,0],
            [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
            [0,1,0,0,1,0,1,0,0,0,0,0,1,0,1,0,0,1,0],
            [0,1,1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,1,0],
            [0,0,0,0,1,0,0,0,1,0,1,0,0,0,1,0,0,0,0],
            [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
            [0,0,0,0,1,0,1,0,0,0,0,0,1,0,1,0,0,0,0],
            [0,1,1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,1,0],
            [0,1,0,0,1,0,1,0,0,0,0,0,1,0,1,0,0,1,0],
            [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
            [0,1,0,0,1,0,0,0,1,0,1,0,0,0,1,0,0,1,0],
            [0,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        ]
        return mapa
    
    def _generar_posicion_aleatoria(self):
        """Genera una posición aleatoria válida en el tablero"""
        espacios_libres = []
        for fila in range(self.filas):
            for columna in range(self.columnas):
                if self.tablero[fila][columna] == 1:
                    espacios_libres.append((fila, columna))
        
        return random.choice(espacios_libres) if espacios_libres else (13, 9)
    
    def _generar_posiciones_fantasmas(self, num_fantasmas):
        """Genera posiciones aleatorias para los fantasmas, alejadas de Pacman"""
        fantasmas = []
        distancia_minima = 6
        
        espacios_libres = []
        for fila in range(self.filas):
            for columna in range(self.columnas):
                if self.tablero[fila][columna] == 1:
                    espacios_libres.append((fila, columna))
        
        intentos = 0
        max_intentos = 200
        
        while len(fantasmas) < num_fantasmas and intentos < max_intentos:
            pos = random.choice(espacios_libres)
            
            # Verificar que esté lejos de Pacman
            distancia = self._distancia_manhattan(pos, self.pos_pacman)
            
            # Verificar que esté lejos de otros fantasmas
            muy_cerca_de_otro = any(
                self._distancia_manhattan(pos, f) < 4 
                for f in fantasmas
            )
            
            if distancia >= distancia_minima and not muy_cerca_de_otro and pos not in fantasmas:
                fantasmas.append(pos)
            
            intentos += 1
        
        # Si no se pudieron generar suficientes, llenar con posiciones válidas
        while len(fantasmas) < num_fantasmas:
            pos = random.choice(espacios_libres)
            if pos not in fantasmas and pos != self.pos_pacman:
                fantasmas.append(pos)
        
        return fantasmas
    
    def _generar_capsulas(self):
        """Genera cápsulas en espacios libres (85% de los espacios)"""
        capsulas = set()
        posiciones_ocupadas = set([self.pos_pacman] + self.pos_fantasmas)
        
        espacios_libres = []
        for fila in range(self.filas):
            for columna in range(self.columnas):
                if self.tablero[fila][columna] == 1:
                    pos = (fila, columna)
                    if pos not in posiciones_ocupadas:
                        espacios_libres.append(pos)
        
        # Colocar cápsulas en 85% de los espacios libres
        num_capsulas = int(len(espacios_libres) * 0.85)
        capsulas = set(random.sample(espacios_libres, num_capsulas))
        
        return capsulas
    
    def _generar_power_ups(self):
        """Genera 4 power-ups en las esquinas del laberinto"""
        power_ups = set()
        
        # Buscar espacios libres en las esquinas
        esquinas_posibles = []
        
        # Esquina superior izquierda
        for f in range(1, 4):
            for c in range(1, 4):
                if self.tablero[f][c] == 1:
                    esquinas_posibles.append((f, c))
        
        # Esquina superior derecha
        for f in range(1, 4):
            for c in range(self.columnas - 4, self.columnas - 1):
                if self.tablero[f][c] == 1:
                    esquinas_posibles.append((f, c))
        
        # Esquina inferior izquierda
        for f in range(self.filas - 4, self.filas - 1):
            for c in range(1, 4):
                if self.tablero[f][c] == 1:
                    esquinas_posibles.append((f, c))
        
        # Esquina inferior derecha
        for f in range(self.filas - 4, self.filas - 1):
            for c in range(self.columnas - 4, self.columnas - 1):
                if self.tablero[f][c] == 1:
                    esquinas_posibles.append((f, c))
        
        # Seleccionar 4 power-ups únicos
        if len(esquinas_posibles) >= 4:
            power_ups = set(random.sample(esquinas_posibles, 4))
        
        return power_ups
    
    def obtener_movimientos_validos_pacman(self):
        """Retorna lista de movimientos válidos para Pacman"""
        movimientos = []
        direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        nombres = ['arriba', 'abajo', 'izquierda', 'derecha']
        
        fila, columna = self.pos_pacman
        
        for i, (df, dc) in enumerate(direcciones):
            nueva_fila = fila + df
            nueva_columna = columna + dc
            
            if (0 <= nueva_fila < self.filas and 
                0 <= nueva_columna < self.columnas and 
                self.tablero[nueva_fila][nueva_columna] == 1):
                movimientos.append(nombres[i])
        
        return movimientos
    
    def obtener_movimientos_validos_fantasma(self, pos_fantasma):
        """Retorna lista de movimientos válidos para un fantasma"""
        movimientos = []
        direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        fila, columna = pos_fantasma
        
        for df, dc in direcciones:
            nueva_fila = fila + df
            nueva_columna = columna + dc
            
            if (0 <= nueva_fila < self.filas and 
                0 <= nueva_columna < self.columnas and 
                self.tablero[nueva_fila][nueva_columna] == 1):
                movimientos.append((nueva_fila, nueva_columna))
        
        return movimientos
    
    def mover_pacman(self, direccion):
        """Mueve a Pacman en la dirección especificada"""
        movimientos_mapa = {
            'arriba': (-1, 0),
            'abajo': (1, 0),
            'izquierda': (0, -1),
            'derecha': (0, 1)
        }
        
        if direccion not in movimientos_mapa:
            return False
        
        # Pacman SIEMPRE se mueve (velocidad 100%)
        df, dc = movimientos_mapa[direccion]
        nueva_fila = self.pos_pacman[0] + df
        nueva_columna = self.pos_pacman[1] + dc
        
        if not (0 <= nueva_fila < self.filas and 
                0 <= nueva_columna < self.columnas and 
                self.tablero[nueva_fila][nueva_columna] == 1):
            return False
        
        self.pos_pacman = (nueva_fila, nueva_columna)
        self.movimientos += 1
        self.turnos_totales += 1
        
        # Reducir turnos de poder
        if self.pacman_poderoso:
            self.turnos_poder_restantes -= 1
            if self.turnos_poder_restantes <= 0:
                self.pacman_poderoso = False
        
        # Verificar si recoge cápsula normal (SIEMPRE, con o sin poder)
        if self.pos_pacman in self.capsulas:
            self.capsulas.remove(self.pos_pacman)
            self.puntuacion += 10
            self.capsulas_recogidas += 1
        
        # Verificar si recoge power-up
        if self.pos_pacman in self.power_ups:
            self.power_ups.remove(self.pos_pacman)
            self.pacman_poderoso = True
            self.turnos_poder_restantes = 15  # 15 turnos con poder
            self.puntuacion += 50
        
        # Verificar colisión con fantasmas
        if self.pos_pacman in self.pos_fantasmas:
            if self.pacman_poderoso:
                # ⚡ ¡Pacman COME al fantasma!
                self.pos_fantasmas.remove(self.pos_pacman)
                self.puntuacion += 200
                self.num_fantasmas = len(self.pos_fantasmas)
                
                # Si comió todos los fantasmas, VICTORIA
                if len(self.pos_fantasmas) == 0:
                    self.juego_terminado = True
                    self.mensaje = "¡Pacman ganó! ¡Comió todos los fantasmas!"
                    self.puntuacion += 500
            else:
                # Pacman es capturado
                self.juego_terminado = True
                self.mensaje = "¡Pacman fue capturado!"
                self.puntuacion -= 100
            return True
        
        # Verificar si ganó (recogió todas las cápsulas)
        if len(self.capsulas) == 0 and len(self.power_ups) == 0:
            self.juego_terminado = True
            self.mensaje = "¡Pacman ganó! ¡Todas las cápsulas recogidas!"
            self.puntuacion += 500
        
        return True
    
    def mover_fantasmas(self):
        """Mueve todos los fantasmas según su velocidad"""
        if len(self.pos_fantasmas) == 0:
            return
        
        nuevas_posiciones = []
        
        for pos_fantasma in self.pos_fantasmas:
            # Determinar velocidad según estado
            if self.pacman_poderoso:
                velocidad = self.velocidad_fantasma_asustado  # 50%
            else:
                velocidad = self.velocidad_fantasma_normal  # 90%
            
            # Probabilidad de movimiento
            if random.random() < velocidad:
                # El fantasma se mueve
                if self.pacman_poderoso:
                    # Los fantasmas huyen de Pacman
                    siguiente_pos = self._siguiente_paso_huyendo_pacman(pos_fantasma)
                else:
                    # Los fantasmas persiguen a Pacman
                    siguiente_pos = self._siguiente_paso_hacia_pacman(pos_fantasma)
                
                nuevas_posiciones.append(siguiente_pos)
            else:
                # El fantasma NO se mueve este turno (por velocidad)
                nuevas_posiciones.append(pos_fantasma)
        
        self.pos_fantasmas = nuevas_posiciones
        
        # Verificar colisiones
        if self.pos_pacman in self.pos_fantasmas:
            if self.pacman_poderoso:
                # ⚡ Pacman come al fantasma
                self.pos_fantasmas.remove(self.pos_pacman)
                self.puntuacion += 200
                self.num_fantasmas = len(self.pos_fantasmas)
                
                if len(self.pos_fantasmas) == 0:
                    self.juego_terminado = True
                    self.mensaje = "¡Pacman ganó! ¡Comió todos los fantasmas!"
                    self.puntuacion += 500
            else:
                self.juego_terminado = True
                self.mensaje = "¡Pacman fue capturado!"
                self.puntuacion -= 100
    
    def _siguiente_paso_hacia_pacman(self, pos_fantasma):
        """Calcula el siguiente paso del fantasma hacia Pacman usando BFS"""
        from collections import deque
        
        if pos_fantasma == self.pos_pacman:
            return pos_fantasma
        
        cola = deque([(pos_fantasma, [pos_fantasma])])
        visitados = {pos_fantasma}
        
        while cola:
            pos_actual, camino = cola.popleft()
            
            if pos_actual == self.pos_pacman:
                return camino[1] if len(camino) > 1 else pos_fantasma
            
            for nueva_pos in self.obtener_movimientos_validos_fantasma(pos_actual):
                if nueva_pos not in visitados:
                    visitados.add(nueva_pos)
                    cola.append((nueva_pos, camino + [nueva_pos]))
        
        return pos_fantasma
    
    def _siguiente_paso_huyendo_pacman(self, pos_fantasma):
        """Calcula el siguiente paso del fantasma alejándose de Pacman"""
        movimientos = self.obtener_movimientos_validos_fantasma(pos_fantasma)
        
        if not movimientos:
            return pos_fantasma
        
        # Elegir el movimiento que maximiza la distancia a Pacman
        mejor_movimiento = max(movimientos, 
            key=lambda pos: self._distancia_manhattan(pos, self.pos_pacman))
        
        return mejor_movimiento
    
    def _distancia_manhattan(self, pos1, pos2):
        """Calcula distancia Manhattan entre dos posiciones"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def evaluar(self):
        """Función de evaluación del estado (para MAX)"""
        if self.juego_terminado:
            if "ganó" in self.mensaje:
                return 10000
            else:
                return -10000
        
        puntos = self.puntuacion * 10
        
        if len(self.pos_fantasmas) > 0:
            distancias_fantasmas = [self._distancia_manhattan(self.pos_pacman, f) 
                                    for f in self.pos_fantasmas]
            distancia_min_fantasma = min(distancias_fantasmas)
            
            if self.pacman_poderoso:
                # ⚡ MODO CAZADOR: ¡PERSEGUIR Y COMER FANTASMAS!
                # Cuanto más cerca del fantasma, mejor
                
                if distancia_min_fantasma == 0:
                    # ¡Contacto! (se come al fantasma)
                    puntos += 2000
                elif distancia_min_fantasma == 1:
                    # ¡A punto de comerlo!
                    puntos += 1500
                elif distancia_min_fantasma == 2:
                    # Muy cerca
                    puntos += 1000
                elif distancia_min_fantasma == 3:
                    # Cerca
                    puntos += 600
                elif distancia_min_fantasma <= 5:
                    # Persiguiendo
                    puntos += 300
                else:
                    # Demasiado lejos, acercarse
                    puntos -= distancia_min_fantasma * 80
                
                # Bonificación por tiempo de poder restante
                puntos += self.turnos_poder_restantes * 60
                
                # También recoger cápsulas si están en el camino
                if self.capsulas:
                    distancias_capsulas = [self._distancia_manhattan(self.pos_pacman, c) 
                                           for c in self.capsulas]
                    distancia_min_capsula = min(distancias_capsulas)
                    # Prioridad media a cápsulas (menos que fantasmas)
                    puntos -= distancia_min_capsula * 15
                
            else:
                # 🏃 MODO HUIDA: Sin poder, HUYE de los fantasmas
                if distancia_min_fantasma == 1:
                    puntos -= 3000  # ¡PELIGRO EXTREMO!
                elif distancia_min_fantasma == 2:
                    puntos -= 1500  # ¡MUY PELIGROSO!
                elif distancia_min_fantasma == 3:
                    puntos -= 600
                elif distancia_min_fantasma == 4:
                    puntos -= 250
                elif distancia_min_fantasma == 5:
                    puntos -= 80
                elif distancia_min_fantasma == 6:
                    puntos += 50
                else:
                    puntos += distancia_min_fantasma * 40  # Recompensa por estar lejos
        else:
            # ¡No hay fantasmas! Solo recoger cápsulas
            if self.capsulas:
                distancias_capsulas = [self._distancia_manhattan(self.pos_pacman, c) 
                                       for c in self.capsulas]
                distancia_min_capsula = min(distancias_capsulas)
                puntos -= distancia_min_capsula * 50
        
        # 💊 POWER-UPS: Prioridad cuando NO tiene poder y fantasmas están cerca
        if self.power_ups and not self.pacman_poderoso:
            distancias_power = [self._distancia_manhattan(self.pos_pacman, p) 
                                for p in self.power_ups]
            distancia_min_power = min(distancias_power)
            
            if len(self.pos_fantasmas) > 0:
                distancia_fantasma_cercano = min([self._distancia_manhattan(self.pos_pacman, f) 
                                                   for f in self.pos_fantasmas])
                
                # Si fantasma está peligrosamente cerca, PRIORIDAD MÁXIMA en power-up
                if distancia_fantasma_cercano <= 6:
                    puntos -= distancia_min_power * 250  # ¡IR AL POWER-UP YA!
                    
                    if distancia_min_power <= 2:
                        puntos += 1000  # ¡Casi ahí!
                    elif distancia_min_power <= 4:
                        puntos += 600
                elif distancia_fantasma_cercano <= 10:
                    puntos -= distancia_min_power * 80
                else:
                    puntos -= distancia_min_power * 30
            else:
                puntos -= distancia_min_power * 25
        
        # 🍪 CÁPSULAS: Cuando NO tiene poder y está seguro
        if self.capsulas and not self.pacman_poderoso:
            distancias_capsulas = [self._distancia_manhattan(self.pos_pacman, c) 
                                   for c in self.capsulas]
            distancia_min_capsula = min(distancias_capsulas)
            
            if len(self.pos_fantasmas) > 0:
                distancia_fantasma_cercano = min([self._distancia_manhattan(self.pos_pacman, f) 
                                                   for f in self.pos_fantasmas])
                
                # Solo buscar cápsulas si está relativamente seguro
                if distancia_fantasma_cercano > 7:
                    puntos -= distancia_min_capsula * 40  # Ir por cápsulas
                elif distancia_fantasma_cercano > 5:
                    puntos -= distancia_min_capsula * 20  # Cápsulas de oportunidad
            else:
                puntos -= distancia_min_capsula * 50  # Sin fantasmas, ir directo
        
        # 🏆 Bonificaciones por progreso
        puntos += self.capsulas_recogidas * 100
        
        # ⏱️ Penalización muy leve por tiempo
        puntos -= self.turnos_totales * 0.1
        
        return puntos
    
    def clonar(self):
        """Crea una copia profunda del estado"""
        nuevo_estado = copy.deepcopy(self)
        return nuevo_estado
    
    def obtener_estado_json(self):
        """Retorna el estado en formato JSON para el frontend"""
        return {
            'filas': self.filas,
            'columnas': self.columnas,
            'tablero': self.tablero,
            'pos_pacman': self.pos_pacman,
            'pos_fantasmas': self.pos_fantasmas,
            'capsulas': list(self.capsulas),
            'power_ups': list(self.power_ups),
            'puntuacion': self.puntuacion,
            'capsulas_recogidas': self.capsulas_recogidas,
            'total_capsulas': self.capsulas_recogidas + len(self.capsulas) + len(self.power_ups),
            'movimientos': self.movimientos,
            'juego_terminado': self.juego_terminado,
            'mensaje': self.mensaje,
            'algoritmo': self.algoritmo,
            'pacman_poderoso': self.pacman_poderoso,
            'turnos_poder_restantes': self.turnos_poder_restantes,
            'num_fantasmas_total': 3,
            'num_fantasmas_restantes': len(self.pos_fantasmas),
            'fantasmas_comidos': 3 - len(self.pos_fantasmas),
            'velocidad_fantasmas': self.velocidad_fantasma_asustado if self.pacman_poderoso else self.velocidad_fantasma_normal
        }