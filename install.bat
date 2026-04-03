@echo off
echo 한국어 프로그래밍 언어 - 설치 스크립트
echo.

echo [1/2] Python 패키지 설치 중...
pip install -r requirements.txt

echo.
echo [2/2] 설치 확인...
python -c "import llvmlite; print('llvmlite 버전:', llvmlite.__version__)"

echo.
echo ========================================
echo 설치 완료!
echo ========================================
echo.
echo 사용법:
echo   python main.py examples/hello.한글
echo   python main.py --repl
echo.
pause
