# ================================================================
# AUTOMATICKÁ DIAGNOSTIKA A OPRAVA - LPA Backend
# ================================================================
# Použití: Spusťte tento skript v PowerShell
# ================================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "LPA Backend - Diagnostika a oprava" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$BackendPath = "C:\lpa_web_v2\backend"
$Issues = @()
$Fixed = @()

# ================================================================
# KONTROLA 1: Existence backend složky
# ================================================================
Write-Host "[1/7] Kontrola backend složky..." -ForegroundColor Yellow

if (Test-Path $BackendPath) {
    Write-Host "  ✅ Backend složka existuje: $BackendPath" -ForegroundColor Green
} else {
    Write-Host "  ❌ CHYBA: Backend složka neexistuje!" -ForegroundColor Red
    Write-Host "  Upravte `$BackendPath v tomto skriptu" -ForegroundColor Yellow
    exit 1
}

cd $BackendPath

# ================================================================
# KONTROLA 2: Existence users.py
# ================================================================
Write-Host ""
Write-Host "[2/7] Kontrola users.py..." -ForegroundColor Yellow

$UsersPath = "app\routers\users.py"
if (Test-Path $UsersPath) {
    $Size = (Get-Item $UsersPath).Length
    Write-Host "  ✅ users.py existuje (velikost: $Size bytů)" -ForegroundColor Green
    
    if ($Size -lt 500) {
        Write-Host "  ⚠️  VAROVÁNÍ: Soubor je podezřele malý!" -ForegroundColor Yellow
        $Issues += "users.py je příliš malý"
    }
} else {
    Write-Host "  ❌ users.py NEEXISTUJE!" -ForegroundColor Red
    $Issues += "users.py neexistuje"
}

# ================================================================
# KONTROLA 3: Kontrola main.py - Import
# ================================================================
Write-Host ""
Write-Host "[3/7] Kontrola main.py - Import routerů..." -ForegroundColor Yellow

$MainPath = "app\main.py"
if (Test-Path $MainPath) {
    $MainContent = Get-Content $MainPath -Raw
    
    if ($MainContent -match "from .routers import.*users") {
        Write-Host "  ✅ Import 'users' nalezen v main.py" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Import 'users' CHYBÍ v main.py!" -ForegroundColor Red
        $Issues += "users není importován v main.py"
    }
} else {
    Write-Host "  ❌ main.py neexistuje!" -ForegroundColor Red
    $Issues += "main.py neexistuje"
}

# ================================================================
# KONTROLA 4: Kontrola main.py - Registrace
# ================================================================
Write-Host ""
Write-Host "[4/7] Kontrola main.py - Registrace routeru..." -ForegroundColor Yellow

if ($MainContent -match 'app\.include_router\(users\.router') {
    Write-Host "  ✅ Registrace users.router nalezena" -ForegroundColor Green
} else {
    Write-Host "  ❌ Registrace users.router CHYBÍ!" -ForegroundColor Red
    $Issues += "users.router není zaregistrován"
}

if ($MainContent -match 'prefix="/users"') {
    Write-Host "  ✅ Prefix '/users' je správně nastaven" -ForegroundColor Green
} else {
    Write-Host "  ❌ Prefix '/users' CHYBÍ!" -ForegroundColor Red
    $Issues += "prefix /users není nastaven"
}

# ================================================================
# KONTROLA 5: Kontrola auth routeru
# ================================================================
Write-Host ""
Write-Host "[5/7] Kontrola auth routeru..." -ForegroundColor Yellow

if ($MainContent -match 'prefix="/auth"') {
    Write-Host "  ✅ Auth router má prefix '/auth'" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Auth router NEMÁ prefix '/auth'!" -ForegroundColor Yellow
    $Issues += "auth router nemá prefix /auth"
}

# ================================================================
# KONTROLA 6: Python cache
# ================================================================
Write-Host ""
Write-Host "[6/7] Kontrola Python cache..." -ForegroundColor Yellow

$CacheFolders = @(
    "__pycache__",
    "app\__pycache__",
    "app\routers\__pycache__"
)

$CacheExists = $false
foreach ($folder in $CacheFolders) {
    if (Test-Path $folder) {
        $CacheExists = $true
        break
    }
}

if ($CacheExists) {
    Write-Host "  ⚠️  Python cache složky existují (může způsobovat problémy)" -ForegroundColor Yellow
    $Issues += "Python cache existuje"
} else {
    Write-Host "  ✅ Žádná Python cache" -ForegroundColor Green
}

# ================================================================
# KONTROLA 7: Test dostupnosti portů
# ================================================================
Write-Host ""
Write-Host "[7/7] Kontrola portu 8000..." -ForegroundColor Yellow

$Port8000 = Test-NetConnection -ComputerName localhost -Port 8000 -InformationLevel Quiet -WarningAction SilentlyContinue
if ($Port8000) {
    Write-Host "  ✅ Port 8000 je otevřený (backend pravděpodobně běží)" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Port 8000 není otevřený (backend neběží)" -ForegroundColor Yellow
}

# ================================================================
# SOUHRN
# ================================================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SOUHRN DIAGNOSTIKY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if ($Issues.Count -eq 0) {
    Write-Host ""
    Write-Host "✅ VŠE V POŘÁDKU!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Pokud stále máte problémy:" -ForegroundColor Yellow
    Write-Host "1. Restartujte backend server" -ForegroundColor White
    Write-Host "2. Zkontrolujte backend log na chyby" -ForegroundColor White
    Write-Host "3. Otevřete http://127.0.0.1:8000/docs" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "❌ NALEZENY PROBLÉMY ($($Issues.Count)):" -ForegroundColor Red
    Write-Host ""
    foreach ($issue in $Issues) {
        Write-Host "  • $issue" -ForegroundColor Yellow
    }
    
    # ================================================================
    # NABÍDKA AUTOMATICKÉ OPRAVY
    # ================================================================
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "AUTOMATICKÁ OPRAVA" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    
    $Response = Read-Host "Chcete zkusit automatickou opravu? (A/N)"
    
    if ($Response -eq "A" -or $Response -eq "a") {
        Write-Host ""
        Write-Host "Spouštím automatickou opravu..." -ForegroundColor Cyan
        Write-Host ""
        
        # Smazání cache
        if ($Issues -contains "Python cache existuje") {
            Write-Host "🔧 Mažu Python cache..." -ForegroundColor Yellow
            foreach ($folder in $CacheFolders) {
                if (Test-Path $folder) {
                    Remove-Item -Recurse -Force $folder
                    Write-Host "  ✅ Smazáno: $folder" -ForegroundColor Green
                }
            }
            $Fixed += "Smazána Python cache"
        }
        
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "OPRAVA DOKONČENA" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Automaticky opraveno:" -ForegroundColor Green
        foreach ($fix in $Fixed) {
            Write-Host "  ✅ $fix" -ForegroundColor Green
        }
        
        Write-Host ""
        Write-Host "MANUÁLNÍ OPRAVY (NUTNÉ):" -ForegroundColor Yellow
        Write-Host ""
        
        if ($Issues -contains "users.py neexistuje") {
            Write-Host "1. Zkopírujte users_minimal.py do app\routers\users.py" -ForegroundColor White
        }
        
        if ($Issues -contains "users není importován v main.py") {
            Write-Host "2. Přidejte 'users,' do importu v main.py" -ForegroundColor White
        }
        
        if ($Issues -contains "users.router není zaregistrován") {
            Write-Host "3. Přidejte registraci do main.py:" -ForegroundColor White
            Write-Host "   app.include_router(users.router, prefix=`"/users`", tags=[`"users`"])" -ForegroundColor Gray
        }
        
        if ($Issues -contains "auth router nemá prefix /auth") {
            Write-Host "4. Opravte registraci auth routeru v main.py:" -ForegroundColor White
            Write-Host "   app.include_router(auth.router, prefix=`"/auth`", tags=[`"auth`"])" -ForegroundColor Gray
        }
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DALŠÍ KROKY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Proveďte manuální opravy (pokud jsou potřeba)" -ForegroundColor White
Write-Host "2. Restartujte backend:" -ForegroundColor White
Write-Host "   uvicorn app.main:app --reload" -ForegroundColor Gray
Write-Host "3. Zkontrolujte http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host ""

pause
