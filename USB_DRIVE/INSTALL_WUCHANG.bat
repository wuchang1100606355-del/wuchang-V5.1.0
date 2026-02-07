@echo off
echo [WUCHANG INSTALLER]
echo INSTALLING SYSTEM TO C:\Wuchang_OS...
mkdir C:\Wuchang_OS
xcopy "%~dp0SYSTEM\*" C:\Wuchang_OS\ /E /I /Y

echo CREATING SHORTCUT...
set SCRIPT="%TEMP%\%RANDOM%-%RANDOM%-%RANDOM%-%RANDOM%.vbs"
echo Set oWS = WScript.CreateObject("WScript.Shell") >> %SCRIPT%
echo sLinkFile = "%USERPROFILE%\Desktop\Wuchang OS.lnk" >> %SCRIPT%
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %SCRIPT%
echo oLink.TargetPath = "msedge.exe" >> %SCRIPT%
echo oLink.Arguments = "--app=C:\Wuchang_OS\desktop.html" >> %SCRIPT%
echo oLink.IconLocation = "C:\Windows\System32\shell32.dll, 15" >> %SCRIPT%
echo oLink.Save >> %SCRIPT%
cscript /nologo %SCRIPT%
del %SCRIPT%

echo INSTALLATION COMPLETE.
echo YOU CAN NOW LAUNCH WUCHANG OS FROM YOUR DESKTOP.
pause
