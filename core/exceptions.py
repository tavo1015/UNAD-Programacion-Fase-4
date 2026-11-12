# Universidad Nacional Abierta y a Distancia - UNAD
# Curso: Programacion (Codigo: 213023)
# Fase 4 - Practicas Simuladas (Software FJ)
# Modulo: Jerarquia de Excepciones


class SoftwareFJError(Exception):
    """Excepcion raiz para el manejo controlado de errores en Software FJ."""
    pass


class ClienteError(SoftwareFJError):
    """Excepcion base para errores del modulo de clientes."""
    pass


class ServicioError(SoftwareFJError):
    """Excepcion base para errores del modulo de servicios."""
    pass


class ReservaError(SoftwareFJError):
    """Excepcion base para errores del modulo de reservas."""
    pass
