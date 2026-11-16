"""Pruebas unitarias del modulo Camilo usando dobles de las dependencias.

Se reemplazan las clases de otros integrantes por versiones compatibles con
las firmas compartidas. Las pruebas integradas se ejecutaran cuando las ramas
servicios, nucleo y cliente se encuentren reunidas.
"""

import importlib.util
import sys
import types
import unittest
from pathlib import Path


def preparar_dependencias():
    nucleo = types.ModuleType("núcleo")
    nucleo.__path__ = []
    base = types.ModuleType("núcleo.base")
    excepciones = types.ModuleType("núcleo.exceptions")
    registro = types.ModuleType("núcleo.logger")
    modelos = types.ModuleType("modelos")
    modelos.__path__ = []
    cliente_mod = types.ModuleType("modelos.cliente")
    servicio_mod = types.ModuleType("modelos.servicios")

    class EntidadBase:
        def __init__(self, id_entidad):
            self._id_entidad = str(id_entidad).strip()

        @property
        def id_entidad(self):
            return self._id_entidad

    class ReservaError(Exception):
        def __init__(self, mensaje, codigo_error="ERR_RESERVA"):
            super().__init__(mensaje)
            self.codigo_error = codigo_error

    class Cliente:
        def __init__(self, vip=False):
            self.nombre = "Cliente de prueba"
            self.cedula = "123456"
            self.es_vip = vip

    class Servicio:
        def __init__(self, nombre="Servicio", horas=None, dias=None, precio=100):
            self.nombre = nombre
            self.precio = precio
            if horas is not None:
                self.horas = horas
            if dias is not None:
                self.dias = dias

        def calcular_costo(self, impuesto=0.19):
            unidades = getattr(self, "horas", getattr(self, "dias", 1))
            return self.precio * unidades * (1 + impuesto)

    eventos = []
    base.EntidadBase = EntidadBase
    excepciones.ReservaError = ReservaError
    registro.registrar_info = lambda msg: eventos.append(("INFO", msg))
    registro.registrar_advertencia = lambda msg: eventos.append(("WARN", msg))
    registro.registrar_error = lambda msg, err=None: eventos.append(("ERROR", msg))
    cliente_mod.Cliente = Cliente
    servicio_mod.Servicio = Servicio
    for nombre, modulo in (
        ("núcleo", nucleo), ("núcleo.base", base),
        ("núcleo.exceptions", excepciones), ("núcleo.logger", registro),
        ("modelos", modelos), ("modelos.cliente", cliente_mod),
        ("modelos.servicios", servicio_mod),
    ):
        sys.modules[nombre] = modulo
    return Cliente, Servicio, ReservaError, eventos


Cliente, Servicio, ReservaError, eventos = preparar_dependencias()
archivo = Path(__file__).resolve().parent.parent / "modelos" / "reserva.py"
if not archivo.is_file():
    # Permite ejecutar el test recibido como archivo suelto junto a reserva.py.
    archivo = Path(__file__).with_name("reserva.py")
spec = importlib.util.spec_from_file_location("reserva_bajo_prueba", archivo)
reserva_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reserva_mod)


class TestReserva(unittest.TestCase):
    def crear(self, *, servicio=None, cliente=None, duracion=None, fecha="2026-11-20"):
        return reserva_mod.Reserva(
            "R-001", cliente or Cliente(),
            servicio or Servicio("Sala", horas=2), fecha, duracion=duracion,
        )

    def test_creacion_toma_horas_del_servicio(self):
        reserva = self.crear()
        self.assertEqual(reserva.duracion, 2)
        self.assertEqual(reserva.estado, reserva_mod.EstadoReserva.PENDIENTE)

    def test_creacion_toma_dias_del_servicio(self):
        reserva = self.crear(servicio=Servicio("Equipo", dias=3))
        self.assertEqual(reserva.duracion, 3)

    def test_rechaza_duracion_distinta_del_servicio(self):
        with self.assertRaises(ReservaError):
            self.crear(duracion=3)

    def test_rechaza_duracion_invalida(self):
        for duracion in (0, -1, True, "2", float("nan"), float("inf")):
            with self.subTest(duracion=duracion):
                with self.assertRaises(ReservaError):
                    self.crear(duracion=duracion)

    def test_confirmacion_incluye_iva(self):
        reserva = self.crear()
        self.assertAlmostEqual(reserva.confirmar(), 238.0)
        self.assertEqual(reserva.estado, reserva_mod.EstadoReserva.CONFIRMADA)

    def test_descuento_adicional(self):
        self.assertAlmostEqual(self.crear().confirmar(0.20), 190.40)

    def test_descuento_vip(self):
        self.assertAlmostEqual(self.crear(cliente=Cliente(True)).confirmar(0.15), 178.50)

    def test_descuento_excesivo(self):
        reserva = self.crear(cliente=Cliente(True))
        with self.assertRaises(ReservaError):
            reserva.confirmar(0.95)
        self.assertEqual(reserva.estado, reserva_mod.EstadoReserva.PENDIENTE)

    def test_impuesto_invalido(self):
        reserva = self.crear()
        with self.assertRaises(ReservaError):
            reserva.confirmar(impuesto=-0.3)

    def test_no_confirmar_dos_veces(self):
        reserva = self.crear()
        reserva.confirmar()
        with self.assertRaises(ReservaError):
            reserva.confirmar()

    def test_no_confirmar_procesada(self):
        reserva = self.crear()
        reserva.confirmar()
        reserva.procesar()
        with self.assertRaises(ReservaError):
            reserva.confirmar()

    def test_cancelar_reserva_pendiente(self):
        reserva = self.crear()
        reserva.cancelar("Solicitud")
        self.assertEqual(reserva.estado, reserva_mod.EstadoReserva.CANCELADA)

    def test_no_confirmar_cancelada(self):
        reserva = self.crear()
        reserva.cancelar()
        with self.assertRaises(ReservaError):
            reserva.confirmar()

    def test_no_cancelar_procesada(self):
        reserva = self.crear()
        reserva.confirmar()
        reserva.procesar()
        with self.assertRaises(ReservaError):
            reserva.cancelar()

    def test_no_procesar_pendiente(self):
        with self.assertRaises(ReservaError):
            self.crear().procesar()

    def test_proceso_completo(self):
        reserva = self.crear()
        reserva.confirmar()
        reserva.procesar()
        self.assertEqual(reserva.estado, reserva_mod.EstadoReserva.PROCESADA)
        self.assertEqual(reserva.obtener_detalle()["duracion"], 2)

    def test_fecha_invalida(self):
        with self.assertRaises(ReservaError):
            self.crear(fecha="2026-02-30")

    def test_costo_negativo_no_confirma(self):
        servicio = Servicio("Sala", horas=2)
        servicio.calcular_costo = lambda impuesto=0.19: -5
        reserva = self.crear(servicio=servicio)
        with self.assertRaises(ReservaError):
            reserva.confirmar()
        self.assertEqual(reserva.estado, reserva_mod.EstadoReserva.PENDIENTE)

    def test_error_costo_encadenado(self):
        servicio = Servicio("Sala", horas=2)
        servicio.calcular_costo = lambda impuesto=0.19: 1 / 0
        reserva = self.crear(servicio=servicio)
        with self.assertRaises(ReservaError) as ctx:
            reserva.confirmar()
        self.assertIsInstance(ctx.exception.__cause__, ZeroDivisionError)
        self.assertEqual(reserva.estado, reserva_mod.EstadoReserva.PENDIENTE)

    def test_registra_auditoria_finally(self):
        eventos.clear()
        self.crear().confirmar()
        self.assertTrue(any("AUDITORIA" in mensaje for _, mensaje in eventos))


if __name__ == "__main__":
    unittest.main(verbosity=2)
