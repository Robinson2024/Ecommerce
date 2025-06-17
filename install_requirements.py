#!/usr/bin/env python3
"""
Script de instalación automática para Tech Ecommerce
Detecta el entorno y instala las dependencias correspondientes
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command):
    """Ejecuta un comando y maneja errores."""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def detect_environment():
    """Detecta el tipo de entorno."""
    if os.getenv('CI') or os.getenv('GITHUB_ACTIONS') or os.getenv('GITLAB_CI'):
        return 'testing'
    elif os.getenv('DJANGO_ENV') == 'production' or os.getenv('ENV') == 'production':
        return 'production'
    else:
        return 'development'

def install_requirements():
    """Instala las dependencias según el entorno."""
    
    print("🚀 TECH ECOMMERCE - INSTALADOR AUTOMÁTICO")
    print("=" * 50)
    
    # Detectar entorno
    env = detect_environment()
    print(f"🔍 Entorno detectado: {env}")
    
    # Verificar que requirements existe
    req_file = f"requirements/{env}.txt"
    if not Path(req_file).exists():
        print(f"❌ No se encontró el archivo {req_file}")
        return False
    
    # Verificar pip
    success, _ = run_command("pip --version")
    if not success:
        print("❌ pip no está instalado")
        return False
    
    print(f"📦 Instalando dependencias desde {req_file}...")
    
    # Instalar dependencias
    success, output = run_command(f"pip install -r {req_file}")
    
    if success:
        print("✅ Dependencias instaladas correctamente")
        print("\n🎯 SIGUIENTES PASOS:")
        print("1. Configurar variables de entorno (.env)")
        print("2. Ejecutar migraciones: python manage.py migrate")
        print("3. Crear superusuario: python manage.py createsuperuser")
        print("4. Iniciar servidor: python manage.py runserver")
        return True
    else:
        print(f"❌ Error instalando dependencias:\n{output}")
        return False

if __name__ == "__main__":
    success = install_requirements()
    sys.exit(0 if success else 1)
