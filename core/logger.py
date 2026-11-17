# Universidad Nacional Abierta y a Distancia - UNAD
# Curso: Programacion (Codigo: 213023)
# Fase 4 - Practicas Simuladas (Software FJ)
# Modulo: Sistema de Auditoria y Registro de Eventos (Logging)
# Descripcion: Configura el sistema centralizado de logs para almacenar
# en el archivo 'software_fj.log' todos los eventos normales y excepciones.

import logging
import os

# Nombre y ruta absoluta del archivo de logs requerido por la guia y el anexo
DIRECTORIO_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVO_LOG = os.path.join(DIRECTORIO_BASE, "software_fj.log")

# Configuracion centralizada del logger
logger_sistema = logging.getLogger("SoftwareFJ")
logger_sistema.setLevel(logging.INFO)

# Evitar duplicar handlers si se llama varias veces
if not logger_sistema.handlers:
    # Formato profesional: Fecha y Hora | Nivel | Mensaje
    formato = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Handler para escribir en archivo en codificacion UTF-8
    file_handler = logging.FileHandler(ARCHIVO_LOG, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formato)
    logger_sistema.addHandler(file_handler)

    # Handler opcional para visualizacion en consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formato)
    logger_sistema.addHandler(console_handler)


def registrar_info(mensaje: str):
    """Registra una operacion exitosa o evento informativo relevante."""
    logger_sistema.info(mensaje)


def registrar_advertencia(mensaje: str):
    """Registra una condicion inusual que no detiene el programa."""
    logger_sistema.warning(mensaje)


def registrar_error(mensaje: str, excepcion: Exception = None):
    """
    Registra un error o excepcion detectada en el archivo de auditoria.
    Si se proporciona el objeto de excepcion, incluye los detalles del tipo de fallo.
    """
    if excepcion:
        detalle = f"{mensaje} | Causa: {type(excepcion).__name__} -> {str(excepcion)}"
        logger_sistema.error(detalle)
    else:
        logger_sistema.error(mensaje)
