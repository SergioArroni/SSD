import simpy
import random
import numpy as np

random.seed(42)  # Semilla para reproducibilidad
np.random.seed(42)  # Semilla para reproducibilidad


class Muelle:
    def __init__(
        self,
        env: simpy.Environment,
        num_muelles: int,
        grados_libertad: int,
        num_petroleros: int,
    ) -> None:
        self.env = env
        self.muelles = simpy.Resource(env, capacity=num_muelles)
        self.tiempo_descarga = np.random.chisquare(grados_libertad, num_petroleros)
        self.numero_total_barcos_atracados = 0
        self.tiempos_atraque = []


class Remolcador:
    def __init__(self, env: simpy.Environment, num_remolcadores: int) -> None:
        self.env = env
        self.remolcadores = simpy.Resource(env, capacity=num_remolcadores)

    def calcular_tiempo_transporte(self, llevando_barco: bool):
        if llevando_barco:
            return max(0, random.gauss(10, 3))
        else:
            return max(0, random.gauss(2, 1))


class Puerto:
    def __init__(self, env, puntos_llegada):
        self.env = env
        self.puntos_llegada = puntos_llegada
        self.tiempos_espera_1 = []
        self.tiempos_espera_2 = []
        self.tiempos_atraque = []
        self.tiempos_espera_muelle = []
        self.max_t_f = 0
        self.espera = 0
        self.max_espera = 0
        self.esperas_tiempo = []


class Evento:
    def __init__(
        self,
        env: simpy.Environment,
        muelle: Muelle,
        remolcador: Remolcador,
        puerto: Puerto,
    ) -> None:
        self.env = env
        self.muelle = muelle
        self.remolcador = remolcador
        self.puerto = puerto
        self.duracion_evento = []

    def evento(self):
        t_i = self.env.now
        t_i_e = self.env.now

        with self.remolcador.remolcadores.request() as req_remolcador_ida:
            self.puerto.espera += 1
            yield req_remolcador_ida

            t_f_e_1 = self.env.now

            if t_i_e != t_f_e_1:
                self.puerto.max_espera = max(self.puerto.espera, self.puerto.max_espera)

            self.puerto.esperas_tiempo.append((self.env.now, self.puerto.espera - 1))

            self.puerto.espera -= 1

            tiempo_ida_remolcador = self.remolcador.calcular_tiempo_transporte(
                llevando_barco=False
            )

            yield self.env.timeout(tiempo_ida_remolcador)

            t_f_e_2 = self.env.now

            with self.muelle.muelles.request() as req_muelle_existe:
                yield req_muelle_existe

                tiempo_vuelta_remolcador = self.remolcador.calcular_tiempo_transporte(
                    llevando_barco=True
                )
                yield self.env.timeout(tiempo_vuelta_remolcador)

        t_i_a = self.env.now

        with self.muelle.muelles.request() as req_muelle_asignado:
            yield req_muelle_asignado

            self.muelle.numero_total_barcos_atracados += 1
            tiempo_descarga = self.muelle.tiempo_descarga[
                self.muelle.numero_total_barcos_atracados - 1
            ]
            yield self.env.timeout(tiempo_descarga)
        t_f_a = self.env.now
        t_i_e_m = self.env.now
        with self.remolcador.remolcadores.request() as req_remolcador_vuelta:
            yield req_remolcador_vuelta

            t_f_e_m = self.env.now

            tiempo_vuelta_remolcador = self.remolcador.calcular_tiempo_transporte(
                llevando_barco=True
            )
            yield self.env.timeout(tiempo_vuelta_remolcador)
        t_f = self.env.now

        self.puerto.tiempos_atraque.append(t_f - t_i)
        self.puerto.max_t_f = max(t_f, self.puerto.max_t_f)
        self.puerto.tiempos_espera_1.append(t_f_e_1 - t_i_e)
        self.puerto.tiempos_espera_2.append(t_f_e_2 - t_i_e)
        self.puerto.tiempos_espera_muelle.append(t_f_e_m - t_i_e_m)
        self.muelle.tiempos_atraque.append(t_f_a - t_i_a)


# Configuración inicial
num_remolcadores = 10
num_muelles = 20
grados_libertad = 5
puntos_llegada = {0: 5, 5: 7, 8: 6, 15: 9, 17: 6, 24: 5}
puntos_llegada = {int(k) * 60: v for k, v in puntos_llegada.items()}

num_petroleros = sum(puntos_llegada.values())  # Número total de petroleros

# Simulación
env = simpy.Environment()

puerto = Puerto(env, puntos_llegada)
muelle = Muelle(env, num_muelles, grados_libertad, num_petroleros)
remolcador = Remolcador(env, num_remolcadores)


# Proceso de llegada de petroleros
def llegada_petroleros(env):
    for i in range(25 * 60):
        if int(i) in puntos_llegada.keys():
            for _ in range(puntos_llegada[int(i)]):
                env.process(Evento(env, muelle, remolcador, puerto).evento())
        yield env.timeout(1)


env.process(llegada_petroleros(env))

# Simulación
env.run(until=25 * 60)  # Simulación de 24 horas en minutos


esperas_tiempo = [(0, 0)]
for i in range(0, len(puerto.esperas_tiempo) - 1):
    if puerto.esperas_tiempo[i][0] == puerto.esperas_tiempo[i + 1][0]:
        continue

    esperas_tiempo.append(
        (
            abs(puerto.esperas_tiempo[i][0] - puerto.esperas_tiempo[i + 1][0]),
            puerto.esperas_tiempo[i][1],
        )
    )
avg_t_esperando = sum([tupla[0] * tupla[1] for tupla in esperas_tiempo]) / sum(
    [tupla[0] for tupla in esperas_tiempo]
)

# Resultados

print(
    "------------------------------------------Contadores------------------------------------------"
)
print(f"Numero total de barcos: {num_petroleros}")
print(f"Numero total de barcos atracados: {muelle.numero_total_barcos_atracados}")
print(f"Numero medio de barcos atracados: { num_petroleros / puerto.max_t_f}")
print(f"Tiempo total de simulacion: {puerto.max_t_f}")
print(f"Maximo numero de barcos esperando: {puerto.max_espera}")
print(f"Numero medio de barcos esperando: {avg_t_esperando}")

print(
    "------------------------------------------Media------------------------------------------"
)
print(f"Tiempo medio en atracar: {np.mean(puerto.tiempos_atraque)}")
print(f"Tiempo medio en espera 1: {np.mean(puerto.tiempos_espera_1)}")
print(f"Tiempo medio en espera 2: {np.mean(puerto.tiempos_espera_2)}")
print(f"Tiempo medio en espera muelle: {np.mean(puerto.tiempos_espera_muelle)}")
print(f"Tiempo medio de atraque: {np.mean(muelle.tiempos_atraque)}")

print(
    "------------------------------------------Maximo------------------------------------------"
)
print(f"Tiempo maximo en atracar: {np.max(puerto.tiempos_atraque)}")
print(f"Tiempo maximo en espera 1: {np.max(puerto.tiempos_espera_1)}")
print(f"Tiempo maximo en espera 2: {np.max(puerto.tiempos_espera_2)}")
print(f"Tiempo maximo en espera muelle: {np.max(puerto.tiempos_espera_muelle)}")
print(f"Tiempo maximo de atraque: {np.max(muelle.tiempos_atraque)}")

print(
    "------------------------------------------Minimo------------------------------------------"
)
print(f"Tiempo minimo en atracar: {np.min(puerto.tiempos_atraque)}")
print(f"Tiempo minimo en espera 1: {np.min(puerto.tiempos_espera_1)}")
print(f"Tiempo minimo en espera 2: {np.min(puerto.tiempos_espera_2)}")
print(f"Tiempo minimo en espera muelle: {np.min(puerto.tiempos_espera_muelle)}")
print(f"Tiempo minimo de atraque: {np.min(muelle.tiempos_atraque)}")
