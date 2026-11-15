# Universidad Nacional Abierta y a Distancia - UNAD
# Curso: Programacion (Codigo: 213023)
# Fase 4 - Practicas Simuladas (Software FJ)
# Modulo: Jerarquia de Excepciones


class SoftwareFJError(Exception):
    """
    Excepcion raiz para las anomalias controladas de Software FJ.
    Incorpora codificacion estandarizada para trazabilidad en logs.
    """
    def __init__(self, mensaje: str, codigo_error: str = "ERR_SISTEMA"):
        super().__init__(mensaje)
        self.codigo_error = codigo_error
        self.mensaje = mensaje

    def __str__(self) -> str:
        return f"[{self.codigo_error}] {self.mensaje}"


# =============================================================================
# EXCEPCIONES ASOCIADAS AL CLIENTE
# =============================================================================

class ClienteError(SoftwareFJError):
    """Clase base para todos los errores relacionados con clientes."""
    def __init__(self, mensaje: str, codigo_error: str = "ERR_CLIENTE"):
        super().__init__(mensaje, codigo_error)


class ClienteInvalidoError(ClienteError):
    """Disparada cuando los datos del cliente no cumplen el formato requerido."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR_CLIENTE_FORMATO")


class ClienteNoEncontradoError(ClienteError):
    """Disparada cuando se busca una cedula de cliente inexistente."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR_CLIENTE_NO_EXISTE")


class ClienteDuplicadoError(ClienteError):
    """Disparada cuando se intenta registrar un cliente con cedula repetida."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR_CLIENTE_DUPLICADO")


# =============================================================================
# EXCEPCIONES ASOCIADAS A LOS SERVICIOS
# =============================================================================

class ServicioError(SoftwareFJError):
    """Clase base para errores generados en el catalogo de servicios."""
    def __init__(self, mensaje: str, codigo_error: str = "ERR_SERVICIO"):
        super().__init__(mensaje, codigo_error)


class ServicioInvalidoError(ServicioError):
    """Disparada cuando la definicion de un servicio no es valida."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR_SERVICIO_INVALIDO")


class ParametroInvalidoError(ServicioError):
    """Disparada cuando se reciben parametros numericos fuera de rango."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR_PARAMETRO_FUERA_DE_RANGO")


# =============================================================================
# EXCEPCIONES ASOCIADAS A LAS RESERVAS
# =============================================================================

class ReservaError(SoftwareFJError):
    """Clase base para fallos originados en el proceso de reservas."""
    def __init__(self, mensaje: str, codigo_error: str = "ERR_RESERVA"):
        super().__init__(mensaje, codigo_error)
