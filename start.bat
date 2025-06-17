@echo off
REM ================================================================
REM Tech Ecommerce - Script de Inicio del Servidor
REM ================================================================
REM
REM Este script verifica dependencias, aplica migraciones y lanza
REM el servidor de desarrollo de Django automáticamente.
REM
REM Autor: Robinson Bravo Morales
REM Fecha: Junio 2025
REM ================================================================

title Tech Ecommerce - Servidor de Desarrollo

echo.
echo ================================================================
echo 🚀 TECH ECOMMERCE - INICIANDO SERVIDOR DE DESARROLLO
echo ================================================================
echo.

REM Cambiar al directorio del proyecto
cd /d "%~dp0"

echo 📁 Directorio de trabajo: %CD%
echo.

REM Verificar si Python está disponible
echo 🔍 Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no encontrado en PATH
    echo    Instalar Python 3.11+ y agregarlo al PATH
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% encontrado
echo.

REM Verificar si manage.py existe
echo 🔍 Verificando estructura del proyecto...
if not exist "manage.py" (
    echo ❌ manage.py no encontrado
    echo    Ejecutar desde el directorio raíz del proyecto
    echo.
    pause
    exit /b 1
)
echo ✅ Estructura del proyecto validada
echo.

REM Activar entorno virtual si existe
echo 🔍 Verificando entorno virtual...
if exist "venv\Scripts\activate.bat" (
    echo ✅ Activando entorno virtual...
    call venv\Scripts\activate.bat
    echo ✅ Entorno virtual activado
) else (
    echo ⚠️  Entorno virtual no encontrado
    echo    Continuando con Python del sistema...
)
echo.

REM Verificar dependencias críticas
echo 🔍 Verificando dependencias críticas...
python -c "import django; print('✅ Django:', django.get_version())" 2>nul
if errorlevel 1 (
    echo ❌ Django no instalado
    echo    Ejecutando: pip install -r requirements/development.txt
    echo.
    pip install -r requirements/development.txt
    if errorlevel 1 (
        echo ❌ Error instalando dependencias
        pause
        exit /b 1
    )
)

python -c "import django_htmx; print('✅ Django-HTMX instalado')" 2>nul
if errorlevel 1 (
    echo ⚠️  Django-HTMX no encontrado, instalando...
    pip install django-htmx
)

echo.

REM Configurar Django
echo 🔧 Configurando Django...
set DJANGO_SETTINGS_MODULE=config.settings.development

REM Verificar configuración
echo 🔍 Verificando configuración de Django...
python manage.py check --deploy 2>nul
if errorlevel 1 (
    echo ⚠️  Advertencias en configuración, continuando...
    python manage.py check
) else (
    echo ✅ Configuración Django validada
)
echo.

REM Verificar y aplicar migraciones
echo 🗄️  Verificando base de datos...
python manage.py showmigrations --plan >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Problema con migraciones, ejecutando migrate...
    python manage.py migrate
    if errorlevel 1 (
        echo ❌ Error en migraciones
        pause
        exit /b 1
    )
) else (
    echo ✅ Base de datos verificada
    
    REM Verificar si hay migraciones pendientes
    for /f %%i in ('python manage.py showmigrations --plan ^| find "[ ]" /c') do set PENDING=%%i
    if !PENDING! GTR 0 (
        echo ⚠️  Migraciones pendientes detectadas, aplicando...
        python manage.py migrate
        if errorlevel 1 (
            echo ❌ Error aplicando migraciones
            pause
            exit /b 1
        )
        echo ✅ Migraciones aplicadas
    ) else (
        echo ✅ Todas las migraciones están aplicadas
    )
)
echo.

REM Recopilar archivos estáticos si es necesario
echo 📁 Verificando archivos estáticos...
if not exist "staticfiles" (
    echo 📦 Recopilando archivos estáticos...
    python manage.py collectstatic --noinput
    if errorlevel 1 (
        echo ⚠️  Error recopilando estáticos, continuando...
    ) else (
        echo ✅ Archivos estáticos recopilados
    )
) else (
    echo ✅ Archivos estáticos disponibles
)
echo.

REM Mostrar información del servidor
echo ================================================================
echo 🌐 INFORMACIÓN DEL SERVIDOR
echo ================================================================
echo.
echo 🏠 Aplicación Principal: http://127.0.0.1:8000/
echo ⚙️  Panel Admin:         http://127.0.0.1:8000/admin/
echo 🔌 API REST:            http://127.0.0.1:8000/api/
echo.
echo 💡 Para crear un superusuario: python manage.py createsuperuser
echo 📊 Para poblar datos:          python scripts/populate_complete_data.py
echo.
echo ================================================================
echo 🚀 INICIANDO SERVIDOR DE DESARROLLO...
echo ================================================================
echo.
echo ⏹️  Presiona Ctrl+C para detener el servidor
echo.

REM Iniciar servidor
python manage.py runserver 127.0.0.1:8000

REM Si llega aquí, el servidor se detuvo
echo.
echo ================================================================
echo 🛑 SERVIDOR DETENIDO
echo ================================================================
echo.
echo ✅ Servidor Django detenido correctamente
echo 📝 Logs disponibles en: logs/django.log
echo.

REM Pausa solo si hay error o cierre manual
if errorlevel 1 (
    echo ❌ El servidor se cerró con errores
    pause
) else (
    echo 👋 ¡Hasta la próxima!
    timeout /t 3 >nul
)
