@echo off
chcp 65001 >nul
echo Testing python3 alias...

echo.
echo Testing python3 --version:
python3 --version

echo.
echo Testing basic import:
python3 -c "import sys; print(f'Python {sys.version}')"

echo.
echo If you see above results, python3 alias is working!
echo.
echo You can now use: python3 [script.py]
echo.
pause
