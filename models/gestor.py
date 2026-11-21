# Universidad Nacional Abierta y a Distancia - UNAD
# Curso: Programacion (Codigo: 213023)
# Fase 4 - Practicas Simuladas (Software FJ)
# Modulo: Gestor del Sistema (Persistencia en Memoria)
# Descripcion: Administra colecciones en memoria de clientes, servicios y reservas
# sin utilizar bases de datos, cumpliendo la condicion estricta del Anexo 3.

from core.exceptions import (
    ClienteNoEncontradoError,
    ClienteDuplicadoError,
    ServicioInvalidoError,
    ReservaError
)
from core.logger import registrar_info, registrar_advertencia, registrar_error
from models.cliente import Cliente
from models.servicios import Servicio
from models.reserva import Reserva


class GestorSistema:
    """
    Controlador central de Software FJ. Gestiona todas las listas internas
    de entidades en memoria RAM (sin base de datos) y orquesta las operaciones
    de negocio capturando y registrando cualquier anomalia.
    """

    def __init__(self):
        # Listas internas en memoria para cumplir la restriccion 'sin bases de datos'
        self._clientes: list[Cliente] = []
        self._servicios: list[Servicio] = []
        self._reservas: list[Reserva] = []
        registrar_info("Gestor de Software FJ inicializado en memoria operativa.")

    # -------------------------------------------------------------------------
    # PROPIEDADES DE ACCESO A COLECCIONES
    # -------------------------------------------------------------------------
    @property
    def clientes(self) -> list[Cliente]:
        """Retorna una copia superficial de la lista de clientes registrados."""
        return list(self._clientes)

    @property
    def servicios(self) -> list[Servicio]:
        """Retorna una copia superficial de la lista de servicios en catalogo."""
        return list(self._servicios)

    @property
    def reservas(self) -> list[Reserva]:
        """Retorna una copia superficial de la lista de reservas registradas."""
        return list(self._reservas)

    # -------------------------------------------------------------------------
    # GESTION DE CLIENTES
    # -------------------------------------------------------------------------
    def registrar_cliente(self, cliente: Cliente) -> bool:
        """Registra un cliente validando que no exista duplicidad de cedula."""
        if any(c.cedula == cliente.cedula for c in self._clientes):
            raise ClienteDuplicadoError(
                f"El cliente con cedula {cliente.cedula} ya se encuentra registrado en el sistema."
            )
        self._clientes.append(cliente)
        return True

    def buscar_cliente(self, cedula: str) -> Cliente:
        """Busca un cliente por su documento de identidad. Lanza excepcion si no existe."""
        for c in self._clientes:
            if c.cedula == str(cedula).strip():
                return c
        raise ClienteNoEncontradoError(f"No existe ningun cliente registrado con cedula '{cedula}'.")

    # -------------------------------------------------------------------------
    # GESTION DE SERVICIOS
    # -------------------------------------------------------------------------
    def registrar_servicio(self, servicio: Servicio) -> bool:
        """Agrega un servicio al catalogo activo de Software FJ."""
        if any(s.codigo_servicio == servicio.codigo_servicio for s in self._servicios):
            raise ServicioInvalidoError(
                f"Ya existe un servicio catalogado con el codigo '{servicio.codigo_servicio}'."
            )
        self._servicios.append(servicio)
        return True

    def buscar_servicio(self, codigo_servicio: str) -> Servicio:
        """Busca un servicio por su codigo unico."""
        codigo = str(codigo_servicio).strip().upper()
        for s in self._servicios:
            if s.codigo_servicio == codigo:
                return s
        raise ServicioInvalidoError(f"El servicio con codigo '{codigo_servicio}' no fue encontrado en catalogo.")

    # -------------------------------------------------------------------------
    # GESTION DE RESERVAS
    # -------------------------------------------------------------------------
    def crear_reserva(self, id_reserva: str, cedula_cliente: str,
                      codigo_servicio: str, fecha_evento: str, notas: str = "") -> Reserva:
        """
        Crea e incorpora una nueva reserva asociando el cliente y el servicio buscados.
        Demuestra la busqueda y vinculacion de objetos en listas.
        """
        cliente = self.buscar_cliente(cedula_cliente)
        servicio = self.buscar_servicio(codigo_servicio)

        # Validacion de id unico de reserva
        if any(r.id_reserva == str(id_reserva).strip() for r in self._reservas):
            raise ReservaError(f"El codigo de reserva '{id_reserva}' ya esta en uso.")

        nueva_reserva = Reserva(
            id_reserva=id_reserva,
            cliente=cliente,
            servicio=servicio,
            fecha_evento=fecha_evento,
            notas=notas
        )
        self._reservas.append(nueva_reserva)
        return nueva_reserva

    def buscar_reserva(self, id_reserva: str) -> Reserva:
        """Busca una reserva en memoria por su ID."""
        id_limpio = str(id_reserva).strip()
        for r in self._reservas:
            if r.id_reserva == id_limpio:
                return r
        raise ReservaError(f"No se encontro ninguna reserva con identificador '{id_reserva}'.")

    # -------------------------------------------------------------------------
    # CONSULTAS GENERALES
    # -------------------------------------------------------------------------
    def obtener_resumen_estadisticas(self) -> dict:
        """Retorna contadores de la operacion actual en memoria."""
        return {
            "total_clientes": len(self._clientes),
            "total_servicios": len(self._servicios),
            "total_reservas": len(self._reservas)
        }
