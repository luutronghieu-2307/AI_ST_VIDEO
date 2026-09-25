@echo off
chcp 65001 >nul
title AURA AI Server Runner
echo ⚡ Đang chuẩn bị môi trường và khởi động AURA AI Server...
python scripts\runner.py
if %errorlevel% neq 0 (
    echo.
    echo ❌ Có lỗi xảy ra trong quá trình chạy!
    pause
)
