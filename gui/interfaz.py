# Universidad Nacional Abierta y a Distancia - UNAD
# Escuela de Ciencias Basicas, Tecnologia e Ingenieria (ECBTI)
# Curso: Programacion (Codigo: 213023)
# Fase 4 - Practicas Simuladas (Componente Practico Colaborativo)
# Empresa: Software FJ - Gestion de Clientes, Servicios y Reservas
# Estudiante: Gustavo Gallego Orrego | Grupo: 213023_119
# Modulo: Estructura Base de la Interfaz Grafica (Tkinter y ttk)

import os
import sys
import tkinter as tk
from tkinter import ttk, scrolledtext

RAIZ_PROYECTO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ_PROYECTO not in sys.path:
    sys.path.insert(0, RAIZ_PROYECTO)

ARCHIVO_LOG = os.path.join(RAIZ_PROYECTO, "software_fj.log")


class InterfazSoftwareFJ:
    """
    Ventana principal base de la aplicacion grafica para Software FJ.
    Define la identidad visual UNAD, la barra superior y las pestanas principales
    para integracion con los modulos de simulacion, modelos y auditoria.
    """

    def __init__(self, root: tk.Tk = None):
        if root is None:
            self.root = tk.Tk()
            self._creo_root = True
        else:
            self.root = root
            self._creo_root = False

        self.root.title("Software FJ - Sistema de Gestion Integral | UNAD Fase 4")
        self.root.geometry("1100x720")
        self.root.minsize(960, 620)

        self._configurar_estilos()
        self._construir_interfaz()

    def _configurar_estilos(self):
        """Configura la paleta de colores institucional UNAD y estilos ttk."""
        self.style = ttk.Style()
        if "clam" in self.style.theme_names():
            self.style.theme_use("clam")

        self.COLOR_UNAD_AZUL = "#002D62"
        self.COLOR_UNAD_AZUL_MEDIO = "#005691"
        self.COLOR_UNAD_AMARILLO = "#F39200"
        self.COLOR_FONDO_CLARO = "#F4F6F9"
        self.COLOR_TEXTO_OSCURO = "#1C2833"

        self.fuente_titulo = ("Segoe UI", 12, "bold")
        self.fuente_subtitulo = ("Segoe UI", 10, "bold")
        self.fuente_regular = ("Segoe UI", 9)
        self.fuente_mono = ("Consolas", 9)

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
        self.style.configure(
            "Primario.TButton",
            font=("Segoe UI", 9, "bold"),
            background=self.COLOR_UNAD_AZUL,
            foreground="#FFFFFF",
            padding=6
        )
        self.style.map("Primario.TButton", background=[("active", self.COLOR_UNAD_AZUL_MEDIO)])

    def _construir_interfaz(self):
        """Construye el encabezado UNAD y las tres pestanas de trabajo."""
        self.root.configure(bg=self.COLOR_FONDO_CLARO)

        header = tk.Frame(self.root, bg=self.COLOR_UNAD_AZUL, height=78)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        franja = tk.Frame(self.root, bg=self.COLOR_UNAD_AMARILLO, height=4)
        franja.pack(fill=tk.X, side=tk.TOP)

        izq = tk.Frame(header, bg=self.COLOR_UNAD_AZUL)
        izq.pack(side=tk.LEFT, padx=20, pady=10)
        tk.Label(
            izq,
            text="UNIVERSIDAD NACIONAL ABIERTA Y A DISTANCIA - UNAD | ECBTI",
            font=("Segoe UI", 11, "bold"),
            bg=self.COLOR_UNAD_AZUL,
            fg="#FFFFFF"
        ).pack(anchor="w")
        tk.Label(
            izq,
            text="Curso de Programacion (213023) - Fase 4 | Sistema Integral Software FJ",
            font=("Segoe UI", 9),
            bg=self.COLOR_UNAD_AZUL,
            fg="#D6EAF8"
        ).pack(anchor="w")

        der = tk.Frame(header, bg=self.COLOR_UNAD_AZUL)
        der.pack(side=tk.RIGHT, padx=20, pady=10)
        tk.Label(
            der,
            text="Grupo: 213023_119",
            font=("Segoe UI", 9, "bold"),
            bg=self.COLOR_UNAD_AZUL,
            fg="#FFFFFF"
        ).pack(anchor="e")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        self.tab_simulacion = tk.Frame(self.notebook, bg=self.COLOR_FONDO_CLARO)
        self.tab_gestion = tk.Frame(self.notebook, bg=self.COLOR_FONDO_CLARO)
        self.tab_logs = tk.Frame(self.notebook, bg=self.COLOR_FONDO_CLARO)

        self.notebook.add(self.tab_simulacion, text=" 1. Simulacion de 10 Operaciones ")
        self.notebook.add(self.tab_gestion, text=" 2. Gestion Interactiva (CRUD y Reservas) ")
        self.notebook.add(self.tab_logs, text=" 3. Auditoria y Logs (software_fj.log) ")

        self._poblar_tab_simulacion()
        self._poblar_tab_gestion()
        self._poblar_tab_logs()

    def _poblar_tab_simulacion(self):
        marco = ttk.LabelFrame(self.tab_simulacion, text=" Panel de Simulacion (Anexo 3) ", padding=15)
        marco.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        tk.Label(
            marco,
            text="Area preparada para la integracion de la suite de 10 operaciones (tests/simulador.py).",
            font=self.fuente_subtitulo,
            fg=self.COLOR_TEXTO_OSCURO
        ).pack(anchor="w", pady=(0, 8))

    def _poblar_tab_gestion(self):
        marco = ttk.LabelFrame(self.tab_gestion, text=" Gestion de Clientes, Servicios y Reservas ", padding=15)
        marco.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        tk.Label(
            marco,
            text="Contenedor base para formularios interactivos conectados a los modulos de models/.",
            font=self.fuente_subtitulo,
            fg=self.COLOR_TEXTO_OSCURO
        ).pack(anchor="w", pady=(0, 8))

    def _poblar_tab_logs(self):
        barra = tk.Frame(self.tab_logs, bg=self.COLOR_FONDO_CLARO)
        barra.pack(fill=tk.X, padx=10, pady=(10, 4))
        ttk.Button(barra, text="Actualizar Logs", style="Primario.TButton", command=self.cargar_logs).pack(side=tk.LEFT)

        self.txt_logs = scrolledtext.ScrolledText(
            self.tab_logs,
            font=self.fuente_mono,
            bg="#1E293B",
            fg="#E2E8F0",
            state=tk.DISABLED
        )
        self.txt_logs.pack(fill=tk.BOTH, expand=True, padx=10, pady=(4, 10))
        self.cargar_logs()

    def cargar_logs(self):
        """Lee y muestra el contenido actual del archivo software_fj.log si existe."""
        self.txt_logs.config(state=tk.NORMAL)
        self.txt_logs.delete("1.0", tk.END)
        if os.path.exists(ARCHIVO_LOG):
            with open(ARCHIVO_LOG, "r", encoding="utf-8") as f:
                contenido = f.read()
            self.txt_logs.insert(tk.END, contenido or "[El archivo software_fj.log esta vacio]\n")
        else:
            self.txt_logs.insert(tk.END, f"[AVISO] Aun no existe el archivo de auditoria en:\n{ARCHIVO_LOG}\n")
        self.txt_logs.config(state=tk.DISABLED)

    def ejecutar(self):
        self.root.mainloop()


def iniciar_gui():
    """Punto de entrada grafico del sistema Software FJ."""
    app = InterfazSoftwareFJ()
    app.ejecutar()
