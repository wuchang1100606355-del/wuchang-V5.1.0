@echo off
echo [WUCHANG BOOTLOADER v2.0]
echo DETECTED NEW MEDIA.
echo BOOTING FROM: %~dp0SYSTEM\boot.html
start msedge --app="%~dp0SYSTEM\boot.html"
exit
