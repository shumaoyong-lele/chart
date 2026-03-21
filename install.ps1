# 统计图制作系统安装脚本
param(
    [switch]$Reinstall,
    [switch]$SkipClone
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$projectUrl = "https://github.com/shumaoyong-lele/chart/"
$venvPath = ".venv"
$venvPython = ".\$venvPath\Scripts\python"
$venvPip = ".\$venvPath\Scripts\pip"
$packages = @("matplotlib", "squarify")

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    统计图制作系统安装脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($Reinstall) {
    Write-Host "[INFO] 重新安装模式..." -ForegroundColor Cyan
    if (Test-Path $venvPath) {
        Write-Host "[INFO] 正在删除旧虚拟环境..." -ForegroundColor Cyan
        Remove-Item -Recurse -Force $venvPath
        Write-Host "[OK] 虚拟环境已删除" -ForegroundColor Green
    }
}

Write-Host "[INFO] 检查 Python 环境..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] 检测到 $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] 未检测到 Python，请先安装 Python" -ForegroundColor Red
    exit 1
}

Write-Host "[INFO] 检查 Git 环境..." -ForegroundColor Cyan
try {
    $gitVersion = git --version 2>&1
    Write-Host "[OK] 检测到 $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] 未检测到 Git，请先安装 Git" -ForegroundColor Red
    exit 1
}

if (-not $SkipClone) {
    Write-Host "[INFO] 检查项目文件..." -ForegroundColor Cyan
    if ((Test-Path "main.py") -or (Test-Path ".git")) {
        Write-Host "[WARN] 项目文件已存在，跳过克隆" -ForegroundColor Yellow
    } else {
        Write-Host "[INFO] 克隆项目: $projectUrl" -ForegroundColor Cyan
        git clone $projectUrl .
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[ERROR] 项目克隆失败" -ForegroundColor Red
            exit 1
        }
        Write-Host "[OK] 项目克隆成功" -ForegroundColor Green
    }
} else {
    Write-Host "[WARN] 跳过克隆步骤" -ForegroundColor Yellow
}

Write-Host "[INFO] 创建虚拟环境 $venvPath..." -ForegroundColor Cyan
if (Test-Path $venvPath) {
    Write-Host "[WARN] 虚拟环境已存在，跳过创建" -ForegroundColor Yellow
} else {
    python -m venv $venvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] 虚拟环境创建失败" -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] 虚拟环境创建成功" -ForegroundColor Green
}

Write-Host "[INFO] 安装 Python 包..." -ForegroundColor Cyan
$failedPackages = @()
foreach ($package in $packages) {
    Write-Host "[INFO] 安装 $package..." -ForegroundColor Cyan
    & $venvPip install $package --quiet 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] $package 安装成功" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] $package 安装失败" -ForegroundColor Red
        $failedPackages += $package
    }
}

Write-Host "[INFO] 验证安装..." -ForegroundColor Cyan
$allInstalled = $failedPackages.Count -eq 0
foreach ($package in $packages) {
    $installed = & $venvPip show $package 2>&1
    if ($installed -match "Name: $package") {
        Write-Host "[OK] $package 已安装" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] $package 未安装" -ForegroundColor Red
        $allInstalled = $false
    }
}

Write-Host ""
if ($allInstalled) {
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "    安装完成！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "项目地址: $projectUrl" -ForegroundColor White
    Write-Host ""
    Write-Host "启动程序:" -ForegroundColor White
    Write-Host "  .\$venvPath\Scripts\python main.py" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "[ERROR] 安装过程中存在问题，请检查错误信息" -ForegroundColor Red
    exit 1
}