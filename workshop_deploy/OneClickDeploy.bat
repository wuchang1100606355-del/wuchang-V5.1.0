@echo off
echo Starting Workshop Sister Deployment...

cd /d "%~dp0"

echo Building Docker Image...
docker build -t workshop-sister .

echo Waking up Sister (Running Container)...
echo Attempting to bind to port 8085 (to avoid conflict with 8080)...
docker rm -f my-workshop-sister
docker run -d -p 8085:8080 -v "%cd%":/app --name my-workshop-sister workshop-sister

echo Deployment Complete. Sister is running on port 8085.
pause
