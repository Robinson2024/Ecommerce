#!/usr/bin/env python3
"""
Tech Ecommerce - Script de Verificación de Dependencias
========================================================

Este script verifica que todas las dependencias necesarias estén instaladas
y que el entorno esté configurado correctamente para ejecutar el proyecto.

Autor: Robinson Bravo Morales
Fecha: Diciembre 2025
"""

import sys
import os
import subprocess
import importlib
from pathlib import Path

def print_header():
    """Imprime el encabezado del script"""
    print("=" * 60)
    print("🔍 TECH ECOMMERCE - VERIFICACIÓN DE DEPENDENCIAS")
    print("=" * 60)
    print()

def check_python_version():
    """Verifica la versión de Python"""
    print("📋 Verificando versión de Python...")
    version = sys.version_info
    
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Se requiere Python 3.8+")
        return False

def check_virtual_environment():
    """Verifica si está en un entorno virtual"""
    print("📋 Verificando entorno virtual...")
    
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Entorno virtual activo - OK")
        return True
    else:
        print("⚠️  No se detectó entorno virtual activo")
        print("   Recomendación: Activar venv con 'venv\\Scripts\\activate'")
        return False

def check_django_setup():
    """Verifica la configuración de Django"""
    print("📋 Verificando configuración de Django...")
    
    try:
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
        django.setup()
        print("✅ Django configurado correctamente - OK")
        return True
    except ImportError:
        print("❌ Django no está instalado")
        return False
    except Exception as e:
        print(f"❌ Error en configuración Django: {e}")
        return False

def check_required_packages():
    """Verifica los paquetes Python requeridos"""
    print("📋 Verificando paquetes Python requeridos...")
    
    required_packages = [
        'django',
        'djangorestframework',
        'django_htmx',
        'pillow',
        'python-dotenv',
        'django-versatileimagefield',
        'django-extensions',
        'pytest',
        'pytest-django',
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package.replace('-', '_'))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - FALTANTE")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Faltan {len(missing_packages)} paquetes:")
        print("   Ejecutar: pip install -r requirements/development.txt")
        return False
    else:
        print("✅ Todos los paquetes requeridos están instalados - OK")
        return True

def check_project_structure():
    """Verifica la estructura del proyecto"""
    print("📋 Verificando estructura del proyecto...")
    
    required_paths = [
        'manage.py',
        'config/',
        'apps/',
        'templates/',
        'static/',
        'requirements/',
        'scripts/',
        'db.sqlite3'
    ]
    
    missing_paths = []
    
    for path in required_paths:
        if os.path.exists(path):
            print(f"   ✅ {path}")
        else:
            print(f"   ❌ {path} - FALTANTE")
            missing_paths.append(path)
    
    if missing_paths:
        print(f"\n❌ Faltan {len(missing_paths)} archivos/directorios críticos")
        return False
    else:
        print("✅ Estructura del proyecto completa - OK")
        return True

def check_database():
    """Verifica el estado de la base de datos"""
    print("📋 Verificando base de datos...")
    
    try:
        result = subprocess.run([
            sys.executable, 'manage.py', 'check', '--database', 'default'
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            print("✅ Base de datos configurada correctamente - OK")
            return True
        else:
            print(f"❌ Error en base de datos: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error verificando base de datos: {e}")
        return False

def check_migrations():
    """Verifica el estado de las migraciones"""
    print("📋 Verificando migraciones...")
    
    try:
        result = subprocess.run([
            sys.executable, 'manage.py', 'showmigrations', '--plan'
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            output_lines = result.stdout.strip().split('\n')
            applied_migrations = [line for line in output_lines if '[X]' in line]
            pending_migrations = [line for line in output_lines if '[ ]' in line]
            
            print(f"   ✅ Migraciones aplicadas: {len(applied_migrations)}")
            
            if pending_migrations:
                print(f"   ⚠️  Migraciones pendientes: {len(pending_migrations)}")
                print("   Ejecutar: python manage.py migrate")
                return False
            else:
                print("✅ Todas las migraciones aplicadas - OK")
                return True
        else:
            print(f"❌ Error verificando migraciones: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error verificando migraciones: {e}")
        return False

def check_environment_variables():
    """Verifica las variables de entorno"""
    print("📋 Verificando variables de entorno...")
    
    env_file = Path('.env')
    if env_file.exists():
        print("   ✅ Archivo .env encontrado")
        
        # Cargar y verificar variables críticas
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            critical_vars = ['SECRET_KEY', 'DEBUG']
            missing_vars = []
            
            for var in critical_vars:
                if os.getenv(var):
                    print(f"   ✅ {var}")
                else:
                    print(f"   ❌ {var} - FALTANTE")
                    missing_vars.append(var)
            
            if missing_vars:
                print("   ⚠️  Configurar variables faltantes en .env")
                return False
            else:
                print("✅ Variables de entorno configuradas - OK")
                return True
                
        except ImportError:
            print("   ⚠️  python-dotenv no instalado, verificando variables manualmente...")
            
            # Verificar variables críticas sin dotenv
            critical_vars = ['SECRET_KEY', 'DEBUG']
            missing_vars = []
            
            for var in critical_vars:
                if os.getenv(var):
                    print(f"   ✅ {var}")
                else:
                    print(f"   ❌ {var} - FALTANTE")
                    missing_vars.append(var)
            
            if missing_vars:
                print("   ⚠️  Configurar variables faltantes en sistema o instalar python-dotenv")
                return False
            else:
                print("✅ Variables de entorno configuradas - OK")
                return True
    else:
        print("   ⚠️  Archivo .env no encontrado")
        print("   Copiar .env.example a .env y configurar")
        return False

def print_summary(checks_passed, total_checks):
    """Imprime el resumen final"""
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("=" * 60)
    
    if checks_passed == total_checks:
        print("🎉 ¡TODAS LAS VERIFICACIONES PASARON!")
        print("✅ El proyecto está listo para ejecutarse")
        print("\n🚀 Para iniciar el servidor:")
        print("   python manage.py runserver")
    else:
        print(f"⚠️  {checks_passed}/{total_checks} verificaciones pasaron")
        print("❌ Corregir los problemas antes de continuar")
        print("\n🔧 Comandos útiles:")
        print("   pip install -r requirements/development.txt")
        print("   python manage.py migrate")
        print("   copy .env.example .env")
    
    print("=" * 60)

def main():
    """Función principal"""
    print_header()
    
    checks = [
        check_python_version,
        check_virtual_environment,
        check_project_structure,
        check_required_packages,
        check_environment_variables,
        check_django_setup,
        check_database,
        check_migrations,
    ]
    
    checks_passed = 0
    
    for check in checks:
        try:
            if check():
                checks_passed += 1
            print()
        except Exception as e:
            print(f"❌ Error en verificación: {e}")
            print()
    
    print_summary(checks_passed, len(checks))
    
    # Código de salida
    if checks_passed == len(checks):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
