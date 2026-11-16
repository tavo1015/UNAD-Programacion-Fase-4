"""Pruebas independientes con dobles de las clases que entrega el equipo."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path


def instalar_simulaciones():
    core = types.ModuleType("core")
    core.__path__ = []
    base = types.ModuleType("core.base")
    exceptions = types.ModuleType("core.exceptions")
    logger = types.ModuleType("core.logger")
    models = types.ModuleType("models")
    models.__path__ = []
    cliente = types.ModuleType("models.cliente")
    servicios = types.ModuleType("models.servicios")

    class EntidadBase:
        def __init__(self, id_entidad):
            self._id_entidad = id_entidad

        @property
        def id_entidad(self):
            return self._id_entidad

    class ReservaError(Exception):
        pass

    class EstadoReservaInvalidoError(ReservaError):
        pass

    class OperacionNoPermitidaError(ReservaError):
        pass

    class Cliente:
        def __init__(self, vip=False):
            self.nombre = "Cliente prueba"
            self.cedula = "12345"
            self.es_vip = vip

    class Servicio:
        nombre = "Sala de prueba"

        def calcular_costo(self, *, duracion, descuento, **kwargs):
            return 100 * duracion * (1 - descuento)

    base.EntidadBase = EntidadBase
    exceptions.ReservaError = ReservaError
    exceptions.EstadoReservaInvalidoError = EstadoReservaInvalidoError
    exceptions.OperacionNoPermitidaError = OperacionNoPermitidaError
    logger.eventos = []
    logger.registrar_info = lambda msg: logger.eventos.append(("info", msg))
    logger.registrar_advertencia = lambda msg: logger.eventos.append(("warning", msg))
    logger.registrar_error = lambda msg, err: logger.eventos.append(("error", msg))
    cliente.Cliente = Cliente
    servicios.Servicio = Servicio
    for nombre, modulo in (
        ("core", core), ("core.base", base), ("core.exceptions", exceptions),
        ("core.logger", logger), ("models", models),
        ("models.cliente", cliente), ("models.servicios", servicios)
    ):
        sys.modules[nombre] = modulo
    return Cliente, Servicio, exceptions, logger


Cliente, Servicio, errores, logger = instalar_simulaciones()
spec = importlib.util.spec_from_file_location("reserva", Path(__file__).with_name("reserva.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class PruebasReserva(unittest.TestCase):
    def crear(self, **kwargs):
        return mod.Reserva("R-1", Cliente(), Servicio(), "2026-11-20 09:00", **kwargs)

    def test_confirmar_y_procesar(self):
        reserva = self.crear(duracion=2)
        self.assertEqual(reserva.confirmar(), 200)
        self.assertEqual(reserva.estado, mod.EstadoReserva.CONFIRMADA)
        reserva.procesar()
        self.assertEqual(reserva.estado, mod.EstadoReserva.PROCESADA)
        self.assertEqual(reserva.obtener_detalle()["duracion"], 2)

    def test_descuento_vip(self):
        reserva = mod.Reserva("R-2", Cliente(True), Servicio(), "2026-11-20", duracion=3)
        self.assertAlmostEqual(reserva.confirmar(0.15), 225)

    def test_descuento_invalido(self):
        reserva = self.crear()
        with self.assertRaises(errores.ReservaError):
            reserva.confirmar(1.1)
        self.assertEqual(reserva.estado, mod.EstadoReserva.PENDIENTE)

    def test_descuento_vip_excesivo(self):
        reserva = mod.Reserva("R-2", Cliente(True), Servicio(), "2026-11-20")
        with self.assertRaises(errores.ReservaError):
            reserva.confirmar(0.95)

    def test_no_confirmar_procesada(self):
        reserva = self.crear()
        reserva.confirmar()
        reserva.procesar()
        with self.assertRaises(errores.EstadoReservaInvalidoError):
            reserva.confirmar()

    def test_no_cancelar_procesada(self):
        reserva = self.crear()
        reserva.confirmar()
        reserva.procesar()
        with self.assertRaises(errores.OperacionNoPermitidaError):
            reserva.cancelar()

    def test_cancelar_pendiente(self):
        reserva = self.crear()
        reserva.cancelar("Sin disponibilidad")
        self.assertEqual(reserva.estado, mod.EstadoReserva.CANCELADA)

    def test_no_confirmar_cancelada(self):
        reserva = self.crear()
        reserva.cancelar()
        with self.assertRaises(errores.EstadoReservaInvalidoError):
            reserva.confirmar()

    def test_duracion_invalida(self):
        for duracion in (0, -2, float("nan"), float("inf"), True, "2"):
            with self.subTest(duracion=duracion):
                with self.assertRaises(errores.ReservaError):
                    self.crear(duracion=duracion)

    def test_fecha_invalida(self):
        with self.assertRaises(errores.ReservaError):
            mod.Reserva("R-3", Cliente(), Servicio(), "2026-02-30")

    def test_procesamiento_sin_confirmar(self):
        with self.assertRaises(errores.EstadoReservaInvalidoError):
            self.crear().procesar()

    def test_costo_invalido_no_altera_estado(self):
        servicio = Servicio()
        servicio.calcular_costo = lambda **kw: -20
        reserva = mod.Reserva("R-5", Cliente(), servicio, "2026-11-20")
        with self.assertRaises(errores.ReservaError):
            reserva.confirmar()
        self.assertEqual(reserva.estado, mod.EstadoReserva.PENDIENTE)

    def test_error_servicio_encadenado(self):
        servicio = Servicio()
        servicio.calcular_costo = lambda **kw: 1 / 0
        reserva = mod.Reserva("R-6", Cliente(), servicio, "2026-11-20")
        with self.assertRaises(errores.ReservaError) as ctx:
            reserva.confirmar()
        self.assertIsInstance(ctx.exception.__cause__, ZeroDivisionError)


if __name__ == "__main__":
    unittest.main(verbosity=2)
