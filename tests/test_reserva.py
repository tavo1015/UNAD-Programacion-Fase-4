# Universidad Nacional Abierta y a Distancia - UNAD
# Curso: Programación (Código: 213023)
# Fase 4 - Prácticas Simuladas (Software FJ)
# Módulo: Pruebas unitarias de reservas (Desarrollador 4 - Camilo)
"""Pruebas de Reserva con soporte para una rama de desarrollo aislada.

Ubicar este archivo en la carpeta tests/ del proyecto, junto a models/ y core/.
Si faltan los módulos de otros integrantes, se utilizan dobles mínimos.
El módulo models.reserva siempre debe ser el módulo REAL que se está probando.
"""

from datetime import datetime, timedelta
from pathlib import Path
import sys
import types
import unittest

RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
if not (RAIZ_PROYECTO / "models" / "reserva.py").is_file():
    # Permite ejecutar el archivo temporalmente desde la raíz del proyecto.
    RAIZ_PROYECTO = Path(__file__).resolve().parent
if str(RAIZ_PROYECTO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROYECTO))


def _asegurar_dependencias_en_rama_aislada():
    """Instala dobles solo si falta el conjunto de dependencias externas.

    Nunca reemplaza models.reserva, que debe existir en el proyecto.
    """
    try:
        import core.base  # noqa: F401
        import core.exceptions  # noqa: F401
        import core.logger  # noqa: F401
        import models.cliente  # noqa: F401
        import models.servicios  # noqa: F401
        return False
    except ModuleNotFoundError as exc:
        # Si el error pertenece a una dependencia interna inesperada, no lo ocultamos.
        faltante = exc.name or ""
        permitidos = {"core", "core.base", "core.exceptions", "core.logger",
                      "models", "models.cliente", "models.servicios"}
        if faltante not in permitidos:
            raise

    from abc import ABC, abstractmethod

    # Si algunos módulos reales ya se importaron, no mezclamos versiones reales
    # y simuladas sin control: eliminamos únicamente los módulos externos de esta prueba.
    for nombre in ("core.base", "core.exceptions", "core.logger",
                   "models.cliente", "models.servicios"):
        sys.modules.pop(nombre, None)

    core_pkg = sys.modules.get("core")
    if core_pkg is None:
        core_pkg = types.ModuleType("core")
        core_pkg.__path__ = [str(RAIZ_PROYECTO / "core")]
        sys.modules["core"] = core_pkg

    models_pkg = sys.modules.get("models")
    if models_pkg is None:
        models_pkg = types.ModuleType("models")
        models_pkg.__path__ = [str(RAIZ_PROYECTO / "models")]
        sys.modules["models"] = models_pkg

    core_base = types.ModuleType("core.base")
    core_exc = types.ModuleType("core.exceptions")
    core_log = types.ModuleType("core.logger")
    models_cli = types.ModuleType("models.cliente")
    models_srv = types.ModuleType("models.servicios")

    class EntidadBase(ABC):
        def __init__(self, id_entidad):
            self._id_entidad = str(id_entidad).strip()
            self._fecha_registro = datetime.now()
            self._activo = True

        @property
        def id_entidad(self):
            return self._id_entidad

        @abstractmethod
        def obtener_detalle(self):
            raise NotImplementedError

    class SoftwareFJError(Exception):
        def __init__(self, mensaje, codigo_error="ERR_SISTEMA"):
            super().__init__(mensaje)
            self.codigo_error = codigo_error
            self.mensaje = mensaje

        def __str__(self):
            return f"[{self.codigo_error}] {self.mensaje}"

    class ReservaError(SoftwareFJError):
        def __init__(self, mensaje, codigo_error="ERR_RESERVA"):
            super().__init__(mensaje, codigo_error)

    class EstadoReservaInvalidoError(ReservaError):
        def __init__(self, mensaje):
            super().__init__(mensaje, codigo_error="ERR_ESTADO_INVALIDO")

    class OperacionNoPermitidaError(SoftwareFJError):
        def __init__(self, mensaje):
            super().__init__(mensaje, codigo_error="ERR_OPERACION_NO_PERMITIDA")

    class Cliente(EntidadBase):
        def __init__(self, cedula, nombre, email, telefono, es_vip=False):
            super().__init__(cedula)
            self.cedula = cedula
            self.nombre = nombre
            self.email = email
            self.telefono = telefono
            self.es_vip = es_vip

        def obtener_detalle(self):
            return {"cedula": self.cedula, "nombre": self.nombre,
                    "es_vip": self.es_vip}

    class Servicio(EntidadBase):
        def __init__(self, codigo_servicio, nombre, tarifa_base):
            super().__init__(codigo_servicio)
            self.codigo_servicio = codigo_servicio
            self.nombre = nombre
            self.tarifa_base = float(tarifa_base)

        def calcular_costo(self, descuento=0.0, impuesto=0.19, **kwargs):
            subtotal = self.tarifa_base * (1.0 - min(max(descuento, 0.0), 1.0))
            return round(subtotal * (1.0 + impuesto), 2)

        def obtener_detalle(self):
            return {"codigo": self.codigo_servicio, "nombre": self.nombre}

    core_base.EntidadBase = EntidadBase
    core_exc.SoftwareFJError = SoftwareFJError
    core_exc.ReservaError = ReservaError
    core_exc.EstadoReservaInvalidoError = EstadoReservaInvalidoError
    core_exc.OperacionNoPermitidaError = OperacionNoPermitidaError
    core_log.registrar_info = lambda msg: None
    core_log.registrar_advertencia = lambda msg: None
    core_log.registrar_error = lambda msg, exc=None: None
    models_cli.Cliente = Cliente
    models_srv.Servicio = Servicio

    for pkg, name, module in (
        (core_pkg, "base", core_base), (core_pkg, "exceptions", core_exc),
        (core_pkg, "logger", core_log), (models_pkg, "cliente", models_cli),
        (models_pkg, "servicios", models_srv),
    ):
        sys.modules[module.__name__] = module
        setattr(pkg, name, module)
    return True


_USANDO_STUBS = _asegurar_dependencias_en_rama_aislada()

from core.exceptions import (  # noqa: E402
    EstadoReservaInvalidoError, OperacionNoPermitidaError, ReservaError,
)
from models.cliente import Cliente  # noqa: E402
from models.reserva import EstadoReserva, Reserva  # noqa: E402
from models.servicios import Servicio  # noqa: E402

if not _USANDO_STUBS:
    from models.servicios import ReservaSala  # noqa: E402


def _crear_servicio_prueba():
    if _USANDO_STUBS:
        return Servicio("SALA-T1", "Sala Pruebas", 100000.0)
    return ReservaSala(
        codigo_servicio="SALA-T1", nombre="Sala Pruebas",
        tarifa_base_hora=50000.0, capacidad_maxima=10, horas=2,
    )


def _fecha_futura(dias, hora):
    """Fecha válida futura en el formato exigido por Reserva."""
    return f"{(datetime.now() + timedelta(days=dias)):%Y-%m-%d} {hora}"


class TestModuloReservas(unittest.TestCase):
    """Pruebas de creación, validaciones y transiciones de estado."""

    def setUp(self):
        self.cliente_normal = Cliente(
            "1015248901", "Ana Maria Perez", "ana.perez@correo.com",
            "3105551234", es_vip=False,
        )
        self.cliente_vip = Cliente(
            "1020304050", "Carlos Mendoza", "carlos@empresa.com",
            "3158889900", es_vip=True,
        )
        self.servicio = _crear_servicio_prueba()

    def test_01_creacion_estado_pendiente_y_fecha_valida(self):
        fecha = _fecha_futura(2, "10:00")
        reserva = Reserva("RES-001", self.cliente_normal, self.servicio,
                          fecha, "Prueba")
        self.assertEqual(reserva.estado, EstadoReserva.PENDIENTE)
        self.assertEqual(reserva.fecha_evento, fecha)
        self.assertEqual(reserva.costo_total, 0.0)

    def test_02_rechazo_fecha_invalida_o_inexistente(self):
        with self.assertRaises(ReservaError):
            Reserva("RES-BAD", self.cliente_normal, self.servicio,
                    "2026-02-30 10:00")
        with self.assertRaises(ReservaError):
            Reserva("RES-EMPTY", self.cliente_normal, self.servicio, "")

    def test_03_confirmacion_vip_y_reconfirmacion_bloqueada(self):
        reserva = Reserva("RES-002", self.cliente_vip, self.servicio,
                          _fecha_futura(2, "14:00"))
        total = reserva.confirmar()
        self.assertEqual(reserva.estado, EstadoReserva.CONFIRMADA)
        # Tarifa base 100000, descuento VIP 10 % e IVA 19 %.
        self.assertAlmostEqual(total, 107100.0, places=2)
        with self.assertRaises(EstadoReservaInvalidoError):
            reserva.confirmar()

    def test_04_cancelacion_y_bloqueo_cancelacion_redundante(self):
        reserva = Reserva("RES-003", self.cliente_normal, self.servicio,
                          _fecha_futura(3, "09:00"))
        reserva.cancelar("Cambio de agenda")
        self.assertEqual(reserva.estado, EstadoReserva.CANCELADA)
        with self.assertRaises(EstadoReservaInvalidoError):
            reserva.cancelar("Segundo intento")

    def test_05_procesamiento_y_bloqueo_anulacion_posterior(self):
        reserva = Reserva("RES-004", self.cliente_normal, self.servicio,
                          _fecha_futura(4, "16:00"))
        with self.assertRaises(EstadoReservaInvalidoError):
            reserva.procesar()
        reserva.confirmar()
        reserva.procesar()
        self.assertEqual(reserva.estado, EstadoReserva.PROCESADA)
        with self.assertRaises(OperacionNoPermitidaError):
            reserva.cancelar("Intento tardio")


if __name__ == "__main__":
    unittest.main()
