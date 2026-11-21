# Universidad Nacional Abierta y a Distancia - UNAD
# Curso: Programacion (Codigo: 213023)
# Fase 4 - Practicas Simuladas (Software FJ)
# Modulo: Jerarquia de Excepciones Personalizadas
# Descripcion: Define las clases de excepcion del dominio para garantizar
# la deteccion, control y gestion robusta de errores en tiempo de ejecucion.


class SoftwareFJError(Exception):
    """
    Excepcion raiz para todas las anomalias controladas de la empresa Software FJ.
    Permite capturar de forma generica cualquier fallo originado en la aplicacion.
    """
    def __init__(self, mensaje: str, codigo_error: str = "ERR_SISTEMA"):
        super().__init__(mensaje)
        # Codigo estandarizado del error para clasificacion y auditoria en logs
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
    """Disparada cuando los datos del cliente (nombre, email, cedula) no cumplen el formato."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR_CLIENTE_FORMATO")


class ClienteNoEncontradoError(ClienteError):
    """Disparada cuando se intenta operar con una cedula de cliente no registrada."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR_CLIENTE_NO_EXISTE")


class ClienteDuplicadoError(ClienteError):
    """Disparada cuando se intenta registrar un cliente cuya cedula ya existe."""
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
    """Disparada cuando se reciben parametros numericos no permitidos (negativos, capacidad cero, etc)."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR_PARAMETRO_FUERA_DE_RANGO")


class ServicioNoDisponibleError(ServicioError):
    """Disparada cuando un servicio solicitado se encuentra inactivo o fuera de operacion."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR_SERVICIO_NO_DISPONIBLE")


# =============================================================================
# EXCEPCIONES ASOCIADAS A LAS RESERVAS Y OPERACIONES DE NEGOCIO
# =============================================================================

class ReservaError(SoftwareFJError):
    """Clase base para fallos originados en el proceso de reservas."""
    def __init__(self, mensaje: str, codigo_error: str = "ERR_RESERVA"):
        super().__init__(mensaje, codigo_error)


class EstadoReservaInvalidoError(ReservaError):
    """Disparada cuando se intenta una transicion prohibida (ej: cancelar una reserva ya cancelada)."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR_ESTADO_INVALIDO")


class CapacidadExcedidaError(ReservaError):
    """Disparada cuando el numero de asistentes sobrepasa el limite maximo de una sala."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR_CAPACIDAD_EXCEDIDA")


class OperacionNoPermitidaError(SoftwareFJError):
    """Disparada cuando se intenta ejecutar una accion que viola las politicas de Software FJ."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR_OPERACION_NO_PERMITIDA")
