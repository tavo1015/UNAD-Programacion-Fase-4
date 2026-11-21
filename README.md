# Software FJ - Sistema Integral de Gestión de Clientes, Servicios y Reservas

**Universidad Nacional Abierta y a Distancia (UNAD)**  
**Escuela:** Ciencias Básicas, Tecnología e Ingeniería (ECBTI)  
**Curso:** Programación (Código: 213023)  
**Actividad:** Fase 4 - Prácticas Simuladas (Componente Práctico Colaborativo)  
**Empresa ficticia:** Software FJ  
**Estudiante:** Gustavo Gallego Orrego | **Grupo:** 213023_119  

---

## 📌 Descripción del Proyecto

Este proyecto consiste en el diseño e implementación de un sistema orientado a objetos en Python para la empresa **Software FJ**, especializada en la prestación de servicios tecnológicos empresariales:
1. **Reserva de Salas** (reuniones de juntas, proyectores, capacidad de asistentes y refrigerios).
2. **Alquiler de Equipos** (laptops, servidores, estaciones de trabajo con seguro y entrega express).
3. **Asesorías Especializadas** (consultoría en Ciberseguridad, Cloud, DevOps con perfiles Junior, Senior y Master).

### Características Principales:
* **Interfaz Gráfica de Usuario (GUI con Tkinter y ttk):** Moderna, responsiva y con la identidad visual institucional de la UNAD.
* **Sin bases de datos:** Gestión basada exclusivamente en memoria operativa (listas de objetos en RAM) y persistencia en archivos únicamente para el registro de auditoría (`software_fj.log`), cumpliendo las directrices del Anexo 3.
* **Principios POO Rigurosos:** Abstracción (`ABC`), Encapsulamiento avanzado (decoradores `@property` y validaciones con expresiones regulares), Herencia y Polimorfismo.
* **Sobrecarga de Métodos:** Cálculo polimórfico de costos con soporte de descuentos (como el 10% adicional para clientes VIP), impuestos (IVA 19%) y parámetros nombrados opcionales.
* **Manejo Riguroso de Excepciones:** Jerarquía de excepciones personalizadas (`SoftwareFJError`), bloques `try/except/else/finally` y encadenamiento de excepciones (`raise ... from ...`).
* **Suite de Simulación Automatizada:** Ejecuta 10 escenarios secuenciales manteniendo el sistema 100% estable ante fallos previstos.

---

## 📁 Estructura del Proyecto

```text
fase 4/
│
├── core/                           # Núcleo de la aplicación
│   ├── __init__.py
│   ├── base.py                     # Clase abstracta EntidadBase
│   ├── exceptions.py               # Jerarquía de excepciones personalizadas
│   └── logger.py                   # Registro centralizado de auditoría en software_fj.log
│
├── models/                         # Modelos del dominio de negocio (POO)
│   ├── __init__.py
│   ├── cliente.py                  # Entidad Cliente con validaciones en vivo
│   ├── servicios.py                # Clase abstracta Servicio y subclases (Salas, Alquiler, Asesorías)
│   ├── reserva.py                  # Entidad Reserva, enum de estados y transiciones
│   └── gestor.py                   # Gestor en memoria RAM de colecciones sin base de datos
│
├── gui/                            # Interfaz Gráfica de Usuario (Tkinter / ttk)
│   ├── __init__.py
│   └── interfaz.py                 # Ventana principal, banner UNAD y las 3 pestañas
│
├── tests/                          # Suite de pruebas y simulación
│   ├── __init__.py
│   ├── simulador.py                # Suite de las 10 operaciones con callback estructurado
│   └── test_completo.py            # Pruebas unitarias automatizadas (unittest)
│
├── docs/                           # Guías y anexos oficiales de la actividad
├── ejecutar_sistema.bat            # Lanzador para Windows (doble clic)
├── main.py                         # Punto de entrada principal (GUI o CLI según parámetros)
├── software_fj.log                 # Archivo de auditoría y persistencia de eventos
└── README.md                       # Documentación del proyecto
```

---

## 🖥️ Módulos de la Interfaz Gráfica (GUI)

La aplicación cuenta con una barra institucional con los datos formales de la **UNAD**, la **ECBTI**, el curso de **Programación 213023** y el estudiante. Dispone de tres pestañas interactivas:

### 1. Pestaña 1: 'Simulación de 10 Operaciones'
* **Ejecución secuencial asíncrona:** Botón para iniciar la simulación en un hilo secundario sin congelar la ventana.
* **Tabla de estados (Treeview):** Monitoreo visual de cada paso con etiquetas coloreadas:
  * **Verde (`tag_ok`):** Operaciones exitosas normales (6 operaciones).
  * **Rojo/Naranja (`tag_controlada`):** Excepciones previstas y controladas por la lógica de negocio (4 operaciones).
* **Consola en tiempo real:** Visor monoespaciado que muestra la traza detallada y el balance de estabilidad.
* **Métricas y Barra de Progreso:** Indicadores de conteo en vivo (Total: 10, Exitosas, Controladas, Progreso 0% a 100%).

### 2. Pestaña 2: 'Gestión Interactiva (CRUD y Reservas)'
* **Gestión de Clientes:** Formulario interactivo con validaciones en tiempo real (formato de cédula, correo con expresión regular, teléfono y membresía VIP). Si se ingresan datos erróneos se capturan las excepciones `ClienteInvalidoError` o `ClienteDuplicadoError` sin interrumpir la ejecución.
* **Servicios y Cotizador Polimórfico:** Formulario dinámico que adapta sus campos según la subclase elegida (`ReservaSala`, `AlquilerEquipo`, `AsesoriaEspecializada`). Permite cotizar polimórficamente desglosando base, recargos e IVA, y guardar el servicio en el catálogo.
* **Gestión de Reservas:** Permite registrar reservas preliminares en estado `PENDIENTE`. Cuenta con botones para:
  * **Confirmar Reserva:** Implementa el bloque `try / except / else / finally`, aplicando automáticamente el descuento VIP si corresponde y calculando el costo total definitivo.
  * **Cancelar Reserva:** Captura `EstadoReservaInvalidoError` si se intenta cancelar una reserva redundante o ya procesada.
  * **Procesar Reserva:** Ejecuta la culminación de la reserva confirmada.

### 3. Pestaña 3: 'Auditoría y Logs (software_fj.log)'
* **Visor de Archivo de Auditoría:** Muestra las líneas registradas con coloreado semántico para `[INFO]`, `[WARNING]` y `[ERROR]`.
* **Filtro de Logs:** Permite filtrar instantáneamente por nivel (`TODOS`, `INFO`, `WARNING`, `ERROR`).
* **Estadísticas:** Ventana modal que cuantifica total de líneas, tamaño en KB y desglose por tipo de evento.
* **Limpieza Segura:** Opción para reiniciar el archivo de logs con confirmación del usuario.

---

## 🚀 Formas de Ejecución

### Opción A: Lanzador para Windows (Recomendado)
Hacer doble clic en el archivo `ejecutar_sistema.bat`. El script detectará automáticamente la versión de Python instalada y abrirá la Interfaz Gráfica.

### Opción B: Ejecución por Línea de Comandos

1. **Iniciar la Interfaz Gráfica (Modo Predeterminado):**
   ```bash
   python main.py
   ```

2. **Iniciar en Modo Consola Interactiva (CLI):**
   ```bash
   python main.py --cli
   # o bien:
   python main.py --consola
   ```

3. **Ejecutar directamente la suite de simulación de 10 operaciones:**
   ```bash
   python main.py --sim
   ```

4. **Consultar la ayuda de comandos:**
   ```bash
   python main.py --ayuda
   ```

5. **Ejecutar la suite completa de pruebas unitarias:**
   ```bash
   python tests/test_completo.py
   ```
