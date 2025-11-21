import random
import math
# Parametos tieempos (día comienza a las 7AM y la primera ventana de parques se abre a las 8AM)
INICIO_DIA_MIN = 7 * 60  # 420minutos desde medianoche 
DESCANSO_NOCTURNO = 8 * 60  # 8 horas = 480 minutos si sales después de 23:00
TIEMPO_DESCANSO = 15  # ver si eliminar esto

# -------------------------------- #
#      Ventanas de tiempo          #
# -------------------------------- #
VENTANAS = [
    (60, 300),    # 08:00 - 12:00
    (360, 540),   # 13:00 - 16:00
    (600, 720),   # 17:00 - 19:00
    (780, 1080)   # 20:00 - 23:00
]
# --------------------------------- #
# Parametros del algoritmo genético #
# --------------------------------- #
TAM_POBLACION = 80
GENERACIONES = 100
TASA_MUTACION = 0.2
TASA_CRUCE = 0.9
TORNEO_K = 3
N_DESTINOS = 10

# Destinos de los paruqes + duración + ventana asociada
DESTINOS_FIJOS = [
    {"id": 0, "coord": (2.5, 8.4),   "dur": 60, "ventana": VENTANAS[0]},
    {"id": 1, "coord": (25.3, 72.4), "dur": 45, "ventana": VENTANAS[1]},
    {"id": 2, "coord": (12.8, 43.2), "dur": 30, "ventana": VENTANAS[2]},
    {"id": 3, "coord": (97.2, 6.3),  "dur": 45, "ventana": VENTANAS[3]},
    {"id": 4, "coord": (7.23, 86.0), "dur": 60, "ventana": VENTANAS[3]},
    {"id": 5, "coord": (13.5, 5.1),  "dur": 30, "ventana": VENTANAS[1]},
    {"id": 6, "coord": (66.2, 45.9), "dur": 30, "ventana": VENTANAS[2]},
    {"id": 7, "coord": (46.7, 99.8), "dur": 20, "ventana": VENTANAS[3]},
    {"id": 8, "coord": (54.2, 79.3), "dur": 60, "ventana": VENTANAS[3]},
    {"id": 9, "coord": (33.0, 66.6), "dur": 45, "ventana": VENTANAS[3]},
]

def crear_destinos(n=N_DESTINOS):
    return DESTINOS_FIJOS[:n]

# -------------------------------- #
#       Funciones Auxiliares       #
# -------------------------------- #
def distancia(a, b):
    dx = a["coord"][0] - b["coord"][0]
    dy = a["coord"][1] - b["coord"][1]
    return math.hypot(dx, dy)

def minutos_a_fecha(minutos_desde_7):
    minutos_totales = INICIO_DIA_MIN + int(round(minutos_desde_7))
    dias = minutos_totales // (24 * 60)
    minutos_del_dia = minutos_totales % (24 * 60)
    hh = minutos_del_dia // 60
    mm = minutos_del_dia % 60
    return f"Día {dias+1}, {hh:02d}:{mm:02d}"

# -------------------------------- #
#        Funcion Fitness           #
# -------------------------------- #
def fitness_itinerario(individuo, destinos):
    distancia_total = 0.0
    penalizacion = 0.0
    tiempo_actual = 0.0
    
    for i, idx in enumerate(individuo):
        destino = destinos[idx]
        if i > 0:
            dist = distancia(destinos[individuo[i-1]], destino)
            distancia_total += dist
            tiempo_actual += dist + TIEMPO_DESCANSO
        if tiempo_actual < destino["ventana"][0]:
            tiempo_actual = destino["ventana"][0]
        if tiempo_actual > destino["ventana"][1]:
            penalizacion += (tiempo_actual - destino["ventana"][1]) * 10
        tiempo_actual += destino["dur"]
        abs_minutos = INICIO_DIA_MIN + tiempo_actual
        if abs_minutos % (24*60) >= 23*60:
            tiempo_actual += DESCANSO_NOCTURNO
    return -(distancia_total + penalizacion)

# -------------------------------- #
#  Operadores genéticos            #
# -------------------------------- #
def seleccion_torneo(poblacion, destinos, k=TORNEO_K):
    return max(random.sample(poblacion, k), key=lambda ind: fitness_itinerario(ind, destinos))

def cruce_ordenado(p1, p2):
    n = len(p1)
    a, b = sorted(random.sample(range(n), 2))
    hijo = [None]*n
    hijo[a:b] = p1[a:b]
    pos = b
    for g in p2:
        if g not in hijo:
            if pos >= n: pos=0
            hijo[pos] = g
            pos+=1
    return hijo

def mutacion_intercambio(individuo):
    a,b = random.sample(range(len(individuo)),2)
    individuo[a], individuo[b] = individuo[b], individuo[a] # --> Intercambio de posiciones para evitar maximos locales.
    return individuo

def algoritmo_genetico(destinos):
    poblacion = [random.sample(range(len(destinos)), len(destinos)) for _ in range(TAM_POBLACION)]
    elite = max(poblacion, key=lambda ind: fitness_itinerario(ind, destinos))
    print(f"Generación 0 | Mejor fitness: {fitness_itinerario(elite, destinos):.2f}")
    for gen in range(1, GENERACIONES+1):
        nueva = [elite]
        while len(nueva)<TAM_POBLACION:
            p1 = seleccion_torneo(poblacion, destinos)
            p2 = seleccion_torneo(poblacion, destinos)
            hijo = cruce_ordenado(p1,p2) if random.random()<TASA_CRUCE else list(p1)
            if random.random()<TASA_MUTACION: hijo = mutacion_intercambio(hijo)
            nueva.append(hijo)
        poblacion = nueva
        elite_actual = max(poblacion,key=lambda ind: fitness_itinerario(ind,destinos))
        if fitness_itinerario(elite_actual,destinos) > fitness_itinerario(elite,destinos):
            elite = elite_actual
        if gen%10==0 or gen==GENERACIONES:
            print(f"Generación {gen} | Mejor fitness: {fitness_itinerario(elite,destinos):.2f}")
    return elite

# -------------------------------- #
#  Funcion para mostrar recorrido  #
# -------------------------------- #
def mostrar_recorrido(individuo, destinos):
    print("\n--- SIMULACIÓN DEL RECORRIDO ---")
    tiempo_actual = 0.0
    distancia_total = 0.0
    pendientes = [destinos[idx] for idx in individuo]
    ultimo = None

    while pendientes:
        d = pendientes.pop(0)

        # --> viaje desde destino anterior.
        if ultimo is not None:
            dist = distancia(ultimo, d)
            distancia_total += dist
            tiempo_actual += dist + TIEMPO_DESCANSO

        llegada_real = tiempo_actual
        espera = 0

        hora_del_dia = tiempo_actual % (24*60)
        ventana_inicio, ventana_fin = d["ventana"]

        # --> si llega antes de la ventana
        if hora_del_dia < ventana_inicio:
            espera = ventana_inicio - hora_del_dia
            tiempo_actual += espera
            hora_del_dia = ventana_inicio

        # --> si llega tarde a la ventana
        if hora_del_dia > ventana_fin:
            # --> reagendar para el siguiente día en su ventana
            tiempo_actual += (24*60 - hora_del_dia) + ventana_inicio
            print(f"Destino {d['id']} llegó tarde a su ventana, se reagenda")
            pendientes.append(d)
            continue

        print(f"Destino {d['id']} | Llega: {minutos_a_fecha(llegada_real)} | Espera: {int(espera)} min | Visita: {d['dur']} min | Sale: {minutos_a_fecha(tiempo_actual+d['dur'])}")

        tiempo_actual += d["dur"]
        ultimo = d

        # --> Penalización por descanso nocturno
        abs_minutos = INICIO_DIA_MIN + tiempo_actual
        if abs_minutos % (24*60) >= 23*60:
            tiempo_actual += DESCANSO_NOCTURNO

    print(f"\nDistancia total recorrida (unidades): {distancia_total:.2f}")
    print("Nota: 1 unidad de distancia = 1 minuto de viaje")

destinos = crear_destinos(N_DESTINOS)
mejor = algoritmo_genetico(destinos)
print("\n--- RESULTADOS ---")
print("Mejor itinerario encontrado:", mejor)
print("Fitness final:", fitness_itinerario(mejor,destinos))
print("\nDetalle de destinos visitados (datos):")
for idx in mejor:
    d=destinos[idx]
    print(f"Destino {d['id']} | Coord={d['coord']} | Dur={d['dur']}min | Ventana={d['ventana']}")
mostrar_recorrido(mejor,destinos)
