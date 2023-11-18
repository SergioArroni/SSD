import simpy
import random


class Tugboat:
    def __init__(self, env: simpy.Environment, num_remolcadores: int) -> None:
        self.env = env
        self.remolcadores = simpy.Resource(env, capacity=num_remolcadores)

    def calcular_tiempo_transporte(self, llevando_barco: bool):
        if llevando_barco:
            return max(0, random.gauss(10, 3))
        else:
            return max(0, random.gauss(2, 1))
