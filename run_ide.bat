@echo off
chcp 65001 >nul
echo ========================================
echo KRP IDE v2.0
echo ========================================
echo.

REM Python 경로 찾기
set PYTHON_CMD=

REM 1. 기본 python 명령어 확인
where python >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    goto :found
)

REM 2. py launcher 확인 (Windows Python Launcher)
where py >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py
    goto :found
)

REM 3. 일반적인 설치 경로 확인
for %%P in (
    "C:\Python312\python.exe"
    "C:\Python311\python.exe"
    "C:\Python310\python.exe"
    "C:\Python39\python.exe"
    "C:\Python38\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python39\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python38\python.exe"
) do (
    if exist %%P (
        set PYTHON_CMD=%%P
        goto :found
    )
)

REM Python을 찾지 못함
:notfound
echo [오류] Python을 찾을 수 없습니다!
echo.
echo Python 설치가 필요합니다:
echo 1. https://www.python.org/downloads/ 방문
echo 2. Python 3.8 이상 다운로드
echo 3. 설치 시 "Add Python to PATH" 체크!
echo.
echo 또는 Microsoft Store에서 Python 설치:
echo - Windows 키 누르기
echo - "Microsoft Store" 검색
echo - "Python 3.12" 검색 및 설치
echo.
pause
exit /b 1

:found
echo Python 찾음: %PYTHON_CMD%
echo.

REM Python 버전 확인
%PYTHON_CMD% --version
echo.

REM 의존성 확인
echo 의존성 확인 중...
%PYTHON_CMD% -c "import tkinter" 2>nul
if %errorlevel% neq 0 (
    echo [경고] tkinter가 설치되지 않았습니다.
    echo Python을 재설치하거나 tkinter 패키지를 설치하세요.
    echo.
    pause
    exit /b 1
)

echo 모든 의존성 확인 완료!
echo.
echo IDE 시작 중...
echo.

REM IDE 실행
%PYTHON_CMD% ide.py

if %errorlevel% neq 0 (
    echo.
    echo [오류] IDE 실행 중 오류가 발생했습니다.
    echo.
)

pause
