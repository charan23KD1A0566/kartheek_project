@echo off
REM deploy.bat - SIF Sentinel Deployment Script for Windows
REM Usage: deploy.bat [environment] [action]
REM Example: deploy.bat production deploy

setlocal enabledelayedexpansion

set ENVIRONMENT=%1
set ACTION=%2

if "%ENVIRONMENT%"=="" set ENVIRONMENT=local
if "%ACTION%"=="" set ACTION=deploy

for %%A in ("%CD%") do set PROJECT_DIR=%%~A

echo.
echo ===============================================
echo   SIF Sentinel Deployment Script
echo ===============================================
echo.

REM Function-like routines using labels and call
goto %ACTION%

:deploy
    echo.
    echo Deploying SIF Sentinel (%ENVIRONMENT%)...
    
    if "%ENVIRONMENT%"=="local" (
        echo Starting with local MongoDB...
        docker compose --profile local up -d
    ) else (
        echo Starting services (using MongoDB Atlas)...
        docker compose up -d --no-build
    )
    
    timeout /t 10 /nobreak
    call :health_check
    echo.
    echo Deployment completed!
    echo Frontend: http://localhost
    echo Backend API: http://localhost:8000
    echo API Docs: http://localhost:8000/docs
    goto :eof

:build
    echo.
    echo Building Docker images...
    docker compose build --no-cache
    echo Build completed!
    goto :eof

:start
    echo.
    echo Starting services...
    docker compose up -d
    timeout /t 5 /nobreak
    call :health_check
    goto :eof

:stop
    echo.
    echo Stopping services...
    docker compose down
    echo Services stopped!
    goto :eof

:restart
    echo.
    echo Restarting services...
    docker compose restart
    timeout /t 5 /nobreak
    call :health_check
    goto :eof

:logs
    echo.
    echo Showing logs (press Ctrl+C to exit)...
    docker compose logs -f
    goto :eof

:health_check
    echo.
    echo Checking service health...
    docker compose ps
    goto :eof

:shell
    echo.
    echo Opening shell in backend container...
    docker exec -it sif_sentinel_backend cmd
    goto :eof

:help
    echo.
    echo SIF Sentinel Deployment Script
    echo.
    echo Usage: deploy.bat [environment] [action]
    echo.
    echo Environments:
    echo   local       - Local development
    echo   staging     - Staging environment
    echo   production  - Production environment
    echo.
    echo Actions:
    echo   deploy      - Build and deploy services
    echo   build       - Build Docker images
    echo   start       - Start services
    echo   stop        - Stop services
    echo   restart     - Restart services
    echo   logs        - View service logs
    echo   health      - Check service health
    echo   shell       - Open shell in backend
    echo.
    echo Examples:
    echo   deploy.bat local deploy
    echo   deploy.bat production logs
    echo.
    goto :eof

:invalid
    echo Unknown action: %ACTION%
    echo Use "deploy.bat help" for usage information
    goto :eof

if "%ACTION%"=="deploy" goto deploy
if "%ACTION%"=="build" goto build
if "%ACTION%"=="start" goto start
if "%ACTION%"=="stop" goto stop
if "%ACTION%"=="restart" goto restart
if "%ACTION%"=="logs" goto logs
if "%ACTION%"=="health" goto health_check
if "%ACTION%"=="shell" goto shell
if "%ACTION%"=="help" goto help
if "%ACTION%"=="--help" goto help
if "%ACTION%"=="-h" goto help

goto invalid
