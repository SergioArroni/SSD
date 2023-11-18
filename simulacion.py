import simpy
import random
import numpy as np


class Puerto:
    def __init__(self, env, num_remolcadores, num_muelles, puntos_llegada):
        self.env = env
        self.remolcadores = simpy.Resource(env, capacity=num_remolcadores)
        self.muelles = simpy.Resource(env, capacity=num_muelles)
        self.tiempo_descarga = lambda: random.chisquare(
            5
        )  # Chi-cuadrado con 5 grados de libertad para tiempo de descarga
        self.puntos_llegada = [
            (x * 60, y) for x, y in puntos_llegada
        ]  # Convertir las coordenadas x a minutos
        self.tiempos_atraque = []  # Lista para almacenar los tiempos de atraco
        self.numero_total_barcos_atracados = 0
        self.numero_total_barcos_esperando = 0
        self.cola_espera = simpy.Store(env)

    def llegada_petrolero(self, petrolero):
        tiempo_llegada = self.calcular_tiempo_atraque(llevando_barco=False)
        yield self.env.timeout(tiempo_llegada)

        # Intentar obtener un remolcador
        with self.remolcadores.request() as req:
            remolcador_disponible = yield req

            if remolcador_disponible:  # Si hay un remolcador disponible
                tiempo_atraque = self.calcular_tiempo_atraque(llevando_barco=True)
                yield self.env.timeout(tiempo_atraque)
                self.tiempos_atraque.append(self.env.now)
                self.numero_total_barcos_atracados += 1
            else:  # Si no hay remolcador disponible, añadir a la cola de espera
                self.numero_total_barcos_esperando += 1
                yield self.cola_espera.put(petrolero)
                # Esperar a que un remolcador esté disponible
                remolcador_disponible = yield self.remolcadores.request()
                tiempo_atraque = self.calcular_tiempo_atraque(llevando_barco=True)
                yield self.env.timeout(tiempo_atraque)
                self.tiempos_atraque.append(self.env.now)
                self.numero_total_barcos_atracados += 1

    def calcular_tiempo_llegada(self):
        x_actual = self.env.now
        for i in range(len(self.puntos_llegada) - 1):
            x0, y0 = self.puntos_llegada[i]
            x1, y1 = self.puntos_llegada[i + 1]
            if x_actual >= x0 and x_actual < x1:
                m = (y1 - y0) / (x1 - x0)
                b = y0 - m * x0
                tiempo_llegada = max(
                    0, (x1 - x_actual) / m
                )  # Evitar tiempos de llegada negativos
                return tiempo_llegada

    def calcular_tiempo_atraque(self, llevando_barco):
        if llevando_barco:
            return max(
                0, random.gauss(10, 3)
            )  # Remolque llevando un barco, tiempo desde desplazamientos.txt
        else:
            return max(0, random.gauss(2, 1))  # Remolque vacío, distribución normal


# Configuración inicial
num_remolcadores = 10
num_muelles = 20
puntos_llegada = [(0, 5), (5, 7), (8, 6), (15, 9), (17, 6), (24, 5)]
desplazamientos_file = "./desplazamiento/E5.desplazamientos.txt"

# Simulación
env = simpy.Environment()
puerto = Puerto(
    env, num_remolcadores, num_muelles, puntos_llegada, desplazamientos_file
)


# Proceso de llegada de petroleros
def llegada_petroleros(env, puerto):
    for i in range(10):  # Número de petroleros a simular
        petrolero = f"Petrolero-{i}"
        env.process(puerto.llegada_petrolero(petrolero))
        yield env.timeout(60)  # Intervalo entre llegadas en minutos


env.process(llegada_petroleros(env, puerto))

# Simulación
env.run(until=24 * 60)  # Simulación de 24 horas en minutos

# Calcular estadísticas
tiempo_medio_atraque = (
    sum(puerto.tiempos_atraque) / len(puerto.tiempos_atraque)
    if puerto.tiempos_atraque
    else 0
)
tiempo_maximo_atraque = max(puerto.tiempos_atraque) if puerto.tiempos_atraque else 0
numero_medio_barcos_atracados = (
    puerto.numero_total_barcos_atracados / num_muelles
)  # Promedio por muelle
numero_medio_barcos_esperando = (
    puerto.numero_total_barcos_esperando / num_remolcadores
)  # Promedio por remolcador
if puerto.tiempos_atraque:
    numero_maximo_barcos_esperando = max(
        range(len(puerto.tiempos_atraque))
    )  # Número máximo en cualquier momento
else:
    numero_maximo_barcos_esperando = 0


# Imprimir estadísticas
print("Estadísticas finales de la simulación:")
print(f"Tiempo medio de atraco: {tiempo_medio_atraque:.2f} minutos")
print(f"Tiempo máximo de atraco: {tiempo_maximo_atraque:.2f} minutos")
print(
    f"Número medio de barcos atracados: {numero_medio_barcos_atracados:.2f} por muelle"
)
print(
    f"Número medio de barcos esperando: {numero_medio_barcos_esperando:.2f} por remolcador"
)
print(f"Número máximo de barcos esperando: {numero_maximo_barcos_esperando}")
