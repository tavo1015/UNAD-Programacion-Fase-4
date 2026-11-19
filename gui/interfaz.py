# Universidad Nacional Abierta y a Distancia - UNAD
# Escuela de Ciencias Basicas, Tecnologia e Ingenieria (ECBTI)
# Curso: Programacion (Codigo: 213023)
# Fase 4 - Practicas Simuladas (Componente Practico Colaborativo)
# Empresa: Software FJ - Gestion de Clientes, Servicios y Reservas
# Estudiante: Gustavo Gallego Orrego | Grupo: 213023_119
# Modulo: Interfaz Grafica de Usuario (GUI con Tkinter y ttk)

import os
import re
import sys
import threading
import time
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog

# Asegurar que la raiz de fase 4 se encuentre en el path de Python
RAIZ_PROYECTO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ_PROYECTO not in sys.path:
    sys.path.insert(0, RAIZ_PROYECTO)

from core.exceptions import (
    SoftwareFJError,
    ClienteError,
    ClienteInvalidoError,
    ClienteNoEncontradoError,
    ClienteDuplicadoError,
    ServicioError,
    ServicioInvalidoError,
    ParametroInvalidoError,
    ReservaError,
    EstadoReservaInvalidoError,
    OperacionNoPermitidaError
)
from core.logger import ARCHIVO_LOG, registrar_info, registrar_advertencia, registrar_error
from models.cliente import Cliente
from models.servicios import Servicio, ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from models.reserva import Reserva, EstadoReserva
from models.gestor import GestorSistema
from tests.simulador import ejecutar_simulacion_pasos


class InterfazSoftwareFJ:
    """
    Ventana principal de la aplicacion grafica para la empresa Software FJ.
    Construida con Tkinter y ttk, aplicando los estandares institucionales de la UNAD.
    """

    def __init__(self, root: tk.Tk = None):
        if root is None:
            self.root = tk.Tk()
            self._creo_root = True
        else:
            self.root = root
            self._creo_root = False

        self.root.title("Software FJ - Sistema de Gestion Integral | UNAD Fase 4")
        self.root.geometry("1180x780")
        self.root.minsize(1050, 680)

        # Gestor de datos en memoria para la sesion interactiva
        self.gestor = GestorSistema()

        # Bandera de ejecucion de simulacion
        self._simulacion_en_progreso = False

        # Configurar estilos graficos
        self._configurar_estilos()

        # Construir interfaz completa
        self._construir_interfaz()

        # Cargar datos iniciales de ejemplo para facilitar la navegacion
        self._cargar_datos_demo()

    # =========================================================================
    # CONFIGURACION DE ESTILOS VISUALES TTK
    # =========================================================================
    def _configurar_estilos(self):
        """Define la paleta de colores institucional UNAD y estilos ttk."""
        self.style = ttk.Style()
        temas_disponibles = self.style.theme_names()
        if "clam" in temas_disponibles:
            self.style.theme_use("clam")

        # Paleta institucional UNAD
        self.COLOR_UNAD_AZUL = "#002D62"
        self.COLOR_UNAD_AZUL_MEDIO = "#005691"
        self.COLOR_UNAD_AMARILLO = "#F39200"
        self.COLOR_FONDO_CLARO = "#F4F6F9"
        self.COLOR_TEXTO_OSCURO = "#1C2833"
        self.COLOR_VERDE_EXITO = "#2E7D32"
        self.COLOR_ROJO_ERROR = "#C62828"
        self.COLOR_NARANJA_WARN = "#EF6C00"

        # Configuracion de fuentes base
        self.fuente_titulo = ("Segoe UI", 12, "bold")
        self.fuente_subtitulo = ("Segoe UI", 10, "bold")
        self.fuente_regular = ("Segoe UI", 9)
        self.fuente_mono = ("Consolas", 9)

        # Estilo de Notebook (pestanas)
        self.style.configure("TNotebook", background=self.COLOR_FONDO_CLARO)
        self.style.configure(
            "TNotebook.Tab",
            font=("Segoe UI", 10, "bold"),
            padding=[16, 8],
            background="#D5DBDB"
        )
        self.style.map(
            "TNotebook.Tab",
            background=[("selected", self.COLOR_UNAD_AZUL)],
            foreground=[("selected", "#FFFFFF")]
        )

        # Botones personalizados
        self.style.configure(
            "Primario.TButton",
            font=("Segoe UI", 9, "bold"),
            background=self.COLOR_UNAD_AZUL,
            foreground="#FFFFFF",
            padding=6
        )
        self.style.map(
            "Primario.TButton",
            background=[("active", self.COLOR_UNAD_AZUL_MEDIO)]
        )

        self.style.configure(
            "Exito.TButton",
            font=("Segoe UI", 9, "bold"),
            background=self.COLOR_VERDE_EXITO,
            foreground="#FFFFFF",
            padding=6
        )
        self.style.map(
            "Exito.TButton",
            background=[("active", "#388E3C")]
        )

        self.style.configure(
            "Peligro.TButton",
            font=("Segoe UI", 9, "bold"),
            background=self.COLOR_ROJO_ERROR,
            foreground="#FFFFFF",
            padding=6
        )
        self.style.map(
            "Peligro.TButton",
            background=[("active", "#E53935")]
        )

        # Estilo de Treeview
        self.style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 9, "bold"),
            background="#EAEDED",
            foreground=self.COLOR_TEXTO_OSCURO
        )
        self.style.configure("Treeview", font=("Segoe UI", 9), rowheight=24)

    # =========================================================================
    # CONSTRUCCION PRINCIPAL DE LA VENTANA
    # =========================================================================
    def _construir_interfaz(self):
        """Ensambla el banner institucional, el notebook y la barra de estado."""
        # 1. ENCABEZADO INSTITUCIONAL UNAD
        self._crear_encabezado_institucional()

        # 2. NOTEBOOK CON LAS TRES PESTANAS OBLIGATORIAS
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)

        # Pestana 1: Simulacion de 10 Operaciones
        self.tab_simulacion = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_simulacion, text="  1. Simulacion de 10 Operaciones  ")
        self._construir_pestana_simulacion()

        # Pestana 2: Gestion Interactiva de Clientes, Servicios y Reservas
        self.tab_gestion = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_gestion, text="  2. Gestion Interactiva (CRUD y Reservas)  ")
        self._construir_pestana_gestion()

        # Pestana 3: Auditoria y Logs
        self.tab_auditoria = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_auditoria, text="  3. Auditoria y Logs (software_fj.log)  ")
        self._construir_pestana_auditoria()

        # Enlazar evento para refrescar logs automaticamente cada vez que el usuario haga clic en la pestana 3
        self.notebook.bind("<<NotebookTabChanged>>", self._on_cambio_pestana_principal)

        # 3. BARRA DE ESTADO INFERIOR
        self._crear_barra_estado()

    def _on_cambio_pestana_principal(self, event=None):
        """Autorefresca el visor de logs cada vez que el usuario selecciona la pestana 3."""
        try:
            tab_activa = self.notebook.select()
            if tab_activa == str(self.tab_auditoria):
                self._cargar_contenido_logs()
        except Exception:
            pass

    # -------------------------------------------------------------------------
    # 1. BANNER INSTITUCIONAL
    # -------------------------------------------------------------------------
    def _crear_encabezado_institucional(self):
        """Construye el banner superior con informacion academica formal de la UNAD."""
        frame_banner = tk.Frame(self.root, bg=self.COLOR_UNAD_AZUL, height=85)
        frame_banner.pack(fill=tk.X, side=tk.TOP)

        # Franja decorativa amarilla institucional
        franja_amarilla = tk.Frame(frame_banner, bg=self.COLOR_UNAD_AMARILLO, width=8)
        franja_amarilla.pack(side=tk.LEFT, fill=tk.Y)

        # Contenedor de textos institucionales
        frame_textos = tk.Frame(frame_banner, bg=self.COLOR_UNAD_AZUL)
        frame_textos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=14, pady=6)

        lbl_institucion = tk.Label(
            frame_textos,
            text="UNIVERSIDAD NACIONAL ABIERTA Y A DISTANCIA - UNAD | ECBTI",
            font=("Segoe UI", 12, "bold"),
            bg=self.COLOR_UNAD_AZUL,
            fg="#FFFFFF"
        )
        lbl_institucion.pack(anchor="w")

        lbl_curso = tk.Label(
            frame_textos,
            text="Curso de Programacion (Codigo: 213023) - Fase 4: Componente Practico y Practicas Simuladas",
            font=("Segoe UI", 9),
            bg=self.COLOR_UNAD_AZUL,
            fg="#FAD7A0"
        )
        lbl_curso.pack(anchor="w")

        lbl_sistema = tk.Label(
            frame_textos,
            text="Sistema Integral de Gestion de Clientes, Servicios y Reservas - Empresa: Software FJ",
            font=("Segoe UI", 9, "italic"),
            bg=self.COLOR_UNAD_AZUL,
            fg="#EAECEE"
        )
        lbl_sistema.pack(anchor="w")

        # Contenedor derecho: Datos del estudiante
        frame_estudiante = tk.Frame(frame_banner, bg=self.COLOR_UNAD_AZUL)
        frame_estudiante.pack(side=tk.RIGHT, padx=16, pady=8)

        lbl_autor_tit = tk.Label(
            frame_estudiante,
            text="Estudiante:",
            font=("Segoe UI", 8, "bold"),
            bg=self.COLOR_UNAD_AZUL,
            fg="#FAD7A0"
        )
        lbl_autor_tit.pack(anchor="e")

        lbl_autor = tk.Label(
            frame_estudiante,
            text="Gustavo Gallego Orrego",
            font=("Segoe UI", 10, "bold"),
            bg=self.COLOR_UNAD_AZUL,
            fg="#FFFFFF"
        )
        lbl_autor.pack(anchor="e")

        lbl_grupo = tk.Label(
            frame_estudiante,
            text="Grupo: 213023_119",
            font=("Segoe UI", 8),
            bg=self.COLOR_UNAD_AZUL,
            fg="#D5D8DC"
        )
        lbl_grupo.pack(anchor="e")

    # -------------------------------------------------------------------------
    # 2. PESTANA 1: SIMULACION DE 10 OPERACIONES
    # -------------------------------------------------------------------------
    def _construir_pestana_simulacion(self):
        """Configura la ejecucion y monitoreo visual de los 10 escenarios obligatorios."""
        # Marco superior de control y metricas
        frame_top = ttk.LabelFrame(self.tab_simulacion, text=" Panel de Control de la Suite de Simulacion ", padding=10)
        frame_top.pack(fill=tk.X, padx=10, pady=8)

        # Boton de ejecucion
        self.btn_ejecutar_sim = ttk.Button(
            frame_top,
            text=" [>] Ejecutar Simulacion Completa (10 Pasos) ",
            style="Primario.TButton",
            command=self._iniciar_hilo_simulacion
        )
        self.btn_ejecutar_sim.pack(side=tk.LEFT, padx=(0, 10))

        # Boton de reinicio
        self.btn_limpiar_sim = ttk.Button(
            frame_top,
            text=" Reiniciar Tabla ",
            command=self._limpiar_tabla_simulacion
        )
        self.btn_limpiar_sim.pack(side=tk.LEFT, padx=(0, 15))

        # Barra de progreso
        self.progreso_sim = ttk.Progressbar(frame_top, orient=tk.HORIZONTAL, length=240, mode="determinate", maximum=10)
        self.progreso_sim.pack(side=tk.LEFT, padx=(0, 15))

        # Tarjetas de contadores de resumen
        frame_badges = tk.Frame(frame_top, bg="#FFFFFF", relief=tk.GROOVE, bd=1)
        frame_badges.pack(side=tk.RIGHT, fill=tk.Y, padx=4)

        self.lbl_badge_total = tk.Label(
            frame_badges,
            text="Total: 10",
            font=("Segoe UI", 9, "bold"),
            bg="#EBF5FB",
            fg=self.COLOR_UNAD_AZUL,
            padx=10,
            pady=4
        )
        self.lbl_badge_total.pack(side=tk.LEFT, padx=2)

        self.lbl_badge_ok = tk.Label(
            frame_badges,
            text="Exitosas: 0",
            font=("Segoe UI", 9, "bold"),
            bg="#E8F8F5",
            fg=self.COLOR_VERDE_EXITO,
            padx=10,
            pady=4
        )
        self.lbl_badge_ok.pack(side=tk.LEFT, padx=2)

        self.lbl_badge_controladas = tk.Label(
            frame_badges,
            text="Controladas: 0",
            font=("Segoe UI", 9, "bold"),
            bg="#FEF9E7",
            fg=self.COLOR_NARANJA_WARN,
            padx=10,
            pady=4
        )
        self.lbl_badge_controladas.pack(side=tk.LEFT, padx=2)

        self.lbl_badge_estado = tk.Label(
            frame_badges,
            text="Estado: En espera",
            font=("Segoe UI", 9, "bold"),
            bg="#EAEDED",
            fg="#566573",
            padx=10,
            pady=4
        )
        self.lbl_badge_estado.pack(side=tk.LEFT, padx=2)

        # Division vertical: Arriba la tabla, abajo la consola detallada
        paned = ttk.PanedWindow(self.tab_simulacion, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 8))

        # --- Subpanel 1: Treeview con el estado de los 10 pasos ---
        frame_tabla = ttk.LabelFrame(paned, text=" Estado por Operacion (OK / Excepcion Controlada) ", padding=6)
        paned.add(frame_tabla, weight=5)

        columnas_sim = ("num", "titulo", "estado", "tipo_exc", "detalle")
        self.tree_sim = ttk.Treeview(frame_tabla, columns=columnas_sim, show="headings", height=8)

        self.tree_sim.heading("num", text="#")
        self.tree_sim.heading("titulo", text="Escenario Evaluado")
        self.tree_sim.heading("estado", text="Estado")
        self.tree_sim.heading("tipo_exc", text="Excepcion Gestionada")
        self.tree_sim.heading("detalle", text="Detalle de la Operacion")

        self.tree_sim.column("num", width=45, anchor=tk.CENTER)
        self.tree_sim.column("titulo", width=250, anchor=tk.W)
        self.tree_sim.column("estado", width=160, anchor=tk.CENTER)
        self.tree_sim.column("tipo_exc", width=190, anchor=tk.W)
        self.tree_sim.column("detalle", width=420, anchor=tk.W)

        # Tags de color para resaltar OK vs Excepcion Controlada
        self.tree_sim.tag_configure("tag_ok", background="#E8F8F5", foreground="#145A32")
        self.tree_sim.tag_configure("tag_controlada", background="#FDEDEC", foreground="#78281F")
        self.tree_sim.tag_configure("tag_pendiente", background="#FFFFFF", foreground="#7F8C8D")

        scroll_y_sim = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tree_sim.yview)
        self.tree_sim.configure(yscrollcommand=scroll_y_sim.set)

        self.tree_sim.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y_sim.pack(side=tk.RIGHT, fill=tk.Y)

        # --- Subpanel 2: Consola en tiempo real ---
        frame_consola = ttk.LabelFrame(paned, text=" Salida de Ejecucion y Auditoria en Tiempo Real ", padding=6)
        paned.add(frame_consola, weight=4)

        self.txt_salida_sim = scrolledtext.ScrolledText(
            frame_consola,
            wrap=tk.WORD,
            font=self.fuente_mono,
            bg="#1E1E1E",
            fg="#D4D4D4",
            insertbackground="#FFFFFF"
        )
        self.txt_salida_sim.pack(fill=tk.BOTH, expand=True)

        # Configurar tags de color para la consola interna
        self.txt_salida_sim.tag_configure("tit", foreground="#4FC3F7", font=("Consolas", 9, "bold"))
        self.txt_salida_sim.tag_configure("ok", foreground="#81C784", font=("Consolas", 9, "bold"))
        self.txt_salida_sim.tag_configure("warn", foreground="#FFB74D", font=("Consolas", 9, "bold"))
        self.txt_salida_sim.tag_configure("err", foreground="#E57373", font=("Consolas", 9, "bold"))
        self.txt_salida_sim.tag_configure("dest", foreground="#FFF176")

        self.txt_salida_sim.insert(
            tk.END,
            ">> Sistema listo para simular las 10 operaciones de Software FJ.\n"
            ">> Presione el boton 'Ejecutar Simulacion Completa' para iniciar la suite.\n"
        )

    def _iniciar_hilo_simulacion(self):
        """Inicia la simulacion en un hilo separado para mantener la UI 100% responsiva."""
        if self._simulacion_en_progreso:
            return

        self._simulacion_en_progreso = True
        self.btn_ejecutar_sim.config(state=tk.DISABLED)
        self.progreso_sim["value"] = 0
        self._limpiar_tabla_simulacion()

        self.txt_salida_sim.delete("1.0", tk.END)
        self.txt_salida_sim.insert(tk.END, "=" * 80 + "\n", "tit")
        self.txt_salida_sim.insert(tk.END, " INICIO DE SIMULACION: SUITE DE 10 OPERACIONES - SOFTWARE FJ\n", "tit")
        self.txt_salida_sim.insert(tk.END, "=" * 80 + "\n\n", "tit")

        hilo = threading.Thread(target=self._tarea_simulacion_hilo, daemon=True)
        hilo.start()

    def _tarea_simulacion_hilo(self):
        """Hilo de ejecucion de los 10 pasos con actualizaciones progresivas en la GUI."""
        gestor_sim = GestorSistema()
        cont_ok = 0
        cont_controladas = 0

        def callback_interfaz(paso: dict):
            nonlocal cont_ok, cont_controladas
            num = paso["numero"]
            titulo = paso["titulo"]
            estado = paso["estado"]
            es_exitosa = paso["es_exitosa"]
            tipo_exc = paso["tipo_excepcion"]
            detalle = paso["detalle"]

            if es_exitosa:
                cont_ok += 1
                tag = "tag_ok"
                estado_texto = "[OK] Exitosa"
            else:
                cont_controladas += 1
                tag = "tag_controlada"
                estado_texto = "[!] Excepcion Controlada"

            # Actualizar GUI en el hilo principal
            self.root.after(0, self._actualizar_fila_simulacion, num, titulo, estado_texto, tipo_exc, detalle, tag)
            self.root.after(0, self._actualizar_consola_paso, paso)
            self.root.after(0, self._actualizar_metricas_sim, num, cont_ok, cont_controladas)

            # Breve pausa para efecto visual agradable
            time.sleep(0.20)

        balance, _ = ejecutar_simulacion_pasos(gestor=gestor_sim, callback_paso=callback_interfaz)

        # Al culminar, sincronizar con la pestaña interactiva
        self.root.after(0, self._finalizar_simulacion, gestor_sim, balance)

    def _actualizar_fila_simulacion(self, num, titulo, estado, tipo_exc, detalle, tag):
        """Inserta una fila completada en la tabla Treeview."""
        self.tree_sim.insert("", tk.END, values=(num, titulo, estado, tipo_exc, detalle), tags=(tag,))
        self.tree_sim.yview_moveto(1.0)

    def _actualizar_consola_paso(self, paso: dict):
        """Escribe en la consola interna de la pestana el resultado del paso."""
        num = paso["numero"]
        tit = paso["titulo"]
        self.txt_salida_sim.insert(tk.END, f"--- [OPERACION {num}/10] {tit} ---\n", "tit")
        if paso["es_exitosa"]:
            self.txt_salida_sim.insert(tk.END, f" [OK] {paso['detalle']}\n\n", "ok")
        else:
            self.txt_salida_sim.insert(tk.END, f" [EXCEPCION CONTROLADA]: {paso['tipo_excepcion']}\n", "warn")
            self.txt_salida_sim.insert(tk.END, f"      --> {paso['detalle']}\n\n", "err")
        self.txt_salida_sim.see(tk.END)

    def _actualizar_metricas_sim(self, paso_actual, ok, controladas):
        """Actualiza la barra de progreso y badges."""
        self.progreso_sim["value"] = paso_actual
        self.lbl_badge_ok.config(text=f"Exitosas: {ok}")
        self.lbl_badge_controladas.config(text=f"Controladas: {controladas}")
        self.lbl_badge_estado.config(text=f"Procesando {paso_actual}/10...", fg=self.COLOR_UNAD_AZUL)

    def _finalizar_simulacion(self, gestor_sim: GestorSistema, balance: dict):
        """Restablece el estado de los controles al terminar la simulacion."""
        self._simulacion_en_progreso = False
        self.btn_ejecutar_sim.config(state=tk.NORMAL)
        self.lbl_badge_estado.config(text="100% ESTABLE", fg=self.COLOR_VERDE_EXITO, bg="#D4EFDF")

        self.txt_salida_sim.insert(tk.END, "=" * 80 + "\n", "dest")
        self.txt_salida_sim.insert(
            tk.END,
            f" BALANCE FINAL: 10 de 10 Operaciones ejecutadas con exito total.\n"
            f" - Operaciones normales: {balance['exitosas']}\n"
            f" - Excepciones previstas y controladas: {balance['excepciones_controladas']}\n"
            f" - Cierres inesperados: 0 (CERO) | Estabilidad garantizada.\n"
            f" Auditoria persistida en '{ARCHIVO_LOG}'.\n",
            "dest"
        )
        self.txt_salida_sim.insert(tk.END, "=" * 80 + "\n", "dest")
        self.txt_salida_sim.see(tk.END)

        # Actualizar pestana de auditoria si esta abierta
        self._cargar_contenido_logs()

        # Notificar al usuario con dialogo
        messagebox.showinfo(
            "Simulacion Completada",
            "La Suite de 10 Operaciones se ha ejecutado de forma impecable.\n\n"
            f"- Operaciones exitosas: {balance['exitosas']}\n"
            f"- Excepciones controladas: {balance['excepciones_controladas']}\n\n"
            "Todos los registros han sido guardados en 'software_fj.log'."
        )

    def _limpiar_tabla_simulacion(self):
        """Vacia la tabla de simulacion y reinicia contadores."""
        for item in self.tree_sim.get_children():
            self.tree_sim.delete(item)
        self.progreso_sim["value"] = 0
        self.lbl_badge_ok.config(text="Exitosas: 0")
        self.lbl_badge_controladas.config(text="Controladas: 0")
        self.lbl_badge_estado.config(text="Estado: En espera", fg="#566573", bg="#EAEDED")

    # -------------------------------------------------------------------------
    # 3. PESTANA 2: GESTION INTERACTIVA (CLIENTES, SERVICIOS, RESERVAS)
    # -------------------------------------------------------------------------
    def _construir_pestana_gestion(self):
        """Construye los formularios interactivos con validacion en vivo y cotizador polimorfico."""
        # Sub-Notebook para dividir Clientes, Servicios y Reservas
        sub_notebook = ttk.Notebook(self.tab_gestion)
        sub_notebook.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        # Subpestana 2.1: Registro de Clientes
        frame_clientes = ttk.Frame(sub_notebook)
        sub_notebook.add(frame_clientes, text="  1. Gestion de Clientes  ")
        self._construir_subpestana_clientes(frame_clientes)

        # Subpestana 2.2: Catalogo y Cotizador Polimorfico de Servicios
        frame_servicios = ttk.Frame(sub_notebook)
        sub_notebook.add(frame_servicios, text="  2. Servicios y Cotizador Polimorfico  ")
        self._construir_subpestana_servicios(frame_servicios)

        # Subpestana 2.3: Gestion del Ciclo de Vida de Reservas
        frame_reservas = ttk.Frame(sub_notebook)
        sub_notebook.add(frame_reservas, text="  3. Tramite de Reservas (try/except/else/finally)  ")
        self._construir_subpestana_reservas(frame_reservas)

    # -------------------------------------------------------------------------
    # SUBPESTANA 2.1: CLIENTES CON VALIDACION EN VIVO
    # -------------------------------------------------------------------------
    def _construir_subpestana_clientes(self, parent):
        """Formulario interactivo para registrar clientes con validaciones en vivo."""
        paned = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Panel Izquierdo: Formulario
        frame_form = ttk.LabelFrame(paned, text=" Registrar Nuevo Cliente ", padding=12)
        paned.add(frame_form, weight=4)

        # Campo: Cedula
        ttk.Label(frame_form, text="Documento de Identidad (Cedula):", font=self.fuente_subtitulo).pack(anchor="w", pady=(2, 2))
        self.ent_cli_cedula = ttk.Entry(frame_form, font=self.fuente_regular)
        self.ent_cli_cedula.pack(fill=tk.X, pady=(0, 2))
        self.lbl_val_cedula = ttk.Label(frame_form, text="* 6 a 10 digitos numericos", font=("Segoe UI", 8), foreground="#7F8C8D")
        self.lbl_val_cedula.pack(anchor="w", pady=(0, 6))

        # Campo: Nombre Completo
        ttk.Label(frame_form, text="Nombre Completo:", font=self.fuente_subtitulo).pack(anchor="w", pady=(2, 2))
        self.ent_cli_nombre = ttk.Entry(frame_form, font=self.fuente_regular)
        self.ent_cli_nombre.pack(fill=tk.X, pady=(0, 2))
        self.lbl_val_nombre = ttk.Label(frame_form, text="* Minimo 3 letras, sin simbolos ni numeros", font=("Segoe UI", 8), foreground="#7F8C8D")
        self.lbl_val_nombre.pack(anchor="w", pady=(0, 6))

        # Campo: Email
        ttk.Label(frame_form, text="Correo Electronico Corporativo / Personal:", font=self.fuente_subtitulo).pack(anchor="w", pady=(2, 2))
        self.ent_cli_email = ttk.Entry(frame_form, font=self.fuente_regular)
        self.ent_cli_email.pack(fill=tk.X, pady=(0, 2))
        self.lbl_val_email = ttk.Label(frame_form, text="* Formato: usuario@dominio.com", font=("Segoe UI", 8), foreground="#7F8C8D")
        self.lbl_val_email.pack(anchor="w", pady=(0, 6))

        # Campo: Telefono
        ttk.Label(frame_form, text="Telefono de Contacto:", font=self.fuente_subtitulo).pack(anchor="w", pady=(2, 2))
        self.ent_cli_telefono = ttk.Entry(frame_form, font=self.fuente_regular)
        self.ent_cli_telefono.pack(fill=tk.X, pady=(0, 2))
        self.lbl_val_tel = ttk.Label(frame_form, text="* 7 a 10 digitos numericos", font=("Segoe UI", 8), foreground="#7F8C8D")
        self.lbl_val_tel.pack(anchor="w", pady=(0, 8))

        # Check: VIP
        self.var_cli_vip = tk.BooleanVar(value=False)
        chk_vip = ttk.Checkbutton(
            frame_form,
            text="  Membresia VIP (Otorga 10% de descuento automatico en reservas)",
            variable=self.var_cli_vip
        )
        chk_vip.pack(anchor="w", pady=(4, 14))

        # Validaciones en vivo al teclear
        self.ent_cli_cedula.bind("<KeyRelease>", lambda e: self._validar_campo_cedula_en_vivo())
        self.ent_cli_email.bind("<KeyRelease>", lambda e: self._validar_campo_email_en_vivo())

        # Botones de accion
        btn_registrar = ttk.Button(
            frame_form,
            text=" [+] Registrar Cliente en Memoria ",
            style="Exito.TButton",
            command=self._accion_registrar_cliente
        )
        btn_registrar.pack(fill=tk.X, pady=4)

        btn_limpiar = ttk.Button(
            frame_form,
            text=" Limpiar Formulario ",
            command=self._limpiar_formulario_cliente
        )
        btn_limpiar.pack(fill=tk.X, pady=4)

        # Panel Derecho: Tabla de Clientes
        frame_lista = ttk.LabelFrame(paned, text=" Directorio de Clientes Registrados ", padding=10)
        paned.add(frame_lista, weight=6)

        columnas = ("cedula", "nombre", "email", "telefono", "vip")
        self.tree_clientes = ttk.Treeview(frame_lista, columns=columnas, show="headings", height=12)

        self.tree_clientes.heading("cedula", text="Cedula (ID)")
        self.tree_clientes.heading("nombre", text="Nombre Completo")
        self.tree_clientes.heading("email", text="Correo Electronico")
        self.tree_clientes.heading("telefono", text="Telefono")
        self.tree_clientes.heading("vip", text="VIP")

        self.tree_clientes.column("cedula", width=95, anchor=tk.CENTER)
        self.tree_clientes.column("nombre", width=170, anchor=tk.W)
        self.tree_clientes.column("email", width=180, anchor=tk.W)
        self.tree_clientes.column("telefono", width=100, anchor=tk.CENTER)
        self.tree_clientes.column("vip", width=60, anchor=tk.CENTER)

        scroll_cli = ttk.Scrollbar(frame_lista, orient=tk.VERTICAL, command=self.tree_clientes.yview)
        self.tree_clientes.configure(yscrollcommand=scroll_cli.set)

        self.tree_clientes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_cli.pack(side=tk.RIGHT, fill=tk.Y)

    def _validar_campo_cedula_en_vivo(self):
        """Aplica validacion inmediata visual en el campo de cedula."""
        val = self.ent_cli_cedula.get().strip()
        if not val:
            self.lbl_val_cedula.config(text="* 6 a 10 digitos numericos", foreground="#7F8C8D")
        elif val.isdigit() and (6 <= len(val) <= 10):
            self.lbl_val_cedula.config(text="[OK] Formato de cedula valido", foreground=self.COLOR_VERDE_EXITO)
        else:
            self.lbl_val_cedula.config(text="[X] Invalido: debe tener entre 6 y 10 digitos numericos", foreground=self.COLOR_ROJO_ERROR)

    def _validar_campo_email_en_vivo(self):
        """Aplica validacion inmediata visual en el campo de correo."""
        val = self.ent_cli_email.get().strip().lower()
        patron = r"^[\w\.-]+@[\w\.-]+\.\w{2,4}$"
        if not val:
            self.lbl_val_email.config(text="* Formato: usuario@dominio.com", foreground="#7F8C8D")
        elif re.match(patron, val):
            self.lbl_val_email.config(text="[OK] Formato de correo valido", foreground=self.COLOR_VERDE_EXITO)
        else:
            self.lbl_val_email.config(text="[X] Formato de correo invalido (falta '@' o dominio)", foreground=self.COLOR_ROJO_ERROR)

    def _accion_registrar_cliente(self):
        """Lee el formulario de cliente y gestiona excepciones de negocio."""
        cedula = self.ent_cli_cedula.get().strip()
        nombre = self.ent_cli_nombre.get().strip()
        email = self.ent_cli_email.get().strip()
        telefono = self.ent_cli_telefono.get().strip()
        es_vip = self.var_cli_vip.get()

        try:
            # Intento de instanciacion: El constructor dispara ClienteInvalidoError si falla
            nuevo_cliente = Cliente(
                cedula=cedula,
                nombre=nombre,
                email=email,
                telefono=telefono,
                es_vip=es_vip
            )
            # Intento de insercion en el gestor: Dispara ClienteDuplicadoError si ya existe
            self.gestor.registrar_cliente(nuevo_cliente)

            messagebox.showinfo(
                "Cliente Registrado",
                f"El cliente '{nuevo_cliente.nombre}' (C.C. {nuevo_cliente.cedula}) "
                f"ha sido registrado exitosamente en memoria."
            )
            self._actualizar_tabla_clientes()
            self._sincronizar_comboboxes_reservas()
            self._limpiar_formulario_cliente()

        except ClienteInvalidoError as err_val:
            registrar_error(f"Registro manual de cliente rechazado por formato invalido (Cedula: '{cedula}')", err_val)
            self._cargar_contenido_logs()
            messagebox.showwarning(
                "Validacion Fallida (ClienteInvalidoError)",
                f"No fue posible registrar al cliente debido a errores de formato:\n\n{err_val}\n\n"
                "Por favor corrija los campos senalados e intente de nuevo."
            )
        except ClienteDuplicadoError as err_dup:
            registrar_error(f"Registro manual de cliente rechazado por duplicidad (Cedula: '{cedula}')", err_dup)
            self._cargar_contenido_logs()
            messagebox.showerror(
                "Documento Duplicado (ClienteDuplicadoError)",
                f"Inconsistencia en el registro:\n\n{err_dup}"
            )
        except Exception as err_gral:
            registrar_error("Error inesperado en registro manual de cliente", err_gral)
            self._cargar_contenido_logs()
            messagebox.showerror(
                "Error Inesperado",
                f"Fallo durante la operacion: {err_gral}"
            )

    def _limpiar_formulario_cliente(self):
        """Vacia los campos del formulario de cliente."""
        self.ent_cli_cedula.delete(0, tk.END)
        self.ent_cli_nombre.delete(0, tk.END)
        self.ent_cli_email.delete(0, tk.END)
        self.ent_cli_telefono.delete(0, tk.END)
        self.var_cli_vip.set(False)
        self.lbl_val_cedula.config(text="* 6 a 10 digitos numericos", foreground="#7F8C8D")
        self.lbl_val_email.config(text="* Formato: usuario@dominio.com", foreground="#7F8C8D")

    def _actualizar_tabla_clientes(self):
        """Sincroniza el Treeview de clientes con la lista en memoria del gestor."""
        for item in self.tree_clientes.get_children():
            self.tree_clientes.delete(item)
        for c in self.gestor.clientes:
            vip_str = "SI" if c.es_vip else "NO"
            self.tree_clientes.insert("", tk.END, values=(c.cedula, c.nombre, c.email, c.telefono, vip_str))

    # -------------------------------------------------------------------------
    # SUBPESTANA 2.2: SERVICIOS Y COTIZADOR POLIMORFICO
    # -------------------------------------------------------------------------
    def _construir_subpestana_servicios(self, parent):
        """Formulario con cotizador polimorfico para las 3 subclases de servicio."""
        paned = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Panel Izquierdo: Parametrizacion del Servicio
        frame_config = ttk.LabelFrame(paned, text=" Configurador y Cotizador de Servicios ", padding=10)
        paned.add(frame_config, weight=5)

        # Selector del Tipo de Servicio Concreto
        ttk.Label(frame_config, text="Tipo de Servicio Especializado:", font=self.fuente_subtitulo).pack(anchor="w", pady=(0, 2))
        self.combo_tipo_servicio = ttk.Combobox(
            frame_config,
            values=[
                "ReservaSala (Salas de Juntas y Eventos)",
                "AlquilerEquipo (Equipos Tecnologicos)",
                "AsesoriaEspecializada (Consultoria Profesional)"
            ],
            state="readonly",
            font=self.fuente_regular
        )
        self.combo_tipo_servicio.current(0)
        self.combo_tipo_servicio.pack(fill=tk.X, pady=(0, 8))
        self.combo_tipo_servicio.bind("<<ComboboxSelected>>", lambda e: self._cambiar_formulario_servicio())

        # Campos Comunes
        ttk.Label(frame_config, text="Codigo del Servicio (ID):", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.ent_srv_codigo = ttk.Entry(frame_config, font=self.fuente_regular)
        self.ent_srv_codigo.insert(0, "SALA-02")
        self.ent_srv_codigo.pack(fill=tk.X, pady=(0, 4))

        ttk.Label(frame_config, text="Nombre Comercial:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.ent_srv_nombre = ttk.Entry(frame_config, font=self.fuente_regular)
        self.ent_srv_nombre.insert(0, "Sala Ejecutiva Innovacion")
        self.ent_srv_nombre.pack(fill=tk.X, pady=(0, 4))

        ttk.Label(frame_config, text="Tarifa Base ($ COP):", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.ent_srv_tarifa = ttk.Entry(frame_config, font=self.fuente_regular)
        self.ent_srv_tarifa.insert(0, "75000")
        self.ent_srv_tarifa.pack(fill=tk.X, pady=(0, 8))

        # Contenedor Dinamico segun la subclase seleccionada
        self.frame_campos_especificos = ttk.LabelFrame(frame_config, text=" Parametros Especializados de la Subclase ", padding=8)
        self.frame_campos_especificos.pack(fill=tk.BOTH, expand=True, pady=4)

        # Variables dinamicas
        self.var_sala_capacidad = tk.StringVar(value="10")
        self.var_sala_horas = tk.StringVar(value="3")
        self.var_sala_proyector = tk.BooleanVar(value=True)
        self.var_sala_refrigerio = tk.BooleanVar(value=False)
        self.var_sala_horas_extra = tk.StringVar(value="0")

        self.var_alq_tipo = tk.StringVar(value="Laptop")
        self.var_alq_dias = tk.StringVar(value="3")
        self.var_alq_cant = tk.StringVar(value="2")
        self.var_alq_seguro = tk.BooleanVar(value=True)
        self.var_alq_express = tk.BooleanVar(value=False)

        self.var_ase_area = tk.StringVar(value="Ciberseguridad")
        self.var_ase_nivel = tk.StringVar(value="Senior")
        self.var_ase_horas = tk.StringVar(value="6")
        self.var_ase_presencial = tk.BooleanVar(value=True)
        self.var_ase_urgente = tk.BooleanVar(value=False)

        # Renderizar formulario inicial de sala
        self._cambiar_formulario_servicio()

        # Botones de Cotizacion y Registro
        frame_botones_srv = tk.Frame(frame_config)
        frame_botones_srv.pack(fill=tk.X, pady=(8, 0))

        btn_cotizar = ttk.Button(
            frame_botones_srv,
            text=" Calcular Cotizacion (Polimorfico) ",
            style="Primario.TButton",
            command=self._accion_cotizar_servicio
        )
        btn_cotizar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))

        btn_guardar_srv = ttk.Button(
            frame_botones_srv,
            text=" Guardar en Catalogo ",
            style="Exito.TButton",
            command=self._accion_guardar_servicio
        )
        btn_guardar_srv.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(4, 0))

        # Panel Derecho: Catalogo y Resultados de Cotizacion
        frame_derecho_srv = tk.Frame(paned)
        paned.add(frame_derecho_srv, weight=5)

        # Caja de Desglose de Cotizacion
        frame_desglose = ttk.LabelFrame(frame_derecho_srv, text=" Resultado Liquidado de la Cotizacion ", padding=10)
        frame_desglose.pack(fill=tk.X, pady=(0, 8))

        self.lbl_cotizacion_res = tk.Label(
            frame_desglose,
            text="Seleccione un servicio y presione 'Calcular Cotizacion (Polimorfico)' para ver el desglose.",
            font=self.fuente_mono,
            justify=tk.LEFT,
            anchor="w",
            bg="#F8F9FA",
            fg=self.COLOR_TEXTO_OSCURO,
            relief=tk.SUNKEN,
            padx=10,
            pady=8
        )
        self.lbl_cotizacion_res.pack(fill=tk.X)

        # Tabla del Catalogo
        frame_cat = ttk.LabelFrame(frame_derecho_srv, text=" Catalogo Activo de Servicios ", padding=8)
        frame_cat.pack(fill=tk.BOTH, expand=True)

        cols_srv = ("codigo", "nombre", "tipo", "tarifa")
        self.tree_servicios = ttk.Treeview(frame_cat, columns=cols_srv, show="headings", height=8)

        self.tree_servicios.heading("codigo", text="Codigo")
        self.tree_servicios.heading("nombre", text="Nombre del Servicio")
        self.tree_servicios.heading("tipo", text="Clase / Categoria")
        self.tree_servicios.heading("tarifa", text="Tarifa Base ($)")

        self.tree_servicios.column("codigo", width=80, anchor=tk.CENTER)
        self.tree_servicios.column("nombre", width=180, anchor=tk.W)
        self.tree_servicios.column("tipo", width=140, anchor=tk.W)
        self.tree_servicios.column("tarifa", width=100, anchor=tk.E)

        scroll_srv = ttk.Scrollbar(frame_cat, orient=tk.VERTICAL, command=self.tree_servicios.yview)
        self.tree_servicios.configure(yscrollcommand=scroll_srv.set)

        self.tree_servicios.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_srv.pack(side=tk.RIGHT, fill=tk.Y)

    def _cambiar_formulario_servicio(self):
        """Redibuja los controles especificos de la subclase de servicio seleccionada."""
        for w in self.frame_campos_especificos.winfo_children():
            w.destroy()

        idx = self.combo_tipo_servicio.current()

        if idx == 0:  # ReservaSala
            ttk.Label(self.frame_campos_especificos, text="Capacidad Maxima (1 a 500 pers):").grid(row=0, column=0, sticky="w", pady=2)
            ttk.Entry(self.frame_campos_especificos, textvariable=self.var_sala_capacidad, width=12).grid(row=0, column=1, sticky="w", pady=2)

            ttk.Label(self.frame_campos_especificos, text="Horas de duracion (1 a 72 h):").grid(row=1, column=0, sticky="w", pady=2)
            ttk.Entry(self.frame_campos_especificos, textvariable=self.var_sala_horas, width=12).grid(row=1, column=1, sticky="w", pady=2)

            ttk.Label(self.frame_campos_especificos, text="Horas extra (0 a 24 h):").grid(row=2, column=0, sticky="w", pady=2)
            ttk.Entry(self.frame_campos_especificos, textvariable=self.var_sala_horas_extra, width=12).grid(row=2, column=1, sticky="w", pady=2)

            ttk.Checkbutton(self.frame_campos_especificos, text="Incluye Proyector (+$25.000)", variable=self.var_sala_proyector).grid(row=3, column=0, columnspan=2, sticky="w", pady=2)
            ttk.Checkbutton(self.frame_campos_especificos, text="Incluye Refrigerio ($15.000 x persona)", variable=self.var_sala_refrigerio).grid(row=4, column=0, columnspan=2, sticky="w", pady=2)

        elif idx == 1:  # AlquilerEquipo
            ttk.Label(self.frame_campos_especificos, text="Tipo de Equipo:").grid(row=0, column=0, sticky="w", pady=2)
            cb_tipo = ttk.Combobox(self.frame_campos_especificos, textvariable=self.var_alq_tipo, values=AlquilerEquipo.TIPOS_PERMITIDOS, state="readonly", width=14)
            cb_tipo.grid(row=0, column=1, sticky="w", pady=2)

            ttk.Label(self.frame_campos_especificos, text="Dias de Alquiler (1 a 365):").grid(row=1, column=0, sticky="w", pady=2)
            ttk.Entry(self.frame_campos_especificos, textvariable=self.var_alq_dias, width=12).grid(row=1, column=1, sticky="w", pady=2)

            ttk.Label(self.frame_campos_especificos, text="Cantidad Equipos (1 a 200):").grid(row=2, column=0, sticky="w", pady=2)
            ttk.Entry(self.frame_campos_especificos, textvariable=self.var_alq_cant, width=12).grid(row=2, column=1, sticky="w", pady=2)

            ttk.Checkbutton(self.frame_campos_especificos, text="Seguro contra robo y danos (+10% base)", variable=self.var_alq_seguro).grid(row=3, column=0, columnspan=2, sticky="w", pady=2)
            ttk.Checkbutton(self.frame_campos_especificos, text="Entrega Express el mismo dia (+$40.000)", variable=self.var_alq_express).grid(row=4, column=0, columnspan=2, sticky="w", pady=2)

        elif idx == 2:  # AsesoriaEspecializada
            ttk.Label(self.frame_campos_especificos, text="Area de Especialidad:").grid(row=0, column=0, sticky="w", pady=2)
            ttk.Entry(self.frame_campos_especificos, textvariable=self.var_ase_area, width=18).grid(row=0, column=1, sticky="w", pady=2)

            ttk.Label(self.frame_campos_especificos, text="Jerarquia del Consultor:").grid(row=1, column=0, sticky="w", pady=2)
            cb_niv = ttk.Combobox(self.frame_campos_especificos, textvariable=self.var_ase_nivel, values=["Junior", "Senior", "Master"], state="readonly", width=14)
            cb_niv.grid(row=1, column=1, sticky="w", pady=2)

            ttk.Label(self.frame_campos_especificos, text="Horas de Consultoria (1 a 240):").grid(row=2, column=0, sticky="w", pady=2)
            ttk.Entry(self.frame_campos_especificos, textvariable=self.var_ase_horas, width=12).grid(row=2, column=1, sticky="w", pady=2)

            ttk.Checkbutton(self.frame_campos_especificos, text="Modalidad Presencial (+$50.000 viaticos)", variable=self.var_ase_presencial).grid(row=3, column=0, columnspan=2, sticky="w", pady=2)
            ttk.Checkbutton(self.frame_campos_especificos, text="Sesion Urgente / Extraordinaria (+25%)", variable=self.var_ase_urgente).grid(row=4, column=0, columnspan=2, sticky="w", pady=2)

    def _instanciar_servicio_actual(self) -> tuple[Servicio, dict]:
        """Crea la instancia correspondiente de Servicio validando parametros."""
        idx = self.combo_tipo_servicio.current()
        codigo = self.ent_srv_codigo.get().strip().upper()
        nombre = self.ent_srv_nombre.get().strip()

        try:
            tarifa = float(self.ent_srv_tarifa.get().strip())
        except ValueError:
            raise ParametroInvalidoError("La tarifa base debe ser un valor numerico valido.")

        kwargs_calculo = {}

        if idx == 0:  # ReservaSala
            try:
                cap = int(self.var_sala_capacidad.get())
                horas = int(self.var_sala_horas.get())
                hextra = int(self.var_sala_horas_extra.get())
            except ValueError:
                raise ParametroInvalidoError("Las personas, horas y horas extra deben ser numeros enteros.")

            srv = ReservaSala(
                codigo_servicio=codigo,
                nombre=nombre,
                tarifa_base_hora=tarifa,
                capacidad_maxima=cap,
                horas=horas,
                incluye_proyector=self.var_sala_proyector.get(),
                incluye_refrigerio=self.var_sala_refrigerio.get()
            )
            kwargs_calculo["horas_extra"] = hextra

        elif idx == 1:  # AlquilerEquipo
            try:
                dias = int(self.var_alq_dias.get())
                cant = int(self.var_alq_cant.get())
            except ValueError:
                raise ParametroInvalidoError("Los dias y la cantidad de equipos deben ser enteros.")

            srv = AlquilerEquipo(
                codigo_servicio=codigo,
                nombre=nombre,
                tarifa_diaria=tarifa,
                tipo_equipo=self.var_alq_tipo.get(),
                dias=dias,
                cantidad=cant,
                incluye_seguro=self.var_alq_seguro.get()
            )
            kwargs_calculo["entrega_express"] = self.var_alq_express.get()

        elif idx == 2:  # AsesoriaEspecializada
            try:
                horas = int(self.var_ase_horas.get())
            except ValueError:
                raise ParametroInvalidoError("Las horas de asesoria deben ser un entero positivo.")

            srv = AsesoriaEspecializada(
                codigo_servicio=codigo,
                nombre=nombre,
                tarifa_hora_base=tarifa,
                area_especialidad=self.var_ase_area.get(),
                nivel_consultor=self.var_ase_nivel.get(),
                horas=horas,
                modalidad_presencial=self.var_ase_presencial.get()
            )
            kwargs_calculo["sesion_urgente"] = self.var_ase_urgente.get()

        return srv, kwargs_calculo

    def _accion_cotizar_servicio(self):
        """Demuestra el calculo de costo polimorfico sobrecargado."""
        try:
            srv, kwargs = self._instanciar_servicio_actual()
            costo_total = srv.calcular_costo(**kwargs)

            texto_res = (
                f"SERVICIO: {srv.nombre} [{srv.codigo_servicio}]\n"
                f"CLASE POLIMORFICA: {type(srv).__name__}\n"
                f"DESCRIPCION: {srv.describir_servicio()}\n"
                f"TARIFA BASE UNITARIA: ${srv.tarifa_base:,.2f} COP\n"
                f"PARAMETROS ADICIONALES: {kwargs}\n"
                f"--------------------------------------------------\n"
                f"VALOR TOTAL LIQUIDADO (CON IVA 19%): ${costo_total:,.2f} COP\n"
            )
            self.lbl_cotizacion_res.config(text=texto_res, fg=self.COLOR_UNAD_AZUL)

        except ParametroInvalidoError as err_param:
            registrar_error("Cotizacion manual de servicio rechazada por parametro invalido", err_param)
            self._cargar_contenido_logs()
            messagebox.showwarning(
                "Parametro Invalido (ParametroInvalidoError)",
                f"No se pudo calcular la cotizacion debido a datos fuera de rango:\n\n{err_param}"
            )
        except Exception as err:
            registrar_error("Error inesperado al cotizar servicio manualmente", err)
            self._cargar_contenido_logs()
            messagebox.showerror("Error de Cotizacion", f"Excepcion capturada: {err}")

    def _accion_guardar_servicio(self):
        """Agrega el servicio configurado al catalogo del gestor."""
        try:
            srv, _ = self._instanciar_servicio_actual()
            self.gestor.registrar_servicio(srv)
            messagebox.showinfo(
                "Servicio Catalogado",
                f"El servicio '{srv.nombre}' ({srv.codigo_servicio}) se ha registrado exitosamente en el catalogo."
            )
            self._actualizar_tabla_servicios()
            self._sincronizar_comboboxes_reservas()

        except ServicioInvalidoError as err_srv:
            registrar_error("Registro manual de servicio rechazado por duplicidad", err_srv)
            self._cargar_contenido_logs()
            messagebox.showerror("Servicio Duplicado (ServicioInvalidoError)", str(err_srv))
        except ParametroInvalidoError as err_param:
            registrar_error("Registro manual de servicio rechazado por parametro fuera de rango", err_param)
            self._cargar_contenido_logs()
            messagebox.showwarning("Parametro Invalido", str(err_param))
        except Exception as err:
            registrar_error("Error inesperado al guardar servicio manualmente", err)
            self._cargar_contenido_logs()
            messagebox.showerror("Error Inesperado", str(err))

    def _actualizar_tabla_servicios(self):
        """Refresca la tabla del catalogo de servicios."""
        for item in self.tree_servicios.get_children():
            self.tree_servicios.delete(item)
        for s in self.gestor.servicios:
            self.tree_servicios.insert(
                "",
                tk.END,
                values=(s.codigo_servicio, s.nombre, type(s).__name__, f"${s.tarifa_base:,.2f}")
            )

    # -------------------------------------------------------------------------
    # SUBPESTANA 2.3: GESTION DE RESERVAS (TRY / EXCEPT / ELSE / FINALLY)
    # -------------------------------------------------------------------------
    def _construir_subpestana_reservas(self, parent):
        """Gestion integral del ciclo de vida de reservas aplicando manejo riguroso de excepciones."""
        # Marco superior: Formulario para crear reserva preliminar
        frame_crear = ttk.LabelFrame(parent, text=" 1. Crear Reserva Preliminar (Estado Inicial: PENDIENTE) ", padding=10)
        frame_crear.pack(fill=tk.X, padx=10, pady=(8, 4))

        frame_grid = tk.Frame(frame_crear)
        frame_grid.pack(fill=tk.X)

        # ID Reserva
        ttk.Label(frame_grid, text="ID Reserva:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w", padx=4, pady=2)
        self.ent_res_id = ttk.Entry(frame_grid, width=14, font=self.fuente_regular)
        self.ent_res_id.insert(0, "RES-2001")
        self.ent_res_id.grid(row=0, column=1, sticky="w", padx=4, pady=2)

        # Selector de Cliente
        ttk.Label(frame_grid, text="Cliente Solicitante:", font=("Segoe UI", 9, "bold")).grid(row=0, column=2, sticky="w", padx=8, pady=2)
        self.combo_res_cliente = ttk.Combobox(frame_grid, width=32, state="readonly", font=self.fuente_regular)
        self.combo_res_cliente.grid(row=0, column=3, sticky="w", padx=4, pady=2)

        # Selector de Servicio
        ttk.Label(frame_grid, text="Servicio a Contratar:", font=("Segoe UI", 9, "bold")).grid(row=0, column=4, sticky="w", padx=8, pady=2)
        self.combo_res_servicio = ttk.Combobox(frame_grid, width=30, state="readonly", font=self.fuente_regular)
        self.combo_res_servicio.grid(row=0, column=5, sticky="w", padx=4, pady=2)

        # Fila 2: Fecha y Notas
        ttk.Label(frame_grid, text="Fecha del Evento\n(AAAA-MM-DD HH:MM):", font=("Segoe UI", 9, "bold")).grid(row=1, column=0, sticky="w", padx=4, pady=4)
        self.ent_res_fecha = ttk.Entry(frame_grid, width=18, font=self.fuente_regular)
        self.ent_res_fecha.insert(0, "2026-11-30 09:00")
        self.ent_res_fecha.grid(row=1, column=1, sticky="w", padx=4, pady=4)

        ttk.Label(frame_grid, text="Notas / Observaciones:", font=("Segoe UI", 9, "bold")).grid(row=1, column=2, sticky="w", padx=8, pady=4)
        self.ent_res_notas = ttk.Entry(frame_grid, width=32, font=self.fuente_regular)
        self.ent_res_notas.insert(0, "Capacitacion empresarial para lideres")
        self.ent_res_notas.grid(row=1, column=3, sticky="w", padx=4, pady=4)

        # Boton Crear Reserva
        btn_crear_res = ttk.Button(
            frame_grid,
            text=" Generar Reserva ",
            style="Primario.TButton",
            command=self._accion_crear_reserva
        )
        btn_crear_res.grid(row=1, column=4, columnspan=2, sticky="ew", padx=8, pady=4)

        # Marco Central: Tabla de Reservas en memoria
        frame_tabla_res = ttk.LabelFrame(parent, text=" 2. Reservas Registradas en Memoria ", padding=8)
        frame_tabla_res.pack(fill=tk.BOTH, expand=True, padx=10, pady=4)

        cols_res = ("id", "cliente", "cedula", "servicio", "fecha", "estado", "costo")
        self.tree_reservas = ttk.Treeview(frame_tabla_res, columns=cols_res, show="headings", height=8)

        self.tree_reservas.heading("id", text="ID Reserva")
        self.tree_reservas.heading("cliente", text="Cliente")
        self.tree_reservas.heading("cedula", text="Cedula")
        self.tree_reservas.heading("servicio", text="Servicio")
        self.tree_reservas.heading("fecha", text="Fecha Evento")
        self.tree_reservas.heading("estado", text="Estado Actual")
        self.tree_reservas.heading("costo", text="Costo Total ($ COP)")

        self.tree_reservas.column("id", width=95, anchor=tk.CENTER)
        self.tree_reservas.column("cliente", width=180, anchor=tk.W)
        self.tree_reservas.column("cedula", width=100, anchor=tk.CENTER)
        self.tree_reservas.column("servicio", width=200, anchor=tk.W)
        self.tree_reservas.column("fecha", width=130, anchor=tk.CENTER)
        self.tree_reservas.column("estado", width=110, anchor=tk.CENTER)
        self.tree_reservas.column("costo", width=120, anchor=tk.E)

        # Coloreado segun estado de reserva
        self.tree_reservas.tag_configure("PENDIENTE", background="#FEF9E7", foreground="#7D6608")
        self.tree_reservas.tag_configure("CONFIRMADA", background="#E8F8F5", foreground="#145A32")
        self.tree_reservas.tag_configure("CANCELADA", background="#FDEDEC", foreground="#78281F")
        self.tree_reservas.tag_configure("PROCESADA", background="#EAF2F8", foreground="#1B4F72")

        scroll_res = ttk.Scrollbar(frame_tabla_res, orient=tk.VERTICAL, command=self.tree_reservas.yview)
        self.tree_reservas.configure(yscrollcommand=scroll_res.set)

        self.tree_reservas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_res.pack(side=tk.RIGHT, fill=tk.Y)

        # Marco Inferior: Operaciones del ciclo de vida con try/except/else/finally
        frame_acciones = ttk.LabelFrame(
            parent,
            text=" 3. Transiciones de Estado con Manejo Riguroso de Excepciones (try / except / else / finally) ",
            padding=10
        )
        frame_acciones.pack(fill=tk.X, padx=10, pady=(4, 8))

        lbl_instruccion = ttk.Label(
            frame_acciones,
            text="Seleccione una fila en la tabla de arriba y presione la accion que desea ejecutar:",
            font=("Segoe UI", 9, "italic")
        )
        lbl_instruccion.pack(anchor="w", pady=(0, 6))

        frame_btns_accion = tk.Frame(frame_acciones)
        frame_btns_accion.pack(fill=tk.X)

        btn_confirmar = ttk.Button(
            frame_btns_accion,
            text="  [OK] Confirmar Reserva (Liquidar Costo Definitivo)  ",
            style="Exito.TButton",
            command=self._accion_confirmar_reserva
        )
        btn_confirmar.pack(side=tk.LEFT, padx=(0, 8))

        btn_cancelar = ttk.Button(
            frame_btns_accion,
            text="  [X] Cancelar Reserva (Control de redundancia)  ",
            style="Peligro.TButton",
            command=self._accion_cancelar_reserva
        )
        btn_cancelar.pack(side=tk.LEFT, padx=(0, 8))

        btn_procesar = ttk.Button(
            frame_btns_accion,
            text="  Procesar y Culminar  ",
            command=self._accion_procesar_reserva
        )
        btn_procesar.pack(side=tk.LEFT, padx=(0, 8))

    def _sincronizar_comboboxes_reservas(self):
        """Actualiza los desplegables de seleccion de cliente y servicio para reservas."""
        # Lista de clientes
        valores_clientes = [f"{c.cedula} - {c.nombre}" for c in self.gestor.clientes]
        self.combo_res_cliente["values"] = valores_clientes
        if valores_clientes and not self.combo_res_cliente.get():
            self.combo_res_cliente.current(0)

        # Lista de servicios
        valores_servicios = [f"{s.codigo_servicio} - {s.nombre}" for s in self.gestor.servicios]
        self.combo_res_servicio["values"] = valores_servicios
        if valores_servicios and not self.combo_res_servicio.get():
            self.combo_res_servicio.current(0)

    def _accion_crear_reserva(self):
        """Genera una reserva preliminar asociando cliente y servicio."""
        id_res = self.ent_res_id.get().strip().upper()
        cli_sel = self.combo_res_cliente.get().strip()
        srv_sel = self.combo_res_servicio.get().strip()
        fecha = self.ent_res_fecha.get().strip()
        notas = self.ent_res_notas.get().strip()

        if not cli_sel or not srv_sel or not id_res:
            messagebox.showwarning("Campos Requeridos", "Debe ingresar un ID y seleccionar tanto un cliente como un servicio.")
            return

        cedula = cli_sel.split(" - ")[0].strip()
        cod_srv = srv_sel.split(" - ")[0].strip()

        try:
            reserva = self.gestor.crear_reserva(
                id_reserva=id_res,
                cedula_cliente=cedula,
                codigo_servicio=cod_srv,
                fecha_evento=fecha,
                notas=notas
            )
            messagebox.showinfo(
                "Reserva Registrada",
                f"La reserva [{reserva.id_reserva}] fue creada en estado 'PENDIENTE'.\n"
                f"Cliente: {reserva.cliente.nombre}\n"
                f"Servicio: {reserva.servicio.nombre}"
            )
            self._actualizar_tabla_reservas()

            # Autoincrementar sugerencia de ID
            try:
                num = int(id_res.replace("RES-", "")) + 1
                self.ent_res_id.delete(0, tk.END)
                self.ent_res_id.insert(0, f"RES-{num}")
            except Exception:
                pass

        except ClienteNoEncontradoError as e:
            registrar_error(f"Creacion manual de reserva [{id_res}] rechazada por cliente no encontrado", e)
            self._cargar_contenido_logs()
            messagebox.showerror("Cliente Inexistente", str(e))
        except ServicioInvalidoError as e:
            registrar_error(f"Creacion manual de reserva [{id_res}] rechazada por servicio invalido", e)
            self._cargar_contenido_logs()
            messagebox.showerror("Servicio No Encontrado", str(e))
        except ReservaError as e:
            registrar_error(f"Creacion manual de reserva [{id_res}] rechazada por conflicto", e)
            self._cargar_contenido_logs()
            messagebox.showwarning("Conflicto en Reserva (ReservaError)", str(e))
        except Exception as e:
            registrar_error(f"Error inesperado al crear reserva [{id_res}]", e)
            self._cargar_contenido_logs()
            messagebox.showerror("Error Inesperado", str(e))

    def _obtener_reserva_seleccionada(self) -> Reserva:
        """Devuelve el objeto Reserva correspondiente a la seleccion actual del Treeview."""
        seleccion = self.tree_reservas.selection()
        if not seleccion:
            messagebox.showwarning("Seleccion Requerida", "Por favor seleccione una reserva en la tabla de arriba.")
            return None
        valores = self.tree_reservas.item(seleccion[0], "values")
        id_reserva = valores[0]
        return self.gestor.buscar_reserva(id_reserva)

    def _accion_confirmar_reserva(self):
        """
        Confirma la reserva seleccionada demostrando el bloque try / except / else / finally.
        """
        reserva = self._obtener_reserva_seleccionada()
        if not reserva:
            return

        exito = False
        try:
            # Ejecuta confirmar(): aplica descuento VIP si el cliente lo es y liquida con IVA
            costo_final = reserva.confirmar()
            exito = True

        except EstadoReservaInvalidoError as err_estado:
            # Captura controlada de estado indebido (ej: confirmar una ya cancelada o confirmada)
            messagebox.showwarning(
                "Excepcion de Estado (EstadoReservaInvalidoError)",
                f"Transicion no permitida:\n\n{err_estado}"
            )

        except Exception as err_otro:
            messagebox.showerror(
                "Fallo Critico",
                f"Ocurrio un error al liquidar la reserva: {err_otro}"
            )

        else:
            # El bloque ELSE se ejecuta si la transaccion se completo sin excepciones
            vip_info = " (Incluye 10% de descuento VIP)" if reserva.cliente.es_vip else ""
            messagebox.showinfo(
                "Reserva Confirmada con Exito",
                f"Reserva [{reserva.id_reserva}] ha sido CONFIRMADA con exito!\n\n"
                f"Cliente: {reserva.cliente.nombre}{vip_info}\n"
                f"Servicio: {reserva.servicio.nombre}\n"
                f"Valor Total Liquidado (con IVA 19%): ${costo_final:,.2f} COP"
            )
            self._actualizar_tabla_reservas()

        finally:
            # El bloque FINALLY siempre audita y refresca los logs
            registrar_info(f"[AUDITORIA GUI FINALLY] Intento de confirmacion para [{reserva.id_reserva}]. Resultado: {'EXITOSO' if exito else 'FALLIDO'}")
            self._cargar_contenido_logs()

    def _accion_cancelar_reserva(self):
        """Cancela una reserva controlando intentos redundantes con EstadoReservaInvalidoError."""
        reserva = self._obtener_reserva_seleccionada()
        if not reserva:
            return

        motivo = simpledialog.askstring(
            "Cancelar Reserva",
            f"Ingrese el motivo de cancelacion para la reserva [{reserva.id_reserva}]:",
            initialvalue="Solicitud del cliente"
        )
        if motivo is None:
            return  # Usuario cancelo el dialogo

        try:
            reserva.cancelar(motivo=motivo)
            messagebox.showinfo(
                "Reserva Cancelada",
                f"La reserva [{reserva.id_reserva}] ha quedado en estado CANCELADA."
            )
            self._actualizar_tabla_reservas()

        except EstadoReservaInvalidoError as err_redundante:
            registrar_error(f"Cancelacion manual de reserva [{reserva.id_reserva}] rechazada por estado invalido", err_redundante)
            messagebox.showwarning(
                "Cancelacion Invalida (EstadoReservaInvalidoError)",
                f"Operacion rechazada por regla de negocio:\n\n{err_redundante}"
            )
        except OperacionNoPermitidaError as err_pol:
            registrar_error(f"Cancelacion manual de reserva [{reserva.id_reserva}] rechazada por politica", err_pol)
            messagebox.showerror("Operacion No Permitida", str(err_pol))
        except Exception as err:
            registrar_error(f"Error inesperado al cancelar reserva [{reserva.id_reserva}]", err)
            messagebox.showerror("Error Inesperado", str(err))
        finally:
            self._cargar_contenido_logs()

    def _accion_procesar_reserva(self):
        """Culmina el servicio contratado si se encuentra en estado confirmada."""
        reserva = self._obtener_reserva_seleccionada()
        if not reserva:
            return

        try:
            reserva.procesar()
            messagebox.showinfo(
                "Servicio Culminado",
                f"La reserva [{reserva.id_reserva}] fue PROCESADA y prestada a satisfaccion."
            )
            self._actualizar_tabla_reservas()
        except EstadoReservaInvalidoError as err:
            messagebox.showwarning("Estado Invalido", str(err))
        finally:
            self._cargar_contenido_logs()

    def _actualizar_tabla_reservas(self):
        """Sincroniza la tabla de reservas con la memoria del gestor."""
        for item in self.tree_reservas.get_children():
            self.tree_reservas.delete(item)
        for r in self.gestor.reservas:
            estado_val = r.estado.value
            costo_str = f"${r.costo_total:,.2f}" if r.costo_total > 0 else "Pendiente"
            self.tree_reservas.insert(
                "",
                tk.END,
                values=(
                    r.id_reserva,
                    r.cliente.nombre,
                    r.cliente.cedula,
                    r.servicio.nombre,
                    r.fecha_evento,
                    estado_val,
                    costo_str
                ),
                tags=(estado_val,)
            )

    # -------------------------------------------------------------------------
    # 4. PESTANA 3: AUDITORIA Y LOGS (software_fj.log)
    # -------------------------------------------------------------------------
    def _construir_pestana_auditoria(self):
        """Configura el visor de auditoria en vivo con filtrado y estadisticas."""
        frame_top = ttk.LabelFrame(self.tab_auditoria, text=" Herramientas de Auditoria ", padding=8)
        frame_top.pack(fill=tk.X, padx=10, pady=8)

        # Boton Refrescar
        btn_refrescar = ttk.Button(
            frame_top,
            text=" Recargar Logs ",
            style="Primario.TButton",
            command=self._cargar_contenido_logs
        )
        btn_refrescar.pack(side=tk.LEFT, padx=(0, 8))

        # Boton Estadisticas
        btn_stats = ttk.Button(
            frame_top,
            text=" Ver Estadisticas de Auditoria ",
            command=self._mostrar_estadisticas_logs
        )
        btn_stats.pack(side=tk.LEFT, padx=(0, 8))

        # Boton Limpiar Logs
        btn_limpiar = ttk.Button(
            frame_top,
            text=" Limpiar Archivo de Logs ",
            style="Peligro.TButton",
            command=self._limpiar_archivo_logs
        )
        btn_limpiar.pack(side=tk.LEFT, padx=(0, 15))

        # Filtro de registros
        ttk.Label(frame_top, text="Filtrar por nivel:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 4))
        self.combo_filtro_logs = ttk.Combobox(
            frame_top,
            values=["TODOS", "INFO", "WARNING", "ERROR"],
            state="readonly",
            width=12
        )
        self.combo_filtro_logs.current(0)
        self.combo_filtro_logs.pack(side=tk.LEFT)
        self.combo_filtro_logs.bind("<<ComboboxSelected>>", lambda e: self._cargar_contenido_logs())

        # Area de Texto con Scroll para los Logs
        frame_visor = ttk.LabelFrame(self.tab_auditoria, text=f" Contenido del Archivo de Persistencia ({ARCHIVO_LOG}) ", padding=8)
        frame_visor.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 8))

        self.txt_logs = scrolledtext.ScrolledText(
            frame_visor,
            wrap=tk.WORD,
            font=self.fuente_mono,
            bg="#0E1621",
            fg="#E4E6EB"
        )
        self.txt_logs.pack(fill=tk.BOTH, expand=True)

        # Tags de color para el visor de logs
        self.txt_logs.tag_configure("log_info", foreground="#81C784")
        self.txt_logs.tag_configure("log_warn", foreground="#FFB74D", font=("Consolas", 9, "bold"))
        self.txt_logs.tag_configure("log_error", foreground="#E57373", font=("Consolas", 9, "bold"))
        self.txt_logs.tag_configure("log_normal", foreground="#B0BEC5")

        # Cargar logs al inicializar
        self._cargar_contenido_logs()

    def _cargar_contenido_logs(self):
        """Lee el archivo de auditoria y colorea las lineas en el visor segun el nivel."""
        filtro = getattr(self, "combo_filtro_logs", None)
        nivel_filtro = filtro.get() if filtro else "TODOS"

        self.txt_logs.delete("1.0", tk.END)

        if not os.path.exists(ARCHIVO_LOG):
            self.txt_logs.insert(tk.END, f">> El archivo '{ARCHIVO_LOG}' no existe aun en el sistema.\n", "log_warn")
            return

        try:
            with open(ARCHIVO_LOG, "r", encoding="utf-8") as f:
                lineas = f.readlines()

            if not lineas:
                self.txt_logs.insert(tk.END, ">> El archivo de logs esta actualmente vacio.\n", "log_normal")
                return

            for linea in lineas:
                # Filtrado por nivel
                if nivel_filtro != "TODOS":
                    if f"[{nivel_filtro}]" not in linea:
                        continue

                # Coloreado semantico
                if "[ERROR]" in linea:
                    self.txt_logs.insert(tk.END, linea, "log_error")
                elif "[WARNING]" in linea:
                    self.txt_logs.insert(tk.END, linea, "log_warn")
                elif "[INFO]" in linea:
                    self.txt_logs.insert(tk.END, linea, "log_info")
                else:
                    self.txt_logs.insert(tk.END, linea, "log_normal")

            self.txt_logs.see(tk.END)

        except Exception as e:
            self.txt_logs.insert(tk.END, f">> Error al abrir o leer '{ARCHIVO_LOG}': {e}\n", "log_error")

    def _mostrar_estadisticas_logs(self):
        """Calcula y muestra un balance cuantitativo de los eventos en software_fj.log."""
        if not os.path.exists(ARCHIVO_LOG):
            messagebox.showinfo("Estadisticas", "El archivo de logs no existe todavia.")
            return

        try:
            with open(ARCHIVO_LOG, "r", encoding="utf-8") as f:
                lineas = f.readlines()

            total = len(lineas)
            total_info = sum(1 for l in lineas if "[INFO]" in l)
            total_warn = sum(1 for l in lineas if "[WARNING]" in l)
            total_error = sum(1 for l in lineas if "[ERROR]" in l)
            tamano_kb = os.path.getsize(ARCHIVO_LOG) / 1024.0

            mensaje = (
                f"ESTADISTICAS DE AUDITORIA ({ARCHIVO_LOG}):\n\n"
                f"- Tamano del archivo: {tamano_kb:.2f} KB\n"
                f"- Total de registros: {total} lineas\n"
                f"- Eventos Informativos (INFO): {total_info}\n"
                f"- Advertencias Registradas (WARNING): {total_warn}\n"
                f"- Excepciones / Fallos (ERROR): {total_error}\n\n"
                f"Ruta completa: {os.path.abspath(ARCHIVO_LOG)}"
            )
            messagebox.showinfo("Auditoria - Estadisticas", mensaje)

        except Exception as e:
            messagebox.showerror("Error de Estadisticas", f"No fue posible analizar el archivo de log: {e}")

    def _limpiar_archivo_logs(self):
        """Vacia el archivo de log tras confirmacion expresa del evaluador."""
        confirmar = messagebox.askyesno(
            "Confirmar Limpieza",
            f"¿Esta seguro de vaciar completamente el archivo '{ARCHIVO_LOG}'?\n"
            "Esta accion no se puede deshacer."
        )
        if not confirmar:
            return

        try:
            with open(ARCHIVO_LOG, "w", encoding="utf-8") as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Registro de auditoria reiniciado por el usuario desde la Interfaz Grafica.\n")
            self._cargar_contenido_logs()
            messagebox.showinfo("Logs Limpiados", "El archivo de logs ha sido reiniciado satisfactoriamente.")
        except Exception as e:
            messagebox.showerror("Error", f"Fallo al limpiar el archivo: {e}")

    # -------------------------------------------------------------------------
    # 5. BARRA DE ESTADO INFERIOR
    # -------------------------------------------------------------------------
    def _crear_barra_estado(self):
        """Crea una franja inferior informativa con datos de ejecucion y persistencia."""
        frame_status = tk.Frame(self.root, bg="#EAECEE", height=24)
        frame_status.pack(fill=tk.X, side=tk.BOTTOM)

        lbl_status_izq = tk.Label(
            frame_status,
            text=" Software FJ v4.0 | Sistema de Tolerancia a Fallos y Excepciones Activo",
            font=("Segoe UI", 8),
            bg="#EAECEE",
            fg="#2C3E50"
        )
        lbl_status_izq.pack(side=tk.LEFT, padx=6)

        lbl_status_der = tk.Label(
            frame_status,
            text=f"Persistencia: Memoria RAM + Auditoria ({ARCHIVO_LOG}) | Python {sys.version.split()[0]} ",
            font=("Segoe UI", 8),
            bg="#EAECEE",
            fg="#566573"
        )
        lbl_status_der.pack(side=tk.RIGHT, padx=6)

    # -------------------------------------------------------------------------
    # CARGA DE DATOS DEMO
    # -------------------------------------------------------------------------
    def _cargar_datos_demo(self):
        """Puebla clientes y servicios iniciales para que la interfaz sea inmediatamente interactiva."""
        try:
            # Cliente 1 (VIP)
            c1 = Cliente("1015248901", "Carlos Andres Mendoza", "carlos.mendoza@empresa.com", "3104567890", es_vip=True)
            self.gestor.registrar_cliente(c1)

            # Cliente 2 (Estandar)
            c2 = Cliente("1020304050", "Mariana Gomez Silva", "mariana.gomez@corporativo.co", "3158901234", es_vip=False)
            self.gestor.registrar_cliente(c2)

            # Servicio 1: Sala
            s1 = ReservaSala("SALA-01", "Sala de Juntas Principal", 80000.0, capacidad_maxima=15, horas=4, incluye_proyector=True, incluye_refrigerio=True)
            self.gestor.registrar_servicio(s1)

            # Servicio 2: Alquiler
            s2 = AlquilerEquipo("ALQ-01", "Estaciones de Trabajo Portatiles", 45000.0, tipo_equipo="Workstation", dias=5, cantidad=3, incluye_seguro=True)
            self.gestor.registrar_servicio(s2)

            # Servicio 3: Asesoria
            s3 = AsesoriaEspecializada("ASE-01", "Auditoria de Ciberseguridad", 120000.0, area_especialidad="Ciberseguridad", nivel_consultor="Senior", horas=8, modalidad_presencial=True)
            self.gestor.registrar_servicio(s3)

            # Reserva preliminar
            self.gestor.crear_reserva(
                id_reserva="RES-1001",
                cedula_cliente="1015248901",
                codigo_servicio="SALA-01",
                fecha_evento="2026-11-20 09:00",
                notas="Reunion ejecutiva de fin de ano"
            )

            # Refrescar tablas y combos
            self._actualizar_tabla_clientes()
            self._actualizar_tabla_servicios()
            self._actualizar_tabla_reservas()
            self._sincronizar_comboboxes_reservas()

        except Exception as e:
            registrar_error("Error al cargar datos demostrativos en GUI", e)

    def ejecutar(self):
        """Inicia el bucle principal de eventos de Tkinter."""
        self.root.mainloop()


def iniciar_gui():
    """Punto de entrada directo para lanzar la interfaz grafica."""
    app = InterfazSoftwareFJ()
    app.ejecutar()


if __name__ == "__main__":
    iniciar_gui()
