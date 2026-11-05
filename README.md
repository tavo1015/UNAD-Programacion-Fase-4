# Software FJ - Sistema Integral de Gestión de Clientes, Servicios y Reservas

**Universidad Nacional Abierta y a Distancia (UNAD)**  
**Curso:** Programación (Código: 213023)  
**Actividad:** Fase 4 - Prácticas Simuladas (Componente Práctico Colaborativo)  
**Empresa ficticia:** Software FJ  

---

## 📌 Descripción del Proyecto

Este proyecto consiste en el diseño e implementación de un sistema orientado a objetos en Python para la empresa **Software FJ**, especializada en la gestión de servicios empresariales:
1. **Reserva de Salas** (reuniones, eventos, proyectores, capacidad).
2. **Alquiler de Equipos** (laptops, servidores, estaciones de trabajo).
3. **Asesorías Especializadas** (consultoría técnica, perfiles junior/senior).

### Características Principales:
* **Sin bases de datos:** Gestión basada exclusivamente en memoria, listas de objetos y persistencia en archivos únicamente para el registro de auditoría y fallos (`software_fj.log`).
* **Principios POO Rigurosos:** Abstracción (`ABC`), Encapsulamiento (decoradores `@property`), Herencia y Polimorfismo.
* **Sobrecarga de Métodos:** Cálculo de costos con variantes de impuestos, descuentos y parámetros opcionales.
* **Manejo Avanzado de Excepciones:** Jerarquía de excepciones personalizadas, uso de `try/except`, `try/except/else`, `try/except/finally` y encadenamiento de excepciones (`raise ... from ...`).
* **Estabilidad y Resiliencia:** El sistema procesa al menos 10 escenarios (operaciones exitosas y fallidas simuladas) manteniendo la ejecución estable en todo momento.

---

## 📁 Estructura del Proyecto

```text
├── core/
│   ├── __init__.py
│   ├── base.py            # Clase abstracta EntidadBase
│   ├── exceptions.py      # Excepciones personalizadas del dominio
│   └── logger.py          # Configuración del registro de eventos y logs
│
├── models/
│   ├── __init__.py
│   ├── cliente.py         # Clase Cliente (encapsulamiento y validación)
│   ├── servicios.py       # Clase abstracta Servicio y subclases especializadas
│   └── reserva.py         # Clase Reserva y Gestor de Reservas
│
├── tests/
│   ├── __init__.py
│   └── simulador.py       # Suite con las 10 operaciones de prueba
│
├── docs/                  # Guías y anexos de la actividad
├── main.py                # Punto de entrada de la aplicación
├── .gitignore             # Archivos excluidos del control de versiones
└── README.md              # Documentación del repositorio
```

---

## 👥 Flujo de Trabajo Colaborativo (Git / GitHub)

Para garantizar la participación individual y evitar conflictos de código:

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/tavo1015/UNAD-Programacion-Fase-4.git
   cd UNAD-Programacion-Fase-4
   ```

2. **Crear una rama de trabajo propia:**
   ```bash
   git checkout -b feature/nombre-de-tu-modulo
   ```

3. **Realizar commits frecuentes y descriptivos:**
   ```bash
   git add .
   git commit -m "Implementa validaciones de cliente y excepciones de formato"
   ```

4. **Subir cambios y abrir Pull Request (PR):**
   ```bash
   git push origin feature/nombre-de-tu-modulo
   ```
   Abrir un *Pull Request* hacia la rama `main` en GitHub para revisión del equipo.

---

## 🚀 Ejecución del Sistema

Para ejecutar el simulador con las 10 operaciones y verificar los logs:

```bash
python main.py
```

Los eventos y errores detectados quedarán registrados automáticamente en `software_fj.log`.
