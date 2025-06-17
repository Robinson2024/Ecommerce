@echo off
echo 🚀 Iniciando Tech Ecommerce...
call venv\Scripts\activate.bat
echo ✅ Entorno virtual activado
echo 🌐 Iniciando servidor en http://127.0.0.1:8000/
python manage.py runserver --settings=config.settings.development
pause
