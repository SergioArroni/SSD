import simpy
from components.dock.dock import Dock
from components.tugboat.tugboat import Tugboat
from components.port.port import Port


class Event:
    def __init__(
        self,
        env: simpy.Environment,
        muelle: Dock,
        remolcador: Tugboat,
        puerto: Port,
    ) -> None:
        self.env = env
        self.muelle = muelle
        self.remolcador = remolcador
        self.puerto = puerto
        self.duracion_evento = []

    def event(self):
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
