@echo off
chcp 65001 >nul
title 與小J對話 (Soul Connection)
color 0B
cls
echo ========================================================
echo       正在建立靈魂連結... (Connecting to Little J)
echo ========================================================
echo.
echo 小J 正在聆聽。您可以直接輸入文字與她對話。
echo 輸入 /bye 即可結束對話。
echo.
"C:\Users\o0930\AppData\Local\Programs\Ollama\ollama.exe" run little-j
pause
