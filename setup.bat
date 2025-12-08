@echo off
chcp 65001 > nul
echo ========================================
echo 프로젝트 뷰어/에디터 초기 설정
echo ========================================
echo.

cd /d "%~dp0"

REM Python 설치 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo [오류] Python이 설치되어 있지 않습니다.
    echo.
    echo Python 3.8 이상을 설치해주세요:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [확인] Python 버전:
python --version
echo.

echo ========================================
echo 필수 패키지 설치
echo ========================================
echo.

echo [설치] tkinter 확인...
python -c "import tkinter" 2>nul
if errorlevel 1 (
    echo [경고] tkinter가 설치되어 있지 않습니다.
    echo tkinter는 Python 설치 시 포함되어야 합니다.
    echo Python을 재설치할 때 "tcl/tk and IDLE" 옵션을 선택해주세요.
    echo.
) else (
    echo [확인] tkinter 설치됨
)

echo.
echo [설치] 기본 패키지...
pip install --upgrade pip
echo.

REM LLM 제공자별 패키지는 선택적으로 설치
echo ========================================
echo LLM 제공자 선택
echo ========================================
echo.
echo 사용할 LLM 제공자를 선택하세요:
echo 1. Gemini (Google)
echo 2. OpenAI (ChatGPT)
echo 3. Anthropic (Claude)
echo 4. 모두 설치
echo 5. 나중에 설치
echo.
set /p LLM_CHOICE="선택 (1-5): "

if "%LLM_CHOICE%"=="1" goto :install_gemini
if "%LLM_CHOICE%"=="2" goto :install_openai
if "%LLM_CHOICE%"=="3" goto :install_anthropic
if "%LLM_CHOICE%"=="4" goto :install_all
if "%LLM_CHOICE%"=="5" goto :skip_llm
goto :skip_llm

:install_gemini
echo.
echo [설치] Gemini (google-generativeai)...
pip install google-generativeai
goto :after_llm

:install_openai
echo.
echo [설치] OpenAI...
pip install openai
goto :after_llm

:install_anthropic
echo.
echo [설치] Anthropic (Claude)...
pip install anthropic
goto :after_llm

:install_all
echo.
echo [설치] 모든 LLM 제공자...
pip install google-generativeai openai anthropic
goto :after_llm

:skip_llm
echo.
echo [건너뜀] LLM 패키지 설치를 건너뜁니다.
echo 나중에 필요할 때 다음 명령으로 설치할 수 있습니다:
echo   pip install google-generativeai  (Gemini용)
echo   pip install openai                (OpenAI용)
echo   pip install anthropic             (Anthropic용)
goto :after_llm

:after_llm
echo.

echo ========================================
echo 구글 시트 패키지 설치
echo ========================================
echo.
echo 구글 시트 내보내기 기능을 사용하시겠습니까?
echo 1. 설치
echo 2. 나중에 설치
echo.
set /p SHEETS_CHOICE="선택 (1-2): "

if "%SHEETS_CHOICE%"=="1" goto :install_sheets
goto :skip_sheets

:install_sheets
echo.
echo [설치] 구글 시트 패키지...
pip install gspread google-auth google-auth-oauthlib google-auth-httplib2
goto :after_sheets

:skip_sheets
echo.
echo [건너뜀] 구글 시트 패키지 설치를 건너뜁니다.
echo 나중에 필요할 때 다음 명령으로 설치할 수 있습니다:
echo   pip install gspread google-auth google-auth-oauthlib google-auth-httplib2
goto :after_sheets

:after_sheets
echo.

echo ========================================
echo 테스트 실행
echo ========================================
echo.

echo [테스트] 기본 모듈 import...
python -c "from config.config_manager import ConfigManager; print('[OK] ConfigManager')"
if errorlevel 1 (
    echo [오류] 모듈 import 실패
    goto :setup_error
)

python -c "from models.project_data import ProjectData; print('[OK] ProjectData')"
if errorlevel 1 (
    echo [오류] 모듈 import 실패
    goto :setup_error
)

python -c "from services.file_service import FileService; print('[OK] FileService')"
if errorlevel 1 (
    echo [오류] 모듈 import 실패
    goto :setup_error
)

echo.

echo ========================================
echo 설정 완료!
echo ========================================
echo.
echo 초기 설정이 완료되었습니다.
echo.
echo 다음 단계:
echo 1. test.bat - 전체 테스트 실행
echo 2. run.bat  - 프로그램 실행
echo.
pause
exit /b 0

:setup_error
echo.
echo [오류] 설정 중 오류가 발생했습니다.
echo 위의 오류 메시지를 확인하고 다시 시도해주세요.
echo.
pause
exit /b 1
