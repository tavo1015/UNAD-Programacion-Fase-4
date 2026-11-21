# Universidad Nacional Abierta y a Distancia - UNAD
# Curso: Programacion (Codigo: 213023)
# Fase 4 - Practicas Simuladas (Componente Practico Colaborativo)
# Empresa: Software FJ - Gestion de Clientes, Servicios y Reservas
# Estudiante: Gustavo Gallego Orrego | Grupo: 213023_119

import os
import sys

# Agregar la raiz del proyecto al PYTHONPATH para ejecucion directa
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tests.simulador import ejecutar_simulacion_completa
from core.logger import ARCHIVO_LOG


def mostrar_encabezado():
    """Imprime el banner institucional de la actividad."""
    print("=" * 80)
    print(" UNIVERSIDAD NACIONAL ABIERTA Y A DISTANCIA - UNAD")
    print(" Escuela de Ciencias Basicas, Tecnologia e Ingenieria (ECBTI)")
    print(" Curso: Programacion 213023 | Fase 4 - Practicas Simuladas")
    print(" Sistema Integral de Gestion de Clientes, Servicios y Reservas - Software FJ")
    print("=" * 80)


def ver_ultimos_logs():
    """Muestra las ultimas lineas registradas en software_fj.log."""
    if not os.path.exists(ARCHIVO_LOG):
        print(f"\n[AVISO] El archivo '{ARCHIVO_LOG}' aun no existe. Ejecute la simulacion primero.\n")
        return

    print("\n" + "-" * 80)
    print(f" ULTIMOS REGISTROS DEL ARCHIVO DE AUDITORIA ({ARCHIVO_LOG}):")
    print("-" * 80)
    try:
        with open(ARCHIVO_LOG, "r", encoding="utf-8") as f:
            lineas = f.readlines()
            # Muestra las ultimas 20 lineas
            ultimas = lineas[-20:] if len(lineas) > 20 else lineas
            for linea in ultimas:
                print(linea.rstrip())
    except Exception as e:
        print(f"Error al leer el archivo de log: {e}")
    print("-" * 80 + "\n")


def menu_principal():
    """Menu interactivo de consola para navegacion del tutor o evaluador."""
    while True:
        mostrar_encabezado()
        print(" MODO CONSOLA / CLI")
        print(" 1. Ejecutar la Simulacion de las 10 Operaciones Obligatorias")
        print(f" 2. Consultar el archivo de auditoria y logs ('{ARCHIVO_LOG}')")
        print(" 3. Lanzar la Interfaz Grafica (GUI)")
        print(" 4. Salir")
        print("=" * 80)

        opcion = input(" Seleccione una opcion (1-4): ").strip()

        if opcion == "1":
            ejecutar_simulacion_completa()
            input("\nPresione ENTER para volver al menu principal...")
        elif opcion == "2":
            ver_ultimos_logs()
            input("Presione ENTER para volver al menu principal...")
        elif opcion == "3":
            print("\nIniciando Interfaz Grafica (Tkinter)...")
            lanzar_interfaz_grafica()
        elif opcion == "4":
            print("\nGracias por utilizar el Sistema Integral de Software FJ. ¡Hasta pronto!\n")
            break
        else:
            print("\n[ALERTA] Opcion invalida. Por favor digite una opcion valida (1-4).\n")


def mostrar_ayuda():
    """Muestra la sintaxis y argumentos de linea de comandos."""
    mostrar_encabezado()
    print(" USO DEL SISTEMA SOFTWARE FJ:")
    print("   python main.py             -> Inicia la Interfaz Grafica Tkinter (Modo Predeterminado)")
    print("   python main.py --cli       -> Inicia el Menu Interactivo de Consola")
    print("   python main.py --consola   -> Inicia el Menu Interactivo de Consola")
    print("   python main.py --sim       -> Ejecuta directamente la suite de simulacion")
    print("   python main.py --ayuda     -> Muestra este mensaje de ayuda")
    print("=" * 80 + "\n")


def lanzar_interfaz_grafica():
    """Importa e inicia la aplicacion grafica Tkinter/ttk."""
    try:
        from gui import iniciar_gui
        iniciar_gui()
    except Exception as e:
        print(f"\n[ALERTA] No fue posible inicializar la Interfaz Grafica Tkinter: {e}")
        print("Iniciando automaticamente en modo Consola (CLI)...\n")
        menu_principal()


def main():
    """Punto de entrada principal con despacho por argumentos."""
    argumentos = [arg.lower() for arg in sys.argv[1:]]

    if any(arg in argumentos for arg in ["--ayuda", "-h", "--help"]):
        mostrar_ayuda()
    elif any(arg in argumentos for arg in ["--cli", "--consola", "-c"]):
        menu_principal()
    elif any(arg in argumentos for arg in ["--sim", "--simulacion", "-s"]):
        mostrar_encabezado()
        ejecutar_simulacion_completa()
    else:
        # Por defecto (sin argumentos o con --gui): inicia la Interfaz Grafica
        lanzar_interfaz_grafica()


if __name__ == "__main__":
    main()
