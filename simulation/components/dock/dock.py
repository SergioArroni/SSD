import simpy
import numpy as np


class Dock:
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
