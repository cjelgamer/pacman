let juegoActivo = false;
let autoPlayInterval = null;
const API_URL = 'http://localhost:5000/api';

const btnIniciar = document.getElementById('btn-iniciar');
const btnPaso = document.getElementById('btn-paso');
const tablero = document.getElementById('tablero');
const mensaje = document.getElementById('mensaje');
const autoPlayCheckbox = document.getElementById('auto-play');

const statAlgoritmo = document.getElementById('stat-algoritmo');
const statPuntuacion = document.getElementById('stat-puntuacion');
const statCapsulas = document.getElementById('stat-capsulas');
const statMovimientos = document.getElementById('stat-movimientos');

btnIniciar.addEventListener('click', iniciarJuego);
btnPaso.addEventListener('click', siguienteTurno);
autoPlayCheckbox.addEventListener('change', toggleAutoPlay);

async function iniciarJuego() {
    const algoritmo = document.getElementById('algoritmo').value;
    
    try {
        const response = await fetch(`${API_URL}/iniciar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ algoritmo })
        });
        
        const data = await response.json();
        juegoActivo = true;
        btnPaso.disabled = false;
        actualizarUI(data.estado);
        mostrarMensaje('¡Juego iniciado! Usa Auto-Play o Siguiente Turno', 2000);
        
    } catch (error) {
        console.error('Error al iniciar juego:', error);
        mostrarMensaje('Error al conectar con el servidor', 2000);
    }
}

async function siguienteTurno() {
    if (!juegoActivo) return;
    
    btnPaso.disabled = true;
    
    try {
        const response = await fetch(`${API_URL}/siguiente_turno`, {
            method: 'POST'
        });
        
        const data = await response.json();
        actualizarUI(data.estado);
        
        if (data.terminado) {
            juegoActivo = false;
            autoPlayCheckbox.checked = false;
            detenerAutoPlay();
            mostrarMensaje(data.estado.mensaje, 0);
        } else {
            btnPaso.disabled = false;
        }
        
    } catch (error) {
        console.error('Error en siguiente turno:', error);
        btnPaso.disabled = false;
    }
}

function actualizarUI(estado) {
    statAlgoritmo.textContent = estado.algoritmo === 'minimax' ? 'MINIMAX' : 'ALFA-BETA';
    statPuntuacion.textContent = estado.puntuacion;
    statCapsulas.textContent = `${estado.capsulas_recogidas}/${estado.total_capsulas}`;
    
    const statPoder = document.getElementById('stat-poder');
    const statVelocidad = document.getElementById('stat-velocidad');
    
    if (estado.pacman_poderoso) {
        statPoder.textContent = `⚡${estado.turnos_poder_restantes}`;
        statPoder.style.color = '#00FF00';
        statVelocidad.textContent = '50%';
        statVelocidad.style.color = '#2196F3';
    } else {
        statPoder.textContent = '❌';
        statPoder.style.color = '#fff';
        statVelocidad.textContent = '90%';
        statVelocidad.style.color = '#FF1744';
    }
    
    statMovimientos.textContent = estado.movimientos;
    
    dibujarTablero(estado);
}

function dibujarTablero(estado) {
    tablero.innerHTML = '';
    tablero.style.gridTemplateColumns = `repeat(${estado.columnas}, 30px)`;
    tablero.style.gridTemplateRows = `repeat(${estado.filas}, 30px)`;
    
    const capsulasSet = new Set(estado.capsulas.map(c => `${c[0]}-${c[1]}`));
    const powerUpsSet = new Set(estado.power_ups.map(p => `${p[0]}-${p[1]}`));
    const fantasmasSet = new Set(estado.pos_fantasmas.map(f => `${f[0]}-${f[1]}`));
    
    for (let i = 0; i < estado.filas; i++) {
        for (let j = 0; j < estado.columnas; j++) {
            const celda = document.createElement('div');
            celda.className = 'celda';
            
            const posKey = `${i}-${j}`;
            const esPared = estado.tablero[i][j] === 0;
            
            if (esPared) {
                celda.classList.add('pared');
            } else if (i === estado.pos_pacman[0] && j === estado.pos_pacman[1]) {
                celda.classList.add('pacman');
                if (estado.pacman_poderoso) {
                    celda.classList.add('poderoso');
                }
                celda.textContent = '◐';
            } else if (fantasmasSet.has(posKey)) {
                celda.classList.add('fantasma');
                if (estado.pacman_poderoso) {
                    celda.classList.add('asustado');
                }
                celda.textContent = '👻';
            } else if (powerUpsSet.has(posKey)) {
                celda.classList.add('power-up');
            } else if (capsulasSet.has(posKey)) {
                celda.classList.add('capsula');
            }
            
            tablero.appendChild(celda);
        }
    }
}

function mostrarMensaje(texto, duracion) {
    mensaje.textContent = texto;
    mensaje.classList.add('mostrar');
    
    if (duracion > 0) {
        setTimeout(() => {
            mensaje.classList.remove('mostrar');
        }, duracion);
    }
}

function toggleAutoPlay() {
    if (autoPlayCheckbox.checked) {
        if (juegoActivo) {
            iniciarAutoPlay();
        } else {
            autoPlayCheckbox.checked = false;
            mostrarMensaje('Inicia un juego primero', 2000);
        }
    } else {
        detenerAutoPlay();
    }
}

function iniciarAutoPlay() {
    if (autoPlayInterval) return;
    
    autoPlayInterval = setInterval(() => {
        if (juegoActivo) {
            siguienteTurno();
        } else {
            detenerAutoPlay();
            autoPlayCheckbox.checked = false;
        }
    }, 300);  // 800ms entre movimientos
}

function detenerAutoPlay() {
    if (autoPlayInterval) {
        clearInterval(autoPlayInterval);
        autoPlayInterval = null;
    }
}