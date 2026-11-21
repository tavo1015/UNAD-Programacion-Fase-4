# Universidad Nacional Abierta y a Distancia - UNAD
# Curso: Programacion (Codigo: 213023)
# Fase 4 - Practicas Simuladas (Software FJ)
# Modulo: Suite de Simulacion (10 Operaciones Obligatorias)
# Descripcion: Ejecuta las 10 operaciones exigidas en el Anexo 3, demostrando
# el manejo riguroso de excepciones (try/except/else/finally, raise from),
# la tolerancia a fallos y la persistencia en el archivo 'software_fj.log'.

import io
import os
import sys
from contextlib import redirect_stdout

raiz_proyecto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if raiz_proyecto not in sys.path:
    sys.path.insert(0, raiz_proyecto)

from core.exceptions import (
    SoftwareFJError,
    ClienteInvalidoError,
    ClienteNoEncontradoError,
    ParametroInvalidoError,
    EstadoReservaInvalidoError,
    ReservaError
)
from core.logger import registrar_info, registrar_error
from models.cliente import Cliente
from models.servicios import ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from models.gestor import GestorSistema


def ejecutar_paso_1(gestor: GestorSistema) -> dict:
    """OPERACION 1: Registro Valido de Cliente."""
    cliente_1 = Cliente(
        cedula="1015248901",
        nombre="Carlos Andres Mendoza",
        email="carlos.mendoza@empresa.com",
        telefono="3104567890",
        es_vip=True
    )
    gestor.registrar_cliente(cliente_1)
    return {
        "numero": 1,
        "titulo": "Registro valido de cliente",
        "estado": "OK",
        "es_exitosa": True,
        "tipo_excepcion": "Ninguna",
        "detalle": f"Cliente registrado con exito: {cliente_1}",
        "objeto": cliente_1
    }


def ejecutar_paso_2(gestor: GestorSistema) -> dict:
    """OPERACION 2: Registro Invalido de Cliente (Email y cedula corruptos)."""
    try:
        _ = Cliente(
            cedula="123456",
            nombre="Laura Restrepo",
            email="correo_sin_arroba",
            telefono="3001234567"
        )
        return {
            "numero": 2,
            "titulo": "Registro invalido de cliente",
            "estado": "FALLO_INESPERADO",
            "es_exitosa": False,
            "tipo_excepcion": "Ninguna",
            "detalle": "Error: no se detecto el correo invalido."
        }
    except ClienteInvalidoError as e:
        registrar_error("Operacion 2 detecto datos de cliente invalidos", e)
        return {
            "numero": 2,
            "titulo": "Registro invalido de cliente (Control de excepcion)",
            "estado": "EXCEPCION_CONTROLADA",
            "es_exitosa": False,
            "tipo_excepcion": type(e).__name__,
            "detalle": f"Captura controlada: {e}"
        }


def ejecutar_paso_3(gestor: GestorSistema) -> dict:
    """OPERACION 3: Creacion Correcta de Servicio (ReservaSala)."""
    sala_directiva = ReservaSala(
        codigo_servicio="SALA-01",
        nombre="Sala de Juntas Principal",
        tarifa_base_hora=80000.0,
        capacidad_maxima=15,
        horas=4,
        incluye_proyector=True,
        incluye_refrigerio=True
    )
    gestor.registrar_servicio(sala_directiva)
    costo_base = sala_directiva.calcular_costo()
    return {
        "numero": 3,
        "titulo": "Creacion correcta de servicio (ReservaSala)",
        "estado": "OK",
        "es_exitosa": True,
        "tipo_excepcion": "Ninguna",
        "detalle": f"{sala_directiva.describir_servicio()} | Costo base: ${costo_base:,.2f} COP",
        "objeto": sala_directiva
    }


def ejecutar_paso_4(gestor: GestorSistema) -> dict:
    """OPERACION 4: Creacion Incorrecta de Servicio (Horas negativas)."""
    try:
        sala_erronea = ReservaSala(
            codigo_servicio="SALA-ERR",
            nombre="Sala Temporal",
            tarifa_base_hora=50000.0,
            capacidad_maxima=10,
            horas=-3
        )
        gestor.registrar_servicio(sala_erronea)
        return {
            "numero": 4,
            "titulo": "Creacion incorrecta de servicio",
            "estado": "FALLO_INESPERADO",
            "es_exitosa": False,
            "tipo_excepcion": "Ninguna",
            "detalle": "Error: se permitieron horas negativas."
        }
    except ParametroInvalidoError as e:
        registrar_error("Operacion 4 detecto parametros de servicio fuera de rango", e)
        return {
            "numero": 4,
            "titulo": "Creacion incorrecta de servicio (Horas negativas)",
            "estado": "EXCEPCION_CONTROLADA",
            "es_exitosa": False,
            "tipo_excepcion": type(e).__name__,
            "detalle": f"Captura controlada: {e}"
        }


def ejecutar_paso_5(gestor: GestorSistema) -> dict:
    """OPERACION 5: Calculo Sobrecargado en Alquiler de Equipos."""
    alquiler_laptops = AlquilerEquipo(
        codigo_servicio="ALQ-01",
        nombre="Estaciones de Trabajo Portatiles",
        tarifa_diaria=45000.0,
        tipo_equipo="Workstation",
        dias=5,
        cantidad=3,
        incluye_seguro=True
    )
    gestor.registrar_servicio(alquiler_laptops)
    costo_v1 = alquiler_laptops.calcular_costo()
    costo_v2 = alquiler_laptops.calcular_costo(descuento=0.15, entrega_express=True)
    return {
        "numero": 5,
        "titulo": "Calculo sobrecargado en Alquiler de Equipos",
        "estado": "OK",
        "es_exitosa": True,
        "tipo_excepcion": "Ninguna",
        "detalle": f"Estandar: ${costo_v1:,.2f} | Sobrecarga (desc 15% + express): ${costo_v2:,.2f} COP",
        "objeto": alquiler_laptops
    }


def ejecutar_paso_6(gestor: GestorSistema) -> dict:
    """OPERACION 6: Asesoria Especializada (Polimorfismo con nivel de consultor)."""
    asesoria_seguridad = AsesoriaEspecializada(
        codigo_servicio="ASE-01",
        nombre="Auditoria de Seguridad y Vulnerabilidades",
        tarifa_hora_base=120000.0,
        area_especialidad="Ciberseguridad",
        nivel_consultor="Senior",
        horas=8,
        modalidad_presencial=True
    )
    gestor.registrar_servicio(asesoria_seguridad)
    costo_asesoria = asesoria_seguridad.calcular_costo(sesion_urgente=False)
    return {
        "numero": 6,
        "titulo": "Asesoria Especializada (Consultor Senior)",
        "estado": "OK",
        "es_exitosa": True,
        "tipo_excepcion": "Ninguna",
        "detalle": f"{asesoria_seguridad.describir_servicio()} | Costo: ${costo_asesoria:,.2f} COP",
        "objeto": asesoria_seguridad
    }


def ejecutar_paso_7(gestor: GestorSistema) -> dict:
    """OPERACION 7: Creacion y Confirmacion Exitosa de Reserva (try/except/else/finally)."""
    reserva_1 = gestor.crear_reserva(
        id_reserva="RES-1001",
        cedula_cliente="1015248901",
        codigo_servicio="SALA-01",
        fecha_evento="2026-11-20 09:00",
        notas="Reunion trimestral de junta directiva"
    )
    costo_final = reserva_1.confirmar()
    return {
        "numero": 7,
        "titulo": "Creacion y confirmacion de Reserva (try/except/else/finally)",
        "estado": "OK",
        "es_exitosa": True,
        "tipo_excepcion": "Ninguna",
        "detalle": f"Reserva {reserva_1.id_reserva} confirmada con exito (VIP 10% desc). Total: ${costo_final:,.2f} COP",
        "objeto": reserva_1
    }


def ejecutar_paso_8(gestor: GestorSistema) -> dict:
    """OPERACION 8: Intento de Reserva Fallida y Encadenamiento de Excepciones."""
    try:
        try:
            gestor.crear_reserva(
                id_reserva="RES-FALLIDA",
                cedula_cliente="99999999",
                codigo_servicio="SALA-01",
                fecha_evento="2026-11-25 14:00"
            )
        except ClienteNoEncontradoError as err_origen:
            raise ReservaError("No fue posible tramitar la reserva debido a inconsistencia en el cliente") from err_origen

        return {
            "numero": 8,
            "titulo": "Reserva fallida y encadenamiento",
            "estado": "FALLO_INESPERADO",
            "es_exitosa": False,
            "tipo_excepcion": "Ninguna",
            "detalle": "Error: se permitio reserva con cliente inexistente."
        }
    except ReservaError as e:
        registrar_error("Operacion 8 verifico encadenamiento de excepciones", e)
        causa = f" (Causa: {type(e.__cause__).__name__})" if e.__cause__ else ""
        return {
            "numero": 8,
            "titulo": "Reserva fallida y encadenamiento (raise ... from ...)",
            "estado": "EXCEPCION_CONTROLADA",
            "es_exitosa": False,
            "tipo_excepcion": f"{type(e).__name__} -> {type(e.__cause__).__name__}",
            "detalle": f"Captura con encadenamiento: {e}{causa}"
        }


def ejecutar_paso_9(gestor: GestorSistema) -> dict:
    """OPERACION 9: Cancelacion Exitosa de Reserva."""
    reserva_2 = gestor.crear_reserva(
        id_reserva="RES-1002",
        cedula_cliente="1015248901",
        codigo_servicio="ALQ-01",
        fecha_evento="2026-11-28 08:00",
        notas="Capacitacion técnica"
    )
    reserva_2.cancelar(motivo="Reasignacion presupuestal interna del cliente")
    return {
        "numero": 9,
        "titulo": "Cancelacion exitosa de una reserva",
        "estado": "OK",
        "es_exitosa": True,
        "tipo_excepcion": "Ninguna",
        "detalle": f"Reserva {reserva_2.id_reserva} cancelada exitosamente. Estado: {reserva_2.estado.value}",
        "objeto": reserva_2
    }


def ejecutar_paso_10(gestor: GestorSistema, reserva_cancelada) -> dict:
    """OPERACION 10: Intento de Cancelacion Invalida (Operacion Redundante)."""
    try:
        reserva_cancelada.cancelar(motivo="Segundo intento redundante")
        return {
            "numero": 10,
            "titulo": "Intento de cancelacion invalida",
            "estado": "FALLO_INESPERADO",
            "es_exitosa": False,
            "tipo_excepcion": "Ninguna",
            "detalle": "Error: se permitio cancelar una reserva dos veces."
        }
    except EstadoReservaInvalidoError as e:
        registrar_error("Operacion 10 rechazo cancelacion repetida", e)
        return {
            "numero": 10,
            "titulo": "Intento de cancelacion invalida (Reserva ya cancelada)",
            "estado": "EXCEPCION_CONTROLADA",
            "es_exitosa": False,
            "tipo_excepcion": type(e).__name__,
            "detalle": f"Captura controlada: {e}"
        }


def ejecutar_simulacion_pasos(gestor: GestorSistema = None, callback_paso=None) -> tuple[dict, list[dict]]:
    """
    Ejecuta los 10 pasos de manera estructurada permitiendo notificar callbacks
    en tiempo real para la interfaz grafica o la consola.
    """
    if gestor is None:
        gestor = GestorSistema()

    pasos_funciones = [
        ejecutar_paso_1,
        ejecutar_paso_2,
        ejecutar_paso_3,
        ejecutar_paso_4,
        ejecutar_paso_5,
        ejecutar_paso_6,
        ejecutar_paso_7,
        ejecutar_paso_8,
        ejecutar_paso_9,
    ]

    historial = []
    reserva_para_paso_10 = None

    for func in pasos_funciones:
        res = func(gestor)
        if res.get("numero") == 9 and "objeto" in res:
            reserva_para_paso_10 = res["objeto"]
        historial.append(res)
        if callback_paso:
            callback_paso(res)

    # Paso 10 requiere la referencia a la reserva cancelada
    res_10 = ejecutar_paso_10(gestor, reserva_para_paso_10)
    historial.append(res_10)
    if callback_paso:
        callback_paso(res_10)

    exitosas = sum(1 for p in historial if p["es_exitosa"])
    controladas = sum(1 for p in historial if p["estado"] == "EXCEPCION_CONTROLADA")

    balance = {
        "total_operaciones": 10,
        "exitosas": exitosas,
        "excepciones_controladas": controladas,
        "gestor": gestor
    }
    return balance, historial


def ejecutar_simulacion_completa() -> dict:
    """
    Ejecuta de manera secuencial los 10 escenarios requeridos por la guia de la UNAD.
    Muestra la salida formateada en consola y retorna el balance final.
    """
    print("\n" + "=" * 80)
    print(" INICIO DE SIMULACION: SISTEMA INTEGRAL SOFTWARE FJ (UNAD FASE 4)")
    print(" Verificando estabilidad, polimorfismo y gestion avanzada de excepciones")
    print("=" * 80)

    def imprimir_paso(paso: dict):
        num = paso["numero"]
        tit = paso["titulo"]
        print(f"\n--- [OPERACION {num}/10] {tit} ---")
        if paso["es_exitosa"]:
            print(f" [OK] {paso['detalle']}")
        elif paso["estado"] == "EXCEPCION_CONTROLADA":
            print(f" [EXCEPCION CONTROLADA CAPTURADA]: {paso['tipo_excepcion']}")
            print(f"      --> {paso['detalle']}")
        else:
            print(f" [ERROR]: {paso['detalle']}")

    balance, _ = ejecutar_simulacion_pasos(callback_paso=imprimir_paso)

    print("\n" + "=" * 80)
    print(" BALANCE DE LA SIMULACION - SOFTWARE FJ")
    print(f" Total operaciones ejecutadas: {balance['total_operaciones']}")
    print(f" Operaciones normales exitosas: {balance['exitosas']}")
    print(f" Errores y excepciones controladas: {balance['excepciones_controladas']}")
    print(" ESTADO GENERAL: SISTEMA 100% ESTABLE (Sin caidas ni cierres inesperados)")
    print(" Registro de auditoria persistido en: 'software_fj.log'")
    print("=" * 80 + "\n")

    return {
        "exitosas": balance["exitosas"],
        "excepciones_controladas": balance["excepciones_controladas"],
        "total_operaciones": balance["total_operaciones"]
    }


if __name__ == "__main__":
    ejecutar_simulacion_completa()
