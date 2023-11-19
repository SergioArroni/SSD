import simpy
from events.event import Event
from components.port.port import Port
from components.dock.dock import Dock
from components.tugboat.tugboat import Tugboat


def aux_wait(puerto: Port) -> float:
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
    return sum([tupla[0] * tupla[1] for tupla in esperas_tiempo]) / sum(
        [tupla[0] for tupla in esperas_tiempo]
    )


def llegada_petroleros(
    env: simpy.Environment,
    muelle: Dock,
    remolcador: Tugboat,
    puerto: Port,
    puntos_llegada: dict,
) -> None:
    for i in range(25 * 60):
        if int(i) in puntos_llegada.keys():
            for _ in range(puntos_llegada[int(i)]):
                env.process(Event(env, muelle, remolcador, puerto).event())
        yield env.timeout(1)
