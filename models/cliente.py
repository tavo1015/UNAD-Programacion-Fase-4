# -*- coding: utf-8 -*-
"""
Universidad Nacional Abierta y a Distancia (UNAD)
Escuela de Ciencias Básicas, Tecnología e Ingeniería (ECBTI)
Programa de Ingeniería de Telecomunicaciones
Curso: Programación (Código: 213023) - Grupo: 213023_119
Fase 4: Prácticas Simuladas (Componente Práctico Colaborativo)
Empresa: Software FJ - Sistema Integral de Gestión de Clientes, Servicios y Reservas

Rol: Desarrollador 2 - Módulo Cliente y Validaciones
Estudiante: Cristian Fernando Zapata Marín (C.C. 1128417633)
Usuario GitHub: cristianzm31-zeta

Descripción:
Implementa la clase Cliente con encapsulamiento estricto mediante atributos
privados (doble guion bajo), validaciones sintácticas rigurosas (cédula, nombre,
correo electrónico mediante expresión regular RFC y teléfono) y manejo defensivo
de excepciones personalizadas (ClienteInvalidoError).
=============================================================================
"""

import re
from typing import Any, Dict
from core.base import EntidadBase
from core.exceptions import ClienteInvalidoError
from core.logger import registrar_info, registrar_advertencia, registrar_error


class Cliente(EntidadBase):
    """
    Representa a un cliente registrado en la empresa Software FJ.
    
    Aplica encapsulamiento avanzado protegiendo atributos privados y
    validando tipos y formatos mediante decoradores @property y setters.
    
    Desarrollado y personalizado por Cristian Fernando Zapata Marín.
    """

    # Expresión regular robusta para nombres (letras latinas, tildes, diéresis, ñ y espacios)
    PATRON_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚáéíóúñÑüÜ\s.]+$")

    # Expresión regular para correo electrónico estándar (RFC 5322 compatible)
    PATRON_EMAIL = re.compile(r"^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,6}$")

    def __init__(
        self,
        cedula: str,
        nombre: str,
        email: str,
        telefono: str,
        es_vip: bool = False,
    ) -> None:
        """
        Constructor de la entidad Cliente.
        Inicializa la clase abstracta EntidadBase y aplica validación en cascada.
        """
        cadena_cedula = str(cedula).strip() if cedula is not None else ""
        super().__init__(id_entidad=cadena_cedula)

        # Encapsulamiento estricto: atributos privados (doble guion bajo)
        # atendiendo las recomendaciones pedagógicas de POO en Python
        self.__cedula: str = ""
        self.__nombre: str = ""
        self.__email: str = ""
        self.__telefono: str = ""
        self.__es_vip: bool = False

        # Validación y asignación a través de los setters defensivos
        self.cedula = cedula
        self.nombre = nombre
        self.email = email
        self.telefono = telefono
        self.es_vip = es_vip

        # Registro de auditoría
        categoria = "VIP" if self.__es_vip else "Estándar"
        registrar_info(
            f"Cliente registrado exitosamente: {self.__nombre} (C.C. {self.__cedula}) - Categoría: {categoria}"
        )

    # -------------------------------------------------------------------------
    # PROPIEDAD: CÉDULA (DOCUMENTO DE IDENTIDAD)
    # -------------------------------------------------------------------------
    @property
    def cedula(self) -> str:
        """Retorna el documento de identidad único del cliente."""
        return self.__cedula

    @cedula.setter
    def cedula(self, valor: Any) -> None:
        """
        Valida que la cédula sea numérica y contenga entre 6 y 10 dígitos.
        Lanza ClienteInvalidoError ante datos anómalos.
        """
        if valor is None:
            raise ClienteInvalidoError("La cédula de ciudadanía es obligatoria y no puede ser nula.")

        cadena = str(valor).strip()
        if not cadena.isdigit() or not (6 <= len(cadena) <= 10):
            raise ClienteInvalidoError(
                f"La cedula '{valor}' es invalida. Debe contener unicamente entre 6 y 10 digitos numericos."
            )

        self.__cedula = cadena
        # Sincronizar identificador de la clase base EntidadBase
        self._cedula = cadena
        self._id_entidad = cadena

    # -------------------------------------------------------------------------
    # PROPIEDAD: NOMBRE COMPLETO
    # -------------------------------------------------------------------------
    @property
    def nombre(self) -> str:
        """Retorna el nombre completo del cliente debidamente formateado."""
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: Any) -> None:
        """
        Valida que el nombre tenga al menos 3 caracteres y no contenga dígitos ni símbolos prohibidos.
        Lanza ClienteInvalidoError si no cumple con las restricciones de negocio.
        """
        if valor is None:
            raise ClienteInvalidoError("El nombre del cliente no puede ser nulo.")

        cadena = str(valor).strip()
        if len(cadena) < 3:
            raise ClienteInvalidoError(f"El nombre '{valor}' es muy corto. Minimo 3 caracteres requeridos.")

        # Validación sintáctica con soporte para tildes y caracteres hispanos
        if not self.PATRON_NOMBRE.match(cadena):
            raise ClienteInvalidoError(
                f"El nombre '{valor}' contiene caracteres numericos o simbolos prohibidos."
            )

        self.__nombre = cadena.title()
        self._nombre = self.__nombre

    # -------------------------------------------------------------------------
    # PROPIEDAD: CORREO ELECTRÓNICO
    # -------------------------------------------------------------------------
    @property
    def email(self) -> str:
        """Retorna la dirección de correo electrónico del cliente."""
        return self.__email

    @email.setter
    def email(self, valor: Any) -> None:
        """
        Valida que la dirección de correo cumpla con el estándar de correo electrónico.
        Lanza ClienteInvalidoError ante formatos incorrectos.
        """
        if valor is None:
            raise ClienteInvalidoError("El correo electrónico no puede ser nulo.")

        cadena = str(valor).strip().lower()
        if not self.PATRON_EMAIL.match(cadena):
            raise ClienteInvalidoError(
                f"El formato del correo electronico '{valor}' es invalido. Ejemplo: usuario@dominio.com"
            )

        self.__email = cadena
        self._email = cadena

    # -------------------------------------------------------------------------
    # PROPIEDAD: TELÉFONO DE CONTACTO
    # -------------------------------------------------------------------------
    @property
    def telefono(self) -> str:
        """Retorna el número de teléfono celular o fijo de contacto."""
        return self.__telefono

    @telefono.setter
    def telefono(self, valor: Any) -> None:
        """
        Valida que el teléfono contenga entre 7 y 10 dígitos numéricos
        (cubriendo líneas fijas locales y telefonía móvil celular en Colombia).
        """
        if valor is None:
            raise ClienteInvalidoError("El número telefónico no puede ser nulo.")

        cadena = str(valor).strip().replace(" ", "").replace("-", "")
        if not cadena.isdigit() or not (7 <= len(cadena) <= 10):
            raise ClienteInvalidoError(
                f"El telefono '{valor}' no es valido. Debe tener entre 7 y 10 digitos numericos."
            )

        self.__telefono = cadena
        self._telefono = cadena

    # -------------------------------------------------------------------------
    # PROPIEDAD: BENEFICIARIO / MEMBRESÍA VIP
    # -------------------------------------------------------------------------
    @property
    def es_vip(self) -> bool:
        """Indica si el cliente cuenta con categoría VIP para descuentos adicionales."""
        return self.__es_vip

    @es_vip.setter
    def es_vip(self, valor: Any) -> None:
        """Valida que el valor de membresía VIP sea estrictamente booleano."""
        if not isinstance(valor, bool):
            raise TypeError("El atributo 'es_vip' debe ser un valor booleano.")
        self.__es_vip = valor
        self._es_vip = valor

    # -------------------------------------------------------------------------
    # MÉTODOS DE NEGOCIO Y VALOR AGREGADO (Toque Personal de Cristian Zapata)
    # -------------------------------------------------------------------------
    @property
    def tipo_cliente(self) -> str:
        """Retorna la categoría del cliente en formato legible."""
        return "Cliente VIP" if self.__es_vip else "Cliente Estándar"

    def actualizar_contacto(self, nuevo_email: str, nuevo_telefono: str) -> None:
        """
        Actualiza simultáneamente el correo y teléfono en una transacción atómica.
        Si la validación de alguno falla, se conserva el estado original (rollback).
        """
        email_antiguo = self.__email
        telefono_antiguo = self.__telefono
        try:
            self.email = nuevo_email
            self.telefono = nuevo_telefono
            registrar_info(
                f"Contacto actualizado para {self.__nombre}: Email='{self.__email}', Tel='{self.__telefono}'"
            )
        except ClienteInvalidoError as err:
            # Reversión de cambios ante fallo
            self.__email = email_antiguo
            self._email = email_antiguo
            self.__telefono = telefono_antiguo
            self._telefono = telefono_antiguo
            registrar_advertencia(f"Reversión de contacto para cédula {self.__cedula}: {err}")
            raise err

    def validar_datos(self) -> bool:
        """Verifica que todos los campos del cliente mantengan su integridad."""
        return bool(
            self.__cedula
            and self.__nombre
            and self.PATRON_EMAIL.match(self.__email)
            and (7 <= len(self.__telefono) <= 10)
        )

    # -------------------------------------------------------------------------
    # IMPLEMENTACIÓN DEL MÉTODO ABSTRACTO DE EntidadBase
    # -------------------------------------------------------------------------
    def obtener_detalle(self) -> Dict[str, Any]:
        """
        Retorna los datos estructurados del cliente en formato de diccionario,
        cumpliendo con el contrato abstracto definido en EntidadBase.
        """
        return {
            "tipo_entidad": "Cliente",
            "cedula": self.cedula,
            "nombre": self.nombre,
            "email": self.email,
            "telefono": self.telefono,
            "es_vip": self.es_vip,
            "categoria": self.tipo_cliente,
            "fecha_registro": self.fecha_registro.strftime("%Y-%m-%d %H:%M:%S"),
        }

    # -------------------------------------------------------------------------
    # SOBRECARGA DE OPERADORES Y MÉTODOS MÁGICOS
    # -------------------------------------------------------------------------
    def __str__(self) -> str:
        """Representación amigable para usuario o reportes."""
        vip_tag = " [VIP]" if self.__es_vip else ""
        return (
            f"Cliente: {self.__nombre} (C.C. {self.__cedula}) - "
            f"Email: {self.__email} - Tel: {self.__telefono}{vip_tag}"
        )

    def __repr__(self) -> str:
        """Representación técnica formal del objeto."""
        return (
            f"<Cliente(cedula='{self.__cedula}', nombre='{self.__nombre}', "
            f"email='{self.__email}', vip={self.__es_vip})>"
        )

    def __eq__(self, otro: object) -> bool:
        """Sobrecarga del operador de igualdad: Dos clientes son iguales si comparten cédula."""
        if isinstance(otro, Cliente):
            return self.__cedula == otro.__cedula
        return False

    def __hash__(self) -> int:
        """Permite usar instancias de Cliente como claves en diccionarios o elementos en sets."""
        return hash(self.__cedula)
