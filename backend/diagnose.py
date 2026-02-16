#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DIAGNOSTICKÝ SKRIPT - Najde problém s /users/ endpointem
Spusťte: python diagnose.py
"""

import sys
import os

print("=" * 60)
print("🔍 LPA DIAGNOSTIKA - /users/ endpoint")
print("=" * 60)
print()

# Přidání backend složky do PYTHONPATH
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_path)

errors = []
warnings = []

# ================================================================
# TEST 1: Import bcrypt
# ================================================================
print("[1/8] Test bcrypt...")
try:
    import bcrypt
    print("  ✅ bcrypt je nainstalován")
except ImportError as e:
    print(f"  ❌ bcrypt CHYBÍ: {e}")
    errors.append("bcrypt není nainstalován")

# ================================================================
# TEST 2: Import app.auth
# ================================================================
print()
print("[2/8] Test app.auth...")
try:
    from app.auth import get_db, hash_password, get_current_user
    print("  ✅ app.auth se načetl")
except Exception as e:
    print(f"  ❌ Chyba v app.auth: {e}")
    errors.append(f"app.auth: {e}")

# ================================================================
# TEST 3: Import app.models
# ================================================================
print()
print("[3/8] Test app.models...")
try:
    from app.models import User
    print("  ✅ app.models.User se načetl")
    
    # Zkontroluj metody
    user_instance = User()
    has_has_role = hasattr(user_instance, 'has_role')
    has_get_roles = hasattr(user_instance, 'get_roles_list')
    
    if has_has_role and has_get_roles:
        print("  ✅ User má metody has_role() a get_roles_list()")
    else:
        print(f"  ⚠️  User NEMÁ některé metody:")
        print(f"     has_role: {has_has_role}")
        print(f"     get_roles_list: {has_get_roles}")
        warnings.append("User model nemá všechny potřebné metody")
except Exception as e:
    print(f"  ❌ Chyba v app.models: {e}")
    errors.append(f"app.models: {e}")

# ================================================================
# TEST 4: Import app.routers.users
# ================================================================
print()
print("[4/8] Test app.routers.users...")
try:
    from app.routers import users
    print("  ✅ app.routers.users se načetl")
    
    # Zkontroluj router
    if hasattr(users, 'router'):
        print("  ✅ users.router existuje")
    else:
        print("  ❌ users.router NEEXISTUJE!")
        errors.append("users.router neexistuje")
        
except Exception as e:
    print(f"  ❌ KRITICKÁ CHYBA v app.routers.users:")
    print(f"     {type(e).__name__}: {e}")
    errors.append(f"users.py: {e}")
    import traceback
    print()
    print("  Traceback:")
    traceback.print_exc()

# ================================================================
# TEST 5: Import app.main
# ================================================================
print()
print("[5/8] Test app.main...")
try:
    from app.main import app
    print("  ✅ app.main se načetl")
except Exception as e:
    print(f"  ❌ Chyba v app.main: {e}")
    errors.append(f"app.main: {e}")

# ================================================================
# TEST 6: Kontrola registrace routerů
# ================================================================
print()
print("[6/8] Kontrola registrovaných endpointů...")
try:
    from app.main import app
    
    # Získej všechny cesty
    routes = []
    for route in app.routes:
        if hasattr(route, 'path'):
            routes.append(route.path)
    
    # Zkontroluj /users/
    if any('/users' in r for r in routes):
        print("  ✅ /users/ endpointy jsou zaregistrovány")
        users_routes = [r for r in routes if '/users' in r]
        for route in users_routes[:5]:  # Zobraz prvních 5
            print(f"     • {route}")
    else:
        print("  ❌ /users/ endpointy NEJSOU zaregistrovány!")
        errors.append("/users/ není v routech")
        
    # Zobraz všechny routy pro kontrolu
    print()
    print("  Všechny dostupné routy:")
    for route in sorted(routes)[:20]:  # Prvních 20
        print(f"     • {route}")
        
except Exception as e:
    print(f"  ❌ Chyba při kontrole routů: {e}")
    errors.append(f"route check: {e}")

# ================================================================
# TEST 7: Kontrola main.py registrace
# ================================================================
print()
print("[7/8] Kontrola main.py...")
try:
    with open('app/main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    has_import = 'from .routers import' in content and 'users' in content
    has_register = 'app.include_router(users.router' in content
    has_prefix = 'prefix="/users"' in content
    
    if has_import:
        print("  ✅ users je v importech")
    else:
        print("  ❌ users NENÍ v importech!")
        errors.append("users není importován v main.py")
    
    if has_register:
        print("  ✅ users.router je zaregistrován")
    else:
        print("  ❌ users.router NENÍ zaregistrován!")
        errors.append("users.router není zaregistrován")
        
    if has_prefix:
        print("  ✅ prefix='/users' je nastaven")
    else:
        print("  ⚠️  prefix='/users' možná chybí")
        warnings.append("prefix /users možná chybí")
        
except Exception as e:
    print(f"  ⚠️  Nelze zkontrolovat main.py: {e}")

# ================================================================
# TEST 8: Test HTTP požadavku
# ================================================================
print()
print("[8/8] Test HTTP požadavku na /users/...")
try:
    import requests
    response = requests.get('http://127.0.0.1:8000/users/', timeout=3)
    if response.status_code == 401:
        print("  ✅ Endpoint existuje (vrací 401 - vyžaduje autentizaci)")
    elif response.status_code == 404:
        print("  ❌ Endpoint NEEXISTUJE (404)!")
        errors.append("HTTP test: endpoint vrací 404")
    else:
        print(f"  ⚠️  Neočekávaná odpověď: {response.status_code}")
except requests.exceptions.ConnectionError:
    print("  ⚠️  Backend neběží nebo není dostupný")
    warnings.append("Backend možná neběží")
except ImportError:
    print("  ⚠️  Knihovna requests není nainstalována (přeskakuji test)")
except Exception as e:
    print(f"  ⚠️  Chyba při HTTP testu: {e}")

# ================================================================
# SOUHRN
# ================================================================
print()
print("=" * 60)
print("📊 SOUHRN")
print("=" * 60)
print()

if not errors and not warnings:
    print("✅ VŠE V POŘÁDKU!")
    print()
    print("Pokud stále vidíte 404, zkuste:")
    print("1. Restartovat backend (Ctrl+C a znovu spustit)")
    print("2. Vyčistit cache: Remove-Item -Recurse __pycache__")
    print("3. Zkontrolovat browser console na chyby")
    
elif errors:
    print(f"❌ NALEZENO {len(errors)} KRITICKÝCH CHYB:")
    print()
    for i, error in enumerate(errors, 1):
        print(f"{i}. {error}")
    
    print()
    print("🔧 DOPORUČENÁ OPRAVA:")
    print()
    
    if "bcrypt není nainstalován" in str(errors):
        print("pip install bcrypt")
    
    if "users.py:" in str(errors):
        print("Problém v users.py - viz traceback výše")
        print("Možná řešení:")
        print("  • Zkontrolujte, že models.py má metody has_role() a get_roles_list()")
        print("  • Použijte users_minimal.py místo users.py")
    
    if "users není importován" in str(errors):
        print("Přidejte 'users,' do importu v main.py")
    
    if "users.router není zaregistrován" in str(errors):
        print("Přidejte do main.py:")
        print("app.include_router(users.router, prefix='/users', tags=['users'])")

if warnings:
    print()
    print(f"⚠️  {len(warnings)} VAROVÁNÍ:")
    for i, warning in enumerate(warnings, 1):
        print(f"{i}. {warning}")

print()
print("=" * 60)
print("Pro další pomoc pošlete tento výstup")
print("=" * 60)
