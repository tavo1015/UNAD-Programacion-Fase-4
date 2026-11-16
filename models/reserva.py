# Universidad Nacional Abierta y a Distancia - UNAD
# Curso: Programacion (Codigo: 213023)
# Fase 4 - Software FJ | Desarrollador 4: Camilo
# Modulo: Gestion de Reservas y Logica de Negocio

"""Reservas compatibles con la interfaz actual de modelos.servicios.

Dependencias previstas al integrar las ramas del equipo:
- nucleo.base.EntidadBase
- nucleo.exceptions.ReservaError
- nucleo.logger.registrar_info/registrar_advertencia/registrar_error
- modelos.cliente.Cliente (aun pendiente de entregar)
- modelos.servicios.Servicio

El servicio calcula el IVA y los recargos; la reserva aplica despues los
 descuentos comerciales sobre ese total. Este orden debe ser acordado por
 el equipo si la regla de facturacion cambia.
"""

from datetime import datetime
from enum import Enum
from math import isfinite

from núcleo.base import EntidadBase
from núcleo.exceptions import ReservaError
from núcleo.logger import registrar_info, registrar_advertencia, registrar_error
from modelos.cliente import Cliente
from modelos.servicios import Servicio


class EstadoReserva(Enum):
    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"
    PROCESADA = "PROCESADA"


class Reserva(EntidadBase):
    """Asocia un cliente y un servicio y controla el ciclo de su reserva.

    La duracion se expresa en horas para ReservaSala y en dias para
    AlquilerEquipo. Si se omite, toma `servicio.horas` o `servicio.dias`.
    Si se especifica para estos servicios, debe coincidir con el valor del
    servicio para impedir facturar un periodo distinto al contratado.
    """

    def __init__(self, id_reserva: str, cliente: Cliente, servicio: Servicio,
                 fecha_evento: str, notas: str = "", *, duracion=None):
        try:
            if not isinstance(id_reserva, str) or not id_reserva.strip():
                raise ReservaError("El identificador de reserva debe ser texto no vacio.")
            if not isinstance(cliente, Cliente):
                raise ReservaError("El cliente debe ser una instancia valida de Cliente.")
            if not isinstance(servicio, Servicio):
                raise ReservaError("El servicio debe ser una instancia valida de Servicio.")
            fecha = self._validar_fecha_evento(fecha_evento)
            unidades = self._determinar_duracion(servicio, duracion)
            if notas is not None and not isinstance(notas, str):
                raise ReservaError("Las notas deben ser texto o None.")
        except ReservaError as error:
            registrar_error(f"Creacion de reserva [{id_reserva}] rechazada", error)
            raise
        else:
            super().__init__(id_entidad=id_reserva.strip())
            self._cliente = cliente
            self._servicio = servicio
            self._fecha_evento = fecha
            self._duracion = unidades
            self._notas = (notas or "").strip()
            self._estado = EstadoReserva.PENDIENTE
            self._costo_total = 0.0
            registrar_info(f"Reserva [{self.id_reserva}] creada en estado PENDIENTE.")

    @staticmethod
    def _numero_positivo(valor, descripcion):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ReservaError(f"{descripcion} debe ser un numero positivo.")
        numero = float(valor)
        if not isfinite(numero) or numero <= 0:
            raise ReservaError(f"{descripcion} debe ser finito y mayor que cero.")
        return numero

    @classmethod
    def _determinar_duracion(cls, servicio, duracion):
        """Impide divergencias entre duracion de Reserva y horas/dias de Servicio."""
        duracion_servicio = None
        for campo in ("horas", "dias"):
            if hasattr(servicio, campo):
                duracion_servicio = cls._numero_positivo(
                    getattr(servicio, campo), f"La duracion del servicio ({campo})"
                )
                break
        if duracion is None:
            if duracion_servicio is None:
                raise ReservaError(
                    "Debe indicar duracion si el servicio no contiene horas o dias."
                )
            return duracion_servicio
        duracion = cls._numero_positivo(duracion, "La duracion de la reserva")
        if duracion_servicio is not None and duracion != duracion_servicio:
            raise ReservaError(
                "La duracion de la reserva debe coincidir con las horas/dias "
                "definidas en el servicio."
            )
        return duracion

    @staticmethod
    def _validar_descuento(valor):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ReservaError("El descuento debe ser un numero entre 0 y 1.")
        valor = float(valor)
        if not isfinite(valor) or not 0 <= valor <= 1:
            raise ReservaError("El descuento debe estar entre 0 y 1.")
        return valor

    @staticmethod
    def _validar_fecha_evento(fecha_str):
        if not isinstance(fecha_str, str) or not fecha_str.strip():
            raise ReservaError("La fecha del evento es obligatoria y debe ser texto.")
        for formato in ("%Y-%m-%d %H:%M", "%Y-%m-%d", "%d/%m/%Y %H:%M", "%d/%m/%Y"):
            try:
                fecha = datetime.strptime(fecha_str.strip(), formato)
                break
            except ValueError:
                continue
        else:
            raise ReservaError(f"Fecha invalida: '{fecha_str}'. Ejemplo: 2026-11-20 09:00.")
        # Regla heredada del archivo original, pendiente de aprobacion del equipo.
        if not 2024 <= fecha.year <= 2035:
            raise ReservaError("El año debe estar entre 2024 y 2035.")
        return fecha.strftime("%Y-%m-%d %H:%M")

    @property
    def id_reserva(self):
        return self.id_entidad

    @property
    def cliente(self):
        return self._cliente

    @property
    def servicio(self):
        return self._servicio

    @property
    def estado(self):
        return self._estado

    @property
    def costo_total(self):
        return self._costo_total

    @property
    def fecha_evento(self):
        return self._fecha_evento

    @property
    def duracion(self):
        return self._duracion

    @property
    def notas(self):
        return self._notas

    def confirmar(self, descuento_adicional: float = 0.0, *, impuesto: float = 0.19) -> float:
        """Confirma una reserva pendiente y calcula su total.

        `calcular_costo(impuesto=...)` es la firma REAL de servicios.py.
        El descuento comercial se aplica al importe devuelto por el servicio.
        """
        operacion_exitosa = False
        try:
            if self._estado != EstadoReserva.PENDIENTE:
                raise ReservaError(
                    f"No se puede confirmar reserva en estado {self._estado.value}.",
                    codigo_error="ERR_ESTADO_RESERVA",
                )
            descuento = self._validar_descuento(descuento_adicional)
            vip = self._cliente.es_vip
            if not isinstance(vip, bool):
                raise ReservaError("La propiedad es_vip debe ser booleana.")
            descuento += 0.10 if vip else 0.0
            if descuento > 1:
                raise ReservaError("El descuento total, incluido VIP, supera el 100 %.")
            if isinstance(impuesto, bool) or not isinstance(impuesto, (int, float)):
                raise ReservaError("El impuesto debe ser numerico.")
            impuesto = float(impuesto)
            if not isfinite(impuesto) or not 0 <= impuesto <= 1:
                raise ReservaError("El impuesto debe estar entre 0 y 1.")

            # Duracion ya esta incluida en el calculo del servicio (horas/dias).
            subtotal_con_impuesto = self._servicio.calcular_costo(impuesto=impuesto)
            if isinstance(subtotal_con_impuesto, bool) or not isinstance(
                subtotal_con_impuesto, (int, float)
            ):
                raise ReservaError("El servicio devolvio un costo no numerico.")
            subtotal_con_impuesto = float(subtotal_con_impuesto)
            if not isfinite(subtotal_con_impuesto) or subtotal_con_impuesto < 0:
                raise ReservaError("El servicio devolvio un costo invalido.")
            costo = round(subtotal_con_impuesto * (1 - descuento), 2)
            self._costo_total = costo
            self._estado = EstadoReserva.CONFIRMADA
            operacion_exitosa = True
        except ReservaError as error:
            registrar_error(f"Fallo al confirmar reserva [{self.id_reserva}]", error)
            raise
        except Exception as error:
            registrar_error(f"Error calculando reserva [{self.id_reserva}]", error)
            raise ReservaError(
                "No fue posible calcular el costo de la reserva.",
                codigo_error="ERR_RESERVA_COSTO",
            ) from error
        else:
            registrar_info(
                f"Reserva [{self.id_reserva}] CONFIRMADA. Total: ${self._costo_total:,.2f}"
            )
            return self._costo_total
        finally:
            registrar_info(
                f"[AUDITORIA] Confirmacion [{self.id_reserva}]: "
                f"{'EXITOSA' if operacion_exitosa else 'FALLIDA'}"
            )

    def cancelar(self, motivo: str = "Solicitud del cliente") -> None:
        """Permite cancelar reservas pendientes o confirmadas."""
        try:
            if self._estado in (EstadoReserva.CANCELADA, EstadoReserva.PROCESADA):
                raise ReservaError(
                    f"No se puede cancelar reserva en estado {self._estado.value}.",
                    codigo_error="ERR_ESTADO_RESERVA",
                )
            if not isinstance(motivo, str) or not motivo.strip():
                raise ReservaError("El motivo de cancelacion debe ser texto no vacio.")
            self._estado = EstadoReserva.CANCELADA
            registrar_advertencia(
                f"Reserva [{self.id_reserva}] CANCELADA. Motivo: {motivo.strip()}"
            )
        except ReservaError as error:
            registrar_error(f"Fallo al cancelar [{self.id_reserva}]", error)
            raise

    def procesar(self) -> None:
        """Solo permite procesar una reserva confirmada."""
        if self._estado != EstadoReserva.CONFIRMADA:
            error = ReservaError(
                f"No se puede procesar reserva en estado {self._estado.value}.",
                codigo_error="ERR_ESTADO_RESERVA",
            )
            registrar_error(f"Fallo al procesar [{self.id_reserva}]", error)
            raise error
        self._estado = EstadoReserva.PROCESADA
        registrar_info(f"Reserva [{self.id_reserva}] PROCESADA.")

    def obtener_detalle(self) -> dict:
        return {
            "id_reserva": self.id_reserva,
            "cliente": self.cliente.nombre,
            "cedula": self.cliente.cedula,
            "servicio": self.servicio.nombre,
            "fecha_evento": self.fecha_evento,
            "duracion": self.duracion,
            "notas": self.notas,
            "estado": self.estado.value,
            "costo_total": self.costo_total,
        }

    def __str__(self) -> str:
        return (
            f"Reserva #{self.id_reserva} | Cliente: {self.cliente.nombre} | "
            f"Servicio: {self.servicio.nombre} | Fecha: {self.fecha_evento} | "
            f"Duracion: {self.duracion:g} | Estado: {self.estado.value} | "
            f"Total: ${self.costo_total:,.2f}"
        )
