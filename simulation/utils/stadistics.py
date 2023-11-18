import numpy as np


def imprimir_resultados(
    name, num_petroleros, muelle, puerto, num_remolcador, num_muelles
):
    with open(name, "a") as file:
        file.write(
            f"------------------------------------------num_remolcador: {num_remolcador} | num_muelles: {num_muelles}------------------------------------------\n"
        )
        imprimir_contadores(file, num_petroleros, muelle, puerto)
        imprimir_media(file, puerto, muelle)
        imprimir_maximo(file, puerto, muelle)
        imprimir_minimo(file, puerto, muelle)


def imprimir_contadores(file, num_petroleros, muelle, puerto):
    file.write(
        "------------------------------------------Contadores------------------------------------------\n"
    )
    file.write(f"Numero total de barcos: {num_petroleros}\n")
    file.write(
        f"Numero total de barcos atracados: {muelle.numero_total_barcos_atracados}\n"
    )
    file.write(
        f"Numero medio de barcos atracados: { num_petroleros / puerto.max_t_f}\n"
    )
    file.write(f"Tiempo total de simulacion: {puerto.max_t_f}\n")
    file.write(f"Maximo numero de barcos esperando: {puerto.max_espera}\n")
    file.write(
        f"Numero medio de barcos esperando: {np.mean(puerto.tiempos_espera_1)}\n"
    )


def imprimir_media(file, puerto, muelle):
    file.write(
        "------------------------------------------Media------------------------------------------\n"
    )
    file.write(f"Tiempo medio en atracar: {np.mean(puerto.tiempos_atraque)}\n")
    file.write(f"Tiempo medio en espera 1: {np.mean(puerto.tiempos_espera_1)}\n")
    file.write(f"Tiempo medio en espera 2: {np.mean(puerto.tiempos_espera_2)}\n")
    file.write(
        f"Tiempo medio en espera muelle: {np.mean(puerto.tiempos_espera_muelle)}\n"
    )
    file.write(f"Tiempo medio de atraque: {np.mean(muelle.tiempos_atraque)}\n")


def imprimir_maximo(file, puerto, muelle):
    file.write(
        "------------------------------------------Maximo------------------------------------------\n"
    )
    file.write(f"Tiempo maximo en atracar: {np.max(puerto.tiempos_atraque)}\n")
    file.write(f"Tiempo maximo en espera 1: {np.max(puerto.tiempos_espera_1)}\n")
    file.write(f"Tiempo maximo en espera 2: {np.max(puerto.tiempos_espera_2)}\n")
    file.write(
        f"Tiempo maximo en espera muelle: {np.max(puerto.tiempos_espera_muelle)}\n"
    )
    file.write(f"Tiempo maximo de atraque: {np.max(muelle.tiempos_atraque)}\n")


def imprimir_minimo(file, puerto, muelle):
    file.write(
        "------------------------------------------Minimo------------------------------------------\n"
    )
    file.write(f"Tiempo minimo en atracar: {np.min(puerto.tiempos_atraque)}\n")
    file.write(f"Tiempo minimo en espera 1: {np.min(puerto.tiempos_espera_1)}\n")
    file.write(f"Tiempo minimo en espera 2: {np.min(puerto.tiempos_espera_2)}\n")
    file.write(
        f"Tiempo minimo en espera muelle: {np.min(puerto.tiempos_espera_muelle)}\n"
    )
    file.write(f"Tiempo minimo de atraque: {np.min(muelle.tiempos_atraque)}\n")
