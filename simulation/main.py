import simpy
import random
import numpy as np
from utils.stadistics import imprimir_resultados
from utils.util import llegada_petroleros
from components.port.port import Port
from components.dock.dock import Dock
from components.tugboat.tugboat import Tugboat


random.seed(42)  # Semilla para reproducibilidad
np.random.seed(42)  # Semilla para reproducibilidad


def main() -> None:
    # Configuración inicial
    num_remolcadores = 10
    num_muelles = 20
    grados_libertad = 5
    puntos_lambda = {0: 5, 5: 7, 8: 6, 15: 9, 17: 6, 24: 5}
    valores_lambda = {}
    for h in range(0, 25):
        if h in puntos_lambda.keys():
            valores_lambda[h] = puntos_lambda[h]
        else:
            prev, siguiente = max([n for n in puntos_lambda.keys() if n < h]), min(
                [n for n in puntos_lambda.keys() if n > h]
            )
            dh = siguiente - prev
            dd = puntos_lambda[siguiente] - puntos_lambda[prev]
            pendiente = dd / dh
            valores_lambda[h] = puntos_lambda[prev] + pendiente * (h - prev)

    puntos_llegada = {h * 60: np.random.poisson(d) for (h, d) in valores_lambda.items()}
    num_petroleros = sum(puntos_llegada.values())

    # Simulación
    env = simpy.Environment()

    puerto = Port(env, puntos_llegada)
    muelle = Dock(env, num_muelles, grados_libertad, num_petroleros)
    remolcador = Tugboat(env, num_remolcadores)

    env.process(llegada_petroleros(env, muelle, remolcador, puerto, puntos_llegada))

    # Simulación
    env.run(until=25 * 60)

    # Llamar a la función con el nombre del archivo deseado
    name = "../results/resultados.txt"
    imprimir_resultados(
        name, num_petroleros, muelle, puerto, num_remolcadores, num_muelles
    )


if __name__ == "__main__":
    main()
