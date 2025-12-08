@echo off
chcp 65001 > nul
echo ========================================
echo 프로젝트 뷰어/에디터 실행
echo ========================================
echo.

cd /d "%~dp0"

REM Python 설치 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo [오류] Python이 설치되어 있지 않습니다.
    echo Python을 설치한 후 다시 시도해주세요.
    echo.
    pause
    exit /b 1
)

echo [확인] Python 버전:
python --version
echo.

REM 프로젝트 경로 확인
if not exist "..\001_gym_romance" (
    echo [경고] 기본 프로젝트 폴더를 찾을 수 없습니다: ..\001_gym_romance
    echo.
    set /p PROJECT_PATH="프로젝트 폴더 경로를 입력하세요 (예: ../001_gym_romance): "
) else (
    set PROJECT_PATH=../001_gym_romance
    echo [확인] 프로젝트 폴더: %PROJECT_PATH%
)
echo.

echo [실행] 프로젝트 뷰어/에디터를 시작합니다...
echo.
python main.py --project %PROJECT_PATH%

if errorlevel 1 (
    echo.
    echo [오류] 프로그램 실행 중 오류가 발생했습니다.
    echo 위의 오류 메시지를 확인해주세요.
)

echo.
pause
