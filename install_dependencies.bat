@echo off
chcp 65001 >nul
echo ========================================
echo 한국어 프로그래밍 언어 - 의존성 설치
echo ========================================
echo.

REM Python 찾기
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
echo [오류] Python을 찾을 수 없습니다!
echo.
echo Python 설치가 필요합니다:
echo 1. https://www.python.org/downloads/ 방문
echo 2. Python 3.8 이상 다운로드
echo 3. 설치 시 "Add Python to PATH" 체크!
echo.
pause
exit /b 1

:found

echo Python 찾음: %PYTHON_CMD%
%PYTHON_CMD% --version
echo.

echo 필요한 패키지 설치 중...
echo.

echo [1/2] llvmlite 설치 중...
%PYTHON_CMD% -m pip install llvmlite
if %errorlevel% neq 0 (
    echo [경고] llvmlite 설치 실패 (LLVM 컴파일 기능 비활성화)
    echo 인터프리터 모드는 정상 작동합니다.
    echo.
)

echo [2/2] 기타 의존성 확인 중...
%PYTHON_CMD% -m pip install --upgrade pip
echo.

echo ========================================
echo 설치 완료!
echo ========================================
echo.
echo 이제 run_ide.bat를 실행하여 IDE를 시작하세요.
echo.

pause
