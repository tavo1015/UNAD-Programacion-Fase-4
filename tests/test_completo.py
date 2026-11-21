# Universidad Nacional Abierta y a Distancia - UNAD
# Curso: Programacion (Codigo: 213023)
# Fase 4 - Practicas Simuladas (Software FJ)
# Modulo: Suite de Pruebas Automatizadas de Verificacion Integral

import os
import sys
import py_compile
import unittest

RAIZ_PROYECTO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ_PROYECTO not in sys.path:
    sys.path.insert(0, RAIZ_PROYECTO)

from core.exceptions import (
    SoftwareFJError,
    ClienteInvalidoError,
    ClienteDuplicadoError,
    ParametroInvalidoError,
    EstadoReservaInvalidoError,
    ReservaError
)
from core.logger import ARCHIVO_LOG
from models.cliente import Cliente
from models.servicios import ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from models.reserva import Reserva, EstadoReserva
from models.gestor import GestorSistema
from tests.simulador import ejecutar_simulacion_pasos
from gui.interfaz import InterfazSoftwareFJ


class TestSistemaSoftwareFJ(unittest.TestCase):
    """Pruebas unitarias de sintaxis, modelos, excepciones, simulacion y GUI."""

    def test_01_compilacion_sintaxis(self):
        """Verifica que todos los archivos .py del proyecto compilen sin errores."""
        archivos = [
            os.path.join(RAIZ_PROYECTO, "main.py"),
            os.path.join(RAIZ_PROYECTO, "core", "base.py"),
            os.path.join(RAIZ_PROYECTO, "core", "exceptions.py"),
            os.path.join(RAIZ_PROYECTO, "core", "logger.py"),
            os.path.join(RAIZ_PROYECTO, "models", "cliente.py"),
            os.path.join(RAIZ_PROYECTO, "models", "servicios.py"),
            os.path.join(RAIZ_PROYECTO, "models", "reserva.py"),
            os.path.join(RAIZ_PROYECTO, "models", "gestor.py"),
            os.path.join(RAIZ_PROYECTO, "tests", "simulador.py"),
            os.path.join(RAIZ_PROYECTO, "gui", "__init__.py"),
            os.path.join(RAIZ_PROYECTO, "gui", "interfaz.py"),
        ]
        for ruta in archivos:
            self.assertTrue(os.path.exists(ruta), f"El archivo no existe: {ruta}")
            py_compile.compile(ruta, doraise=True)

    def test_02_simulacion_10_operaciones(self):
        """Verifica que la simulacion ejecute 10 operaciones: 6 exitosas y 4 controladas."""
        gestor = GestorSistema()
        balance, historial = ejecutar_simulacion_pasos(gestor=gestor)
        self.assertEqual(balance["total_operaciones"], 10)
        self.assertEqual(balance["exitosas"], 6)
        self.assertEqual(balance["excepciones_controladas"], 4)
        self.assertEqual(len(historial), 10)

    def test_03_validaciones_cliente(self):
        """Verifica las excepciones de validacion en Cliente."""
        # Email invalido
        with self.assertRaises(ClienteInvalidoError):
            Cliente("1015248901", "Ana Perez", "correo_invalido", "3101234567")

        # Cedula muy corta
        with self.assertRaises(ClienteInvalidoError):
            Cliente("123", "Ana Perez", "ana@empresa.com", "3101234567")

        # Nombre con simbolos
        with self.assertRaises(ClienteInvalidoError):
            Cliente("1015248901", "Ana123!", "ana@empresa.com", "3101234567")

        # Registro valido y duplicado
        gestor = GestorSistema()
        c = Cliente("1015248901", "Carlos Mendoza", "carlos@empresa.com", "3104567890", es_vip=True)
        self.assertTrue(gestor.registrar_cliente(c))
        with self.assertRaises(ClienteDuplicadoError):
            gestor.registrar_cliente(c)

    def test_04_polimorfismo_servicios(self):
        """Verifica el calculo polimorfico en las 3 subclases de Servicio."""
        sala = ReservaSala("SALA-T1", "Sala Test", 50000.0, capacidad_maxima=10, horas=2)
        costo_sala = sala.calcular_costo()
        self.assertGreater(costo_sala, 0)

        # Parametro negativo debe disparar ParametroInvalidoError
        with self.assertRaises(ParametroInvalidoError):
            ReservaSala("SALA-ERR", "Sala Error", 50000.0, capacidad_maxima=10, horas=-2)

        alq = AlquilerEquipo("ALQ-T1", "Laptops Test", 40000.0, "Laptop", dias=2, cantidad=1)
        costo_alq = alq.calcular_costo()
        self.assertGreater(costo_alq, 0)

        ase = AsesoriaEspecializada("ASE-T1", "Asesoria Test", 100000.0, "Cloud", "Junior", horas=3)
        costo_ase = ase.calcular_costo()
        self.assertGreater(costo_ase, 0)

    def test_05_ciclo_vida_reserva_y_excepciones(self):
        """Verifica confirmacion, cancelacion y control de transiciones invalidas."""
        gestor = GestorSistema()
        c = Cliente("1015248901", "Carlos Mendoza", "carlos@empresa.com", "3104567890", es_vip=True)
        s = ReservaSala("SALA-01", "Sala Juntas", 80000.0, capacidad_maxima=10, horas=2)
        gestor.registrar_cliente(c)
        gestor.registrar_servicio(s)

        res = gestor.crear_reserva("RES-T1", "1015248901", "SALA-01", "2026-11-20 10:00")
        self.assertEqual(res.estado, EstadoReserva.PENDIENTE)

        costo = res.confirmar()
        self.assertEqual(res.estado, EstadoReserva.CONFIRMADA)
        self.assertGreater(costo, 0)

        # Confirmar por segunda vez debe fallar con EstadoReservaInvalidoError
        with self.assertRaises(EstadoReservaInvalidoError):
            res.confirmar()

        # Cancelar reserva
        res2 = gestor.crear_reserva("RES-T2", "1015248901", "SALA-01", "2026-11-22 10:00")
        res2.cancelar()
        self.assertEqual(res2.estado, EstadoReserva.CANCELADA)

        # Cancelar de nuevo debe disparar EstadoReservaInvalidoError
        with self.assertRaises(EstadoReservaInvalidoError):
            res2.cancelar()

    def test_06_inicializacion_gui(self):
        """Verifica que la Interfaz Grafica se instancie, renderice y contenga las 3 pestanas."""
        app = InterfazSoftwareFJ()
        app.root.update()
        self.assertEqual(len(app.notebook.tabs()), 3)
        self.assertTrue(os.path.exists(ARCHIVO_LOG))
        app.root.destroy()


if __name__ == "__main__":
    unittest.main()
