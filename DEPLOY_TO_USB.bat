@echo off
chcp 65001
echo ==========================================
echo      WUCHANG SYSTEM DEPLOYMENT TOOL
echo ==========================================
echo.
echo I have prepared the system files in the local staging folder:
echo %~dp0USB_DRIVE_NEW
echo.
echo Please enter the Drive Letter of your physical USB (e.g. D, E, F):
set /p DriveLetter=Drive Letter: 

if "%DriveLetter%"=="" goto error

echo.
echo Deploying Wuchang System to %DriveLetter%:\ ...
echo.

xcopy "%~dp0USB_DRIVE_NEW\*" %DriveLetter%:\ /E /I /Y

echo.
echo ==========================================
echo      DEPLOYMENT COMPLETE
echo ==========================================
echo The USB is now ready.
echo You can inspect it at %DriveLetter%:\
pause
exit

:error
echo Invalid Input. Exiting.
pause
