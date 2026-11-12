# Universidad Nacional Abierta y a Distancia - UNAD
# Curso: Programacion (Codigo: 213023)
# Fase 4 - Practicas Simuladas (Software FJ)
# Modulo: Sistema de Logging

import logging

ARCHIVO_LOG = "software_fj.log"

logging.basicConfig(
    filename=ARCHIVO_LOG,
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8"
)


def registrar_info(mensaje: str):
    """Registra un evento informativo en el archivo de logs."""
    logging.info(mensaje)


def registrar_error(mensaje: str):
    """Registra un error en el archivo de logs."""
    logging.error(mensaje)
