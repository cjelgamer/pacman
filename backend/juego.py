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
        self.turnos_totales = 0
        self.juego_terminado = False
        self.mensaje = ""
        self.num_fantasmas = len(self.pos_fantasmas)
        
        # Sistema de power-up
        self.pacman_poderoso = False
        self.turnos_poder_restantes = 0
        self.power_ups_consumidos = set()
        
        # Configuración de algoritmo
        self.algoritmo = 'minimax'
        self.profundidad_maxima = 2
        
        # Sistema de velocidad
        self.velocidad_pacman = 1.0
        self.velocidad_fantasma_normal = 0.92
        self.velocidad_fantasma_asustado = 0.60
        
    def _crear_laberinto(self):
        """Crea un laberinto estilo Pacman clásico"""
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
            
            distancia = self._distancia_manhattan(pos, self.pos_pacman)
            
            muy_cerca_de_otro = any(
                self._distancia_manhattan(pos, f) < 4 
                for f in fantasmas
            )
            
            if distancia >= distancia_minima and not muy_cerca_de_otro and pos not in fantasmas:
                fantasmas.append(pos)
            
            intentos += 1
        
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
        
        num_capsulas = int(len(espacios_libres) * 0.85)
        capsulas = set(random.sample(espacios_libres, num_capsulas))
        
        return capsulas
    
    def _generar_power_ups(self):
        """Genera 5 power-ups en las esquinas del laberinto"""
        power_ups = set()
        
        esquinas_posibles = []
        
        for f in range(1, 4):
            for c in range(1, 4):
                if self.tablero[f][c] == 1:
                    esquinas_posibles.append((f, c))
        
        for f in range(1, 4):
            for c in range(self.columnas - 4, self.columnas - 1):
                if self.tablero[f][c] == 1:
                    esquinas_posibles.append((f, c))
        
        for f in range(self.filas - 4, self.filas - 1):
            for c in range(1, 4):
                if self.tablero[f][c] == 1:
                    esquinas_posibles.append((f, c))
        
        for f in range(self.filas - 4, self.filas - 1):
            for c in range(self.columnas - 4, self.columnas - 1):
                if self.tablero[f][c] == 1:
                    esquinas_posibles.append((f, c))
        
        if len(esquinas_posibles) >= 5:
            power_ups = set(random.sample(esquinas_posibles, 5))
        
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

        df, dc = movimientos_mapa[direccion]
        nueva_fila = self.pos_pacman[0] + df
        nueva_columna = self.pos_pacman[1] + dc

        if not (0 <= nueva_fila < self.filas and
                0 <= nueva_columna < self.columnas and
                self.tablero[nueva_fila][nueva_columna] == 1):
            return False

        # Mover Pacman
        self.pos_pacman = (nueva_fila, nueva_columna)
        self.movimientos += 1
        self.turnos_totales += 1

        # Reducir turnos de poder (si ya tenía)
        if self.pacman_poderoso:
            self.turnos_poder_restantes -= 1
            if self.turnos_poder_restantes <= 0:
                self.pacman_poderoso = False
                self.turnos_poder_restantes = 0

        # Recoger cápsula normal
        if self.pos_pacman in self.capsulas:
            self.capsulas.remove(self.pos_pacman)
            self.puntuacion += 10
            self.capsulas_recogidas += 1

        # --- POWER-UP: consumo y acumulación de duración ---
        # Solo procesamos si la posición tiene un power-up disponible (no consumido)
        if self.pos_pacman in self.power_ups and self.pos_pacman not in self.power_ups_consumidos:
            # marcar como consumido
            self.power_ups_consumidos.add(self.pos_pacman)
            # opcional: removerlo de self.power_ups para que no siga apareciendo
            # self.power_ups.remove(self.pos_pacman)

            # Si ya está poderoso, sumamos turnos; si no, lo activamos
            DURACION_POWERUP_BASE = 18   # <- cambia este número si quieres otra duración inicial
            DURACION_POWERUP_SUMAR = 10  # <- cuántos turnos suma si ya tenía poder

            if self.pacman_poderoso:
                self.turnos_poder_restantes += DURACION_POWERUP_SUMAR
            else:
                self.pacman_poderoso = True
                self.turnos_poder_restantes = DURACION_POWERUP_BASE

            self.puntuacion += 50

            # DEBUG opcional (quita o comenta en producción)
            # print(f"[DEBUG] Power-up consumido en {self.pos_pacman}. Poder: {self.pacman_poderoso}, turnos_restantes: {self.turnos_poder_restantes}")

        # Verificar colisión con fantasmas (tras el movimiento y eventuales efectos del power-up)
        fantasmas_a_eliminar = []
        for fantasma in list(self.pos_fantasmas):  # lista para evitar problemas al eliminar mientras iteramos
            if self.pos_pacman == fantasma:
                if self.pacman_poderoso:
                    fantasmas_a_eliminar.append(fantasma)
                    self.puntuacion += 200
                else:
                    self.juego_terminado = True
                    self.mensaje = "¡Pacman fue capturado!"
                    self.puntuacion -= 100
                    return True

        for fantasma in fantasmas_a_eliminar:
            if fantasma in self.pos_fantasmas:
                self.pos_fantasmas.remove(fantasma)

        self.num_fantasmas = len(self.pos_fantasmas)

        if len(self.pos_fantasmas) == 0:
            self.juego_terminado = True
            self.mensaje = "¡Pacman ganó! ¡Comió todos los fantasmas!"
            self.puntuacion += 500
            return True

        power_ups_disponibles = self.power_ups - self.power_ups_consumidos
        if len(self.capsulas) == 0 and len(power_ups_disponibles) == 0:
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
            if self.pacman_poderoso:
                velocidad = self.velocidad_fantasma_asustado
            else:
                velocidad = self.velocidad_fantasma_normal
            
            if random.random() < velocidad:
                if self.pacman_poderoso:
                    siguiente_pos = self._siguiente_paso_huyendo_pacman(pos_fantasma)
                else:
                    siguiente_pos = self._siguiente_paso_hacia_pacman(pos_fantasma)
                
                nuevas_posiciones.append(siguiente_pos)
            else:
                nuevas_posiciones.append(pos_fantasma)
        
        self.pos_fantasmas = nuevas_posiciones
        
        fantasmas_a_eliminar = []
        for fantasma in self.pos_fantasmas:
            if self.pos_pacman == fantasma:
                if self.pacman_poderoso:
                    fantasmas_a_eliminar.append(fantasma)
                    self.puntuacion += 200
                else:
                    self.juego_terminado = True
                    self.mensaje = "¡Pacman fue capturado!"
                    self.puntuacion -= 100
                    return
        
        for fantasma in fantasmas_a_eliminar:
            if fantasma in self.pos_fantasmas:
                self.pos_fantasmas.remove(fantasma)
        
        self.num_fantasmas = len(self.pos_fantasmas)
        
        if len(self.pos_fantasmas) == 0:
            self.juego_terminado = True
            self.mensaje = "¡Pacman ganó! ¡Comió todos los fantasmas!"
            self.puntuacion += 500
    
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
        
        mejor_movimiento = max(movimientos, 
            key=lambda pos: self._distancia_manhattan(pos, self.pos_pacman))
        
        return mejor_movimiento
    
    def _distancia_manhattan(self, pos1, pos2):
        """Calcula distancia Manhattan entre dos posiciones"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def _evaluar_modo_cazador(self, distancia_min_fantasma, distancias_fantasmas):
        """Evaluación cuando Pacman tiene poder - CAZAR FANTASMAS"""
        puntos = 0
        
        # BONO por tener poder activo
        puntos += self.turnos_poder_restantes * 80
        
        # 🎯 PRIORIDAD ABSOLUTA: ÚLTIMO FANTASMA
        if len(self.pos_fantasmas) == 1:
            if distancia_min_fantasma == 0:
                puntos += 50000  # ¡COMER!
            elif distancia_min_fantasma == 1:
                puntos += 60000
            elif distancia_min_fantasma == 2:
                puntos += 8000
            elif distancia_min_fantasma <= 4:
                puntos += 6000
            else:
                puntos -= distancia_min_fantasma * 50  # Penalizar lejanía
        
        else:
            # MÚLTIPLES FANTASMAS - Estrategia agresiva
            if distancia_min_fantasma == 0:
                puntos += 3500
            elif distancia_min_fantasma == 1:
                puntos += 2200
            elif distancia_min_fantasma == 2:
                puntos += 1300
            elif distancia_min_fantasma == 3:
                puntos += 700
            elif distancia_min_fantasma <= 5:
                puntos += 300
            else:
                # Si está lejos, penalizar moderadamente
                puntos -= distancia_min_fantasma * 25
        
        # Pequeño bonus por fantasmas cercanos (más oportunidades)
        fantasmas_cercanos = sum(1 for d in distancias_fantasmas if d <= 4)
        puntos += fantasmas_cercanos * 200
        
        return puntos
    
    def _evaluar_modo_supervivencia(self, distancia_min_fantasma, distancia_promedio_fantasmas, power_ups_disponibles):
        """Evaluación cuando Pacman NO tiene poder - SUPERVIVENCIA Y RECOLECCIÓN"""
        puntos = 0
        
        # 🚨 EVASIÓN DE FANTASMAS (MÁXIMA PRIORIDAD)
        if distancia_min_fantasma <= 2:
            puntos -= 5000  # ¡PELIGRO INMINENTE!
        elif distancia_min_fantasma == 3:
            puntos -= 2000
        elif distancia_min_fantasma == 4:
            puntos -= 800
        elif distancia_min_fantasma == 5:
            puntos -= 300
        elif distancia_min_fantasma <= 7:
            puntos -= 50
        else:
            # Zona segura - bonus por distancia
            puntos += min(distancia_min_fantasma * 15, 200)
        
        # 💊 POWER-UPS - SEGUNDA PRIORIDAD (para ganar poder)
        if power_ups_disponibles:
            distancias_power = [self._distancia_manhattan(self.pos_pacman, p) 
                                for p in power_ups_disponibles]
            distancia_min_power = min(distancias_power)
            
            # Prioridad ALTA de power-ups cuando hay peligro
            if distancia_min_fantasma <= 5:
                # ¡Necesita poder urgentemente!
                puntos += (8 - distancia_min_power) * 300
                if distancia_min_power <= 2:
                    puntos += 1500  # Bonus extra por power-up muy cercano
            else:
                # Situación más tranquila - prioridad media
                puntos += (6 - distancia_min_power) * 150
        
        # 🍪 CÁPSULAS - TERCERA PRIORIDAD (recolección segura)
        if self.capsulas:
            distancias_capsulas = [self._distancia_manhattan(self.pos_pacman, c) 
                                   for c in self.capsulas]
            distancia_min_capsula = min(distancias_capsulas)
            
            # Solo recolectar cápsulas si estamos en zona SEGURA
            if distancia_min_fantasma >= 6:
                # Zona segura - alta prioridad de recolección
                puntos -= distancia_min_capsula * 35
            elif distancia_min_fantasma >= 4:
                # Zona medianamente segura - prioridad media
                puntos -= distancia_min_capsula * 15
            else:
                # Zona peligrosa - evitar cápsulas
                puntos += distancia_min_capsula * 10  # Penalizar acercarse a cápsulas en peligro
        
        # 🛡️ BONUS por estar en posición segura
        if distancia_promedio_fantasmas >= 8:
            puntos += 200  # Zona muy segura
        elif distancia_promedio_fantasmas >= 6:
            puntos += 80   # Zona segura
        
        return puntos
    
    def evaluar(self):
        """Función de evaluación del estado (para MAX) - ESTRATEGIA MEJORADA"""
        if self.juego_terminado:
            if "ganó" in self.mensaje:
                return 60000
            else:
                return -15000
        
        puntos = self.puntuacion * 10
        
        # Calcular distancias importantes
        if len(self.pos_fantasmas) > 0:
            distancias_fantasmas = [self._distancia_manhattan(self.pos_pacman, f) 
                                    for f in self.pos_fantasmas]
            distancia_min_fantasma = min(distancias_fantasmas)
            distancia_promedio_fantasmas = sum(distancias_fantasmas) / len(distancias_fantasmas)
        
        power_ups_disponibles = self.power_ups - self.power_ups_consumidos
        
        # 🎯 ESTRATEGIA PRINCIPAL: 3 FASES CLARAS
        
        if self.pacman_poderoso:
            # ⚡ FASE 3: MODO CAZADOR - IR POR FANTASMAS
            puntos += self._evaluar_modo_cazador(distancia_min_fantasma, distancias_fantasmas)
        
        else:
            # 🏃 FASE 1 & 2: MODO SUPERVIVENCIA
            puntos += self._evaluar_modo_supervivencia(
                distancia_min_fantasma, 
                distancia_promedio_fantasmas if len(self.pos_fantasmas) > 0 else 999,
                power_ups_disponibles
            )
        
        # 📊 FACTORES GENERALES
        puntos += self.capsulas_recogidas * 120
        puntos -= self.turnos_totales * 0.5
        
        return puntos
    
    def clonar(self):
        """Crea una copia profunda del estado"""
        nuevo_estado = copy.deepcopy(self)
        return nuevo_estado
    
    def obtener_estado_json(self):
        """Retorna el estado en formato JSON para el frontend"""
        power_ups_visibles = [p for p in self.power_ups if p not in self.power_ups_consumidos]
        
        return {
            'filas': self.filas,
            'columnas': self.columnas,
            'tablero': self.tablero,
            'pos_pacman': self.pos_pacman,
            'pos_fantasmas': self.pos_fantasmas,
            'capsulas': list(self.capsulas),
            'power_ups': power_ups_visibles,
            'puntuacion': self.puntuacion,
            'capsulas_recogidas': self.capsulas_recogidas,
            'total_capsulas': self.capsulas_recogidas + len(self.capsulas) + len(power_ups_visibles),
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