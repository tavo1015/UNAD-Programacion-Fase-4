@echo off
rem ============================================================================
rem  UNIVERSIDAD NACIONAL ABIERTA Y A DISTANCIA - UNAD
rem  Escuela de Ciencias Basicas, Tecnologia e Ingenieria (ECBTI)
rem  Curso: Programacion (Codigo: 213023) | Fase 4 - Practicas Simuladas
rem  Empresa: Software FJ - Gestion de Clientes, Servicios y Reservas
rem  Estudiante: Gustavo Gallego Orrego | Grupo: 213023_119
rem  Lanzador Automatico para Windows: Inicia la Interfaz Grafica (GUI)
rem ============================================================================

chcp 65001 > nul
title Software FJ - Sistema de Gestion Integral (UNAD Fase 4)

rem Cambiar al directorio exacto donde reside este archivo .bat
cd /d "%~dp0"

echo ================================================================================
echo   UNIVERSIDAD NACIONAL ABIERTA Y A DISTANCIA - UNAD
echo   Escuela de Ciencias Basicas, Tecnologia e Ingenieria (ECBTI)
echo   Curso: Programacion 213023 ^| Fase 4 - Componente Practico
echo   Software FJ - Sistema Integral de Gestion de Clientes, Servicios y Reservas
echo ================================================================================
echo.

rem Deteccion automatica del interprete de Python en el sistema
set PYTHON_CMD=

where python >nul 2>nul
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
) else (
    where py >nul 2>nul
    if %errorlevel% equ 0 (
        set PYTHON_CMD=py
    )
)

if "%PYTHON_CMD%"=="" (
    echo [ERROR CRITICO] No se detecto ninguna instalacion de Python en el PATH del sistema.
    echo Por favor asegurese de instalar Python 3.10 o superior y marcar 'Add Python to PATH'.
    echo.
    pause
    exit /b 1
)

echo [OK] Interprete detectado: %PYTHON_CMD%
%PYTHON_CMD% --version
echo.
echo Iniciando aplicacion Software FJ...
echo (Para ejecutar en modo consola interactiva pase el parametro --cli)
echo.

rem Ejecutar main.py pasando cualquier parametro adicional que se haya enviado al .bat
%PYTHON_CMD% main.py %*

if %errorlevel% neq 0 (
    echo.
    echo [AVISO] El programa finalizo con codigo de salida: %errorlevel%
    pause
)
