@echo off
setlocal
cd /d "%~dp0"

title Campus Complaint Portal - Local Setup

:menu
echo.
echo ================================================
echo   Campus Complaint Portal - Local Setup
echo ================================================
echo   1. Full setup and start the application
echo   2. Install or update dependencies
echo   3. Initialize demo database (resets existing data)
echo   4. Create or update administrator
echo   5. Run tests
echo   6. Start application
echo   0. Exit
echo.
set "MENU_CHOICE="
set /p "MENU_CHOICE=Choose an option: "

if "%MENU_CHOICE%"=="1" goto full_setup
if "%MENU_CHOICE%"=="2" goto install_only
if "%MENU_CHOICE%"=="3" goto initialize_database
if "%MENU_CHOICE%"=="4" goto create_admin
if "%MENU_CHOICE%"=="5" goto run_tests
if "%MENU_CHOICE%"=="6" goto start_application
if "%MENU_CHOICE%"=="0" goto finish
echo Invalid option.
goto menu

:full_setup
call :install_dependencies
if errorlevel 1 goto action_failed
call :ensure_config
if errorlevel 1 goto action_failed

echo.
echo Database setup:
echo   Y = reset the configured database and load demo accounts and complaints.
echo   N = keep existing data; the application will initialize empty tables if needed.
echo Reset and seed the database? Existing data may be deleted (Y/N)
set "RESET_DB="
set /p "RESET_DB=Choice: "
if /i "%RESET_DB%"=="Y" (
    ".venv\Scripts\python.exe" scripts\init_db.py --reset
    if errorlevel 1 goto action_failed
) else (
    echo Skipping database seeding. Existing data will be preserved.
)

echo.
set "MAKE_ADMIN="
set /p "MAKE_ADMIN=Create or update an administrator now? (y/N): "
if /i "%MAKE_ADMIN%"=="Y" (
    ".venv\Scripts\python.exe" scripts\create_admin.py
    if errorlevel 1 goto action_failed
)

echo.
set "RUN_TESTS="
set /p "RUN_TESTS=Run the test suite before starting? (Y/n): "
if /i not "%RUN_TESTS%"=="N" (
    ".venv\Scripts\python.exe" -m pytest -v
    if errorlevel 1 goto action_failed
)

goto launch_app

:install_only
call :install_dependencies
if errorlevel 1 goto action_failed
echo Dependencies are installed.
goto return_to_menu

:initialize_database
call :ensure_environment
if errorlevel 1 goto action_failed
call :ensure_config
if errorlevel 1 goto action_failed
echo WARNING: --reset deletes existing complaints, student accounts, and administrator accounts.
set "RESET_DB="
set /p "RESET_DB=Type RESET to continue: "
if /i not "%RESET_DB%"=="RESET" (
    echo Database reset cancelled.
    goto return_to_menu
)
".venv\Scripts\python.exe" scripts\init_db.py --reset
if errorlevel 1 goto action_failed
echo Demo database initialized.
goto return_to_menu

:create_admin
call :ensure_environment
if errorlevel 1 goto action_failed
call :ensure_config
if errorlevel 1 goto action_failed
".venv\Scripts\python.exe" scripts\create_admin.py
if errorlevel 1 goto action_failed
goto return_to_menu

:run_tests
call :install_dependencies
if errorlevel 1 goto action_failed
".venv\Scripts\python.exe" -m pytest -v
if errorlevel 1 goto action_failed
goto return_to_menu

:start_application
call :ensure_environment
if errorlevel 1 goto action_failed
call :ensure_config
if errorlevel 1 goto action_failed

:launch_app
echo.
echo Starting the application at http://127.0.0.1:5000
echo Press Ctrl+C to stop the server.
".venv\Scripts\python.exe" app.py
goto return_to_menu

:install_dependencies
call :ensure_environment
if errorlevel 1 exit /b 1
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 exit /b 1
exit /b 0

:ensure_environment
where python >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python 3.12 or newer was not found on PATH.
    echo Install Python and enable the option to add it to PATH, then retry.
    exit /b 1
)
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)"
if errorlevel 1 (
    echo ERROR: Python 3.12 or newer is required.
    python --version
    exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
    echo Creating the virtual environment...
    python -m venv .venv
    if errorlevel 1 exit /b 1
)
exit /b 0

:ensure_config
if exist ".env" exit /b 0
if not exist ".env.example" (
    echo ERROR: .env.example is missing.
    exit /b 1
)
copy ".env.example" ".env" >nul
if errorlevel 1 (
    echo ERROR: Could not create .env from .env.example.
    exit /b 1
)
echo Created .env from .env.example.
echo Review its database settings before using MySQL. SQLite can be selected with DB_ENGINE=sqlite.
exit /b 0

:action_failed
echo.
echo The requested step failed. Review the error above, fix the issue, and try again.
goto return_to_menu

:return_to_menu
echo.
pause
goto menu

:finish
endlocal
exit /b 0
