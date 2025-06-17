@echo off
chcp 65001 >nul
echo ================================================
echo    Translate2 Node 转写测试脚本
echo ================================================

REM 检查参数
if "%~1"=="" (
    echo 使用方法: test_transcribe.bat ^<音频文件路径^>
    echo 示例: test_transcribe.bat test.wav
    echo 示例: test_transcribe.bat "C:\audio\test.mp3"
    pause
    exit /b 1
)

set AUDIO_FILE=%~1

REM 检查文件是否存在
if not exist "%AUDIO_FILE%" (
    echo 错误: 音频文件不存在 - %AUDIO_FILE%
    pause
    exit /b 1
)

echo 音频文件: %AUDIO_FILE%

REM 创建输出目录
if not exist "output" mkdir output

REM 生成输出文件名
for %%i in ("%AUDIO_FILE%") do set BASE_NAME=%%~ni
set OUTPUT_FILE=output\%BASE_NAME%_transcribe.json

echo 输出文件: %OUTPUT_FILE%
echo.

REM 执行转写测试
echo 开始转写测试...
python test_local_transcribe.py "%AUDIO_FILE%" -o "%OUTPUT_FILE%" -v

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ================================================
    echo 转写测试成功完成！
    echo ================================================
    echo 结果文件:
    echo   JSON: %OUTPUT_FILE%
    echo   SRT: %OUTPUT_FILE:.json=.srt%
    echo.
    echo 是否打开结果文件？(Y/N)
    set /p OPEN_RESULT=
    if /i "%OPEN_RESULT%"=="Y" (
        start "" "%OUTPUT_FILE%"
        start "" "%OUTPUT_FILE:.json=.srt%"
    )
) else (
    echo.
    echo ================================================
    echo 转写测试失败！
    echo ================================================
)

pause 