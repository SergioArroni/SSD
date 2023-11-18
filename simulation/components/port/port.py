import simpy


class Port:
    def __init__(self, env: simpy.Environment, puntos_llegada: dict):
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
