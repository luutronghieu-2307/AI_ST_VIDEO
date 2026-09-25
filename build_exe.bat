@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title Đóng gói AURA AI Launcher (.EXE)

echo ============================================================
echo ⚡ BẮT ĐẦU ĐÓNG GÓI ỨNG DỤNG AURA AI LAUNCHER (.EXE)
echo ============================================================
echo.

REM 1. Dò tìm đường dẫn Python khả dụng
set "PY_CMD="

REM Kiểm tra python trong PATH
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_CMD=python"
    goto :FOUND_PYTHON
)

REM Kiểm tra py launcher trong PATH
py --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_CMD=py"
    goto :FOUND_PYTHON
)

REM Kiểm tra trong thư mục .venv nếu có
if exist ".venv\Scripts\python.exe" (
    set "PY_CMD=.venv\Scripts\python.exe"
    goto :FOUND_PYTHON
)

REM Kiểm tra các vị trí cài đặt mặc định của Windows
for %%V in (312 311 310 39) do (
    if exist "%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe" (
        set "PY_CMD=%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe"
        goto :FOUND_PYTHON
    )
    if exist "C:\Python%%V\python.exe" (
        set "PY_CMD=C:\Python%%V\python.exe"
        goto :FOUND_PYTHON
    )
)

:FOUND_PYTHON
if "%PY_CMD%"=="" (
    echo ❌ KHÔNG TÌM THẤY PYTHON TRÊN MÁY TÍNH CỦA BẠN!
    echo.
    echo 💡 Hướng dẫn xử lý:
    echo 1. Hãy tải và cài đặt Python 3.11 hoặc 3.12 từ https://www.python.org/
    echo 2. Khi cài đặt, nhớ TÍCH CHỌN vào ô: "Add Python to PATH"
    echo ============================================================
    pause
    exit /b 1
)

echo ✅ Đã tìm thấy Python tại: %PY_CMD%
%PY_CMD% --version
echo.

REM 2. Cài đặt các gói PyInstaller và Pillow nếu chưa có
echo 📦 [1/3] Đang kiểm tra và cài đặt công cụ đóng gói PyInstaller & Pillow...
%PY_CMD% -m pip install --upgrade pip >nul 2>&1
%PY_CMD% -m pip install pyinstaller Pillow
if %errorlevel% neq 0 (
    echo ❌ Lỗi khi cài đặt PyInstaller! Vui lòng kiểm tra kết nối mạng.
    pause
    exit /b 1
)

REM 3. Chuyển đổi Icon
echo.
echo 🎨 [2/3] Đang xử lý Icon logo H-AURA...
%PY_CMD% scripts\convert_icon.py

REM 4. Chạy PyInstaller
echo.
echo 🚀 [3/3] Đang tiến hành đóng gói file thực thi EXE...
%PY_CMD% -m PyInstaller AURA_Launcher.spec

if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo 🎉 CHÚC MỪNG! ĐÃ HOÀN TẤT ĐÓNG GÓI ỨNG DỤNG!
    echo 📂 Thư mục chứa file EXE: dist\AURA_Launcher\
    echo 🚀 File thực thi: dist\AURA_Launcher\AURA_Launcher.exe
    echo ============================================================
) else (
    echo.
    echo ❌ CÓ LỖI XẢY RA TRONG QUÁ TRÌNH ĐÓNG GÓI!
)

echo.
echo Nhấn phím bất kỳ để đóng cửa sổ này...
pause >nul

