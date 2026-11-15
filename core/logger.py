# Universidad Nacional Abierta y a Distancia - UNAD
# Curso: Programacion (Codigo: 213023)
# Fase 4 - Practicas Simuladas (Software FJ)
# Modulo: Sistema de Auditoria y Logging

import logging
import os

# Ruta absoluta en la raiz del proyecto para evitar inconsistencias segun directorio de ejecucion
DIRECTORIO_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVO_LOG = os.path.join(DIRECTORIO_BASE, "software_fj.log")

logger_sistema = logging.getLogger("SoftwareFJ")
logger_sistema.setLevel(logging.INFO)

if not logger_sistema.handlers:
    formato = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler = logging.FileHandler(ARCHIVO_LOG, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formato)
    logger_sistema.addHandler(file_handler)


def registrar_info(mensaje: str):
    """Registra una operacion exitosa o evento informativo relevante."""
    logger_sistema.info(mensaje)


def registrar_advertencia(mensaje: str):
    """Registra una condicion inusual que no detiene el programa."""
    logger_sistema.warning(mensaje)


def registrar_error(mensaje: str, excepcion: Exception = None):
    """Registra un error o excepcion detectada incluyendo la causa si existe."""
    if excepcion:
        detalle = f"{mensaje} | Causa: {type(excepcion).__name__} -> {str(excepcion)}"
        logger_sistema.error(detalle)
    else:
        logger_sistema.error(mensaje)
