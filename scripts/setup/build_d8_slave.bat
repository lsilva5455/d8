@echo off
REM ###############################################################################
REM build_d8_slave.bat - Instalación automática de D8 Slave para Windows
REM 
REM USO: 
REM   Simplemente ejecutar: build_d8_slave.bat
REM
REM DESCRIPCIÓN:
REM   Instala y configura D8 Slave completamente automático en Windows
REM
REM AUTOR: D8 Team
REM FECHA: 2025-11-20
REM ###############################################################################

setlocal enabledelayedexpansion

REM Variables
set "D8_DIR=%USERPROFILE%\d8"
set "D8_REPO=https://github.com/lsilva5455/d8.git"
set "D8_BRANCH=main"
set "SLAVE_PORT=7600"
set "LOG_FILE=%USERPROFILE%\d8_slave_install.log"

REM Colores (usando PowerShell para colores)
set "PS_GREEN=[System.ConsoleColor]::Green"
set "PS_RED=[System.ConsoleColor]::Red"
set "PS_YELLOW=[System.ConsoleColor]::Yellow"

REM Iniciar log
echo. > "%LOG_FILE%"
echo [%date% %time%] Iniciando instalacion de D8 Slave... >> "%LOG_FILE%"

REM Banner
echo.
echo ===============================================================
echo.
echo            D8 SLAVE - INSTALACION AUTOMATICA
echo.
echo ===============================================================
echo.
echo [INFO] Iniciando instalacion de D8 Slave...
echo [INFO] Log: %LOG_FILE%
echo.

REM Verificar si Python esta instalado
:check_python
echo [VERIFICANDO] Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no encontrado >> "%LOG_FILE%"
    echo.
    echo [ERROR] Python no esta instalado.
    echo.
    echo Por favor, instala Python 3.10 o superior desde:
    echo https://www.python.org/downloads/
    echo.
    echo Asegurate de marcar "Add Python to PATH" durante la instalacion.
    echo.
    pause
    exit /b 1
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo [OK] Python ya instalado: !PYTHON_VERSION! >> "%LOG_FILE%"
    echo [OK] Python ya instalado: !PYTHON_VERSION!
)

REM Verificar si Git esta instalado
:check_git
echo [VERIFICANDO] Git...
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git no encontrado >> "%LOG_FILE%"
    echo.
    echo [ERROR] Git no esta instalado.
    echo.
    echo Por favor, instala Git desde:
    echo https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
) else (
    for /f "tokens=3" %%i in ('git --version 2^>^&1') do set GIT_VERSION=%%i
    echo [OK] Git ya instalado: !GIT_VERSION! >> "%LOG_FILE%"
    echo [OK] Git ya instalado: !GIT_VERSION!
)

REM Clonar repositorio
:clone_repo
echo.
echo [CLONANDO] Repositorio D8...
if exist "%D8_DIR%" (
    echo [WARNING] Directorio %D8_DIR% ya existe >> "%LOG_FILE%"
    echo [WARNING] El directorio %D8_DIR% ya existe.
    echo.
    set /p OVERWRITE="Eliminar y clonar de nuevo? (S/N): "
    if /i "!OVERWRITE!"=="S" (
        echo [INFO] Eliminando directorio anterior... >> "%LOG_FILE%"
        echo [INFO] Eliminando directorio anterior...
        rmdir /s /q "%D8_DIR%"
    ) else (
        echo [INFO] Usando directorio existente >> "%LOG_FILE%"
        echo [INFO] Usando directorio existente
        cd /d "%D8_DIR%"
        echo [INFO] Actualizando repositorio... >> "%LOG_FILE%"
        echo [INFO] Actualizando repositorio...
        git fetch origin >> "%LOG_FILE%" 2>&1
        git checkout %D8_BRANCH% >> "%LOG_FILE%" 2>&1
        git pull origin %D8_BRANCH% >> "%LOG_FILE%" 2>&1
        goto :create_venv
    )
)

echo [INFO] Clonando desde %D8_REPO%... >> "%LOG_FILE%"
echo [INFO] Clonando desde %D8_REPO%...
git clone --branch %D8_BRANCH% %D8_REPO% "%D8_DIR%" >> "%LOG_FILE%" 2>&1

if not exist "%D8_DIR%" (
    echo [ERROR] Fallo clonacion del repositorio >> "%LOG_FILE%"
    echo [ERROR] Fallo la clonacion del repositorio
    pause
    exit /b 1
)

echo [OK] Repositorio clonado correctamente >> "%LOG_FILE%"
echo [OK] Repositorio clonado correctamente
cd /d "%D8_DIR%"

REM Crear entorno virtual
:create_venv
echo.
echo [CREANDO] Entorno virtual...
if exist "venv" (
    echo [WARNING] venv ya existe, eliminando... >> "%LOG_FILE%"
    echo [WARNING] venv ya existe, eliminando...
    rmdir /s /q venv
)

python -m venv venv >> "%LOG_FILE%" 2>&1

if not exist "venv" (
    echo [ERROR] Fallo creacion de venv >> "%LOG_FILE%"
    echo [ERROR] Fallo la creacion de venv
    pause
    exit /b 1
)

echo [OK] Entorno virtual creado >> "%LOG_FILE%"
echo [OK] Entorno virtual creado

REM Activar venv e instalar dependencias
:install_deps
echo.
echo [INSTALANDO] Dependencias Python...
call venv\Scripts\activate.bat

echo [INFO] Actualizando pip... >> "%LOG_FILE%"
echo [INFO] Actualizando pip...
python -m pip install --upgrade pip >> "%LOG_FILE%" 2>&1

echo [INFO] Instalando requirements.txt... >> "%LOG_FILE%"
echo [INFO] Instalando requirements.txt...
echo [INFO] Esto puede tomar varios minutos...
pip install -r requirements.txt >> "%LOG_FILE%" 2>&1

if errorlevel 1 (
    echo [ERROR] Fallo instalacion de dependencias >> "%LOG_FILE%"
    echo [ERROR] Fallo la instalacion de dependencias
    echo [ERROR] Revisa el log: %LOG_FILE%
    pause
    exit /b 1
)

echo [OK] Dependencias instaladas correctamente >> "%LOG_FILE%"
echo [OK] Dependencias instaladas correctamente

REM Configurar .env
:configure_env
echo.
echo [CONFIGURANDO] Variables de entorno...
if not exist ".env" (
    echo [INFO] Creando archivo .env... >> "%LOG_FILE%"
    echo [INFO] Creando archivo .env...
    (
        echo # D8 Slave Configuration
        echo SLAVE_TOKEN=default-dev-token-change-in-production
        echo SLAVE_PORT=%SLAVE_PORT%
        echo SLAVE_HOST=0.0.0.0
        echo.
        echo # LLM API Keys ^(opcional - solo si este slave usara LLMs^)
        echo # GROQ_API_KEY=
        echo # GEMINI_API_KEY=
        echo # DEEPSEEK_API_KEY=
    ) > .env
    echo [OK] Archivo .env creado >> "%LOG_FILE%"
    echo [OK] Archivo .env creado
) else (
    echo [OK] Archivo .env ya existe >> "%LOG_FILE%"
    echo [OK] Archivo .env ya existe
)

REM Verificar instalacion
:verify
echo.
echo [VERIFICANDO] Instalacion...

if not exist "app\distributed\slave_server.py" (
    echo [ERROR] Falta archivo slave_server.py >> "%LOG_FILE%"
    echo [ERROR] Falta archivo slave_server.py
    pause
    exit /b 1
)

if not exist "venv" (
    echo [ERROR] Falta directorio venv >> "%LOG_FILE%"
    echo [ERROR] Falta directorio venv
    pause
    exit /b 1
)

REM Verificar dependencias
python -c "import flask, requests" 2>&1 >> "%LOG_FILE%"
if errorlevel 1 (
    echo [ERROR] Faltan dependencias >> "%LOG_FILE%"
    echo [ERROR] Faltan dependencias
    pause
    exit /b 1
)

echo [OK] Instalacion verificada correctamente >> "%LOG_FILE%"
echo [OK] Instalacion verificada correctamente

REM Test rapido
:test
echo.
echo [TESTEANDO] Slave server...
python -c "import sys; sys.path.insert(0, '%D8_DIR%'); from app.distributed.slave_server import get_version_info, _get_available_methods; print('Version Info:', get_version_info()); print('Available Methods:', _get_available_methods())" >> "%LOG_FILE%" 2>&1

if errorlevel 1 (
    echo [WARNING] Test fallo, pero la instalacion esta completa >> "%LOG_FILE%"
    echo [WARNING] Test fallo, pero la instalacion esta completa
) else (
    echo [OK] Test completado exitosamente >> "%LOG_FILE%"
    echo [OK] Test completado exitosamente
)

REM Obtener IP local
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set LOCAL_IP=%%a
    goto :ip_found
)
:ip_found
set LOCAL_IP=%LOCAL_IP:~1%

REM Crear script de inicio rapido
:create_start_script
echo [INFO] Creando script de inicio rapido... >> "%LOG_FILE%"
(
    echo @echo off
    echo cd /d "%D8_DIR%"
    echo call venv\Scripts\activate.bat
    echo python app\distributed\slave_server.py
    echo pause
) > "%D8_DIR%\start_slave.bat"

echo [OK] Script de inicio creado: start_slave.bat >> "%LOG_FILE%"

REM Crear servicio de Windows (opcional)
:create_service
echo.
set /p CREATE_SERVICE="Crear servicio de Windows para inicio automatico? (S/N): "
if /i "%CREATE_SERVICE%"=="S" (
    echo [INFO] Para crear un servicio de Windows, necesitas instalar NSSM >> "%LOG_FILE%"
    echo [INFO] Para crear un servicio de Windows, necesitas instalar NSSM
    echo [INFO] Descarga desde: https://nssm.cc/download
    echo [INFO] Luego ejecuta:
    echo.
    echo   nssm install D8Slave "%D8_DIR%\venv\Scripts\python.exe"
    echo   nssm set D8Slave AppParameters "%D8_DIR%\app\distributed\slave_server.py"
    echo   nssm set D8Slave AppDirectory "%D8_DIR%"
    echo   nssm set D8Slave Start SERVICE_AUTO_START
    echo   nssm start D8Slave
    echo.
)

REM Resumen
:summary
call deactivate 2>nul
echo.
echo ===============================================================
echo.
echo              INSTALACION COMPLETADA
echo.
echo ===============================================================
echo.
echo [RESUMEN]
echo.
echo   Directorio: %D8_DIR%
echo   Python: %PYTHON_VERSION%
echo   Git: %GIT_VERSION%
echo   IP Local: %LOCAL_IP%
echo   Puerto: %SLAVE_PORT%
echo.
echo [PROXIMOS PASOS]
echo.
echo   1. Iniciar slave server:
echo      cd %D8_DIR%
echo      start_slave.bat
echo.
echo   2. O manualmente:
echo      cd %D8_DIR%
echo      venv\Scripts\activate
echo      python app\distributed\slave_server.py
echo.
echo   3. En el MASTER, registrar este slave:
echo      python scripts/add_slave.py nombre-slave %LOCAL_IP% %SLAVE_PORT%
echo.
echo   Log completo: %LOG_FILE%
echo.
echo ===============================================================
echo.

pause
exit /b 0
