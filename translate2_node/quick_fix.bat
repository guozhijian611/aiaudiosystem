@echo off
chcp 65001 >nul
echo ================================================
echo    快速修复 huggingface_hub 版本问题
echo ================================================

echo 1. 卸载当前 huggingface_hub 版本...
pip uninstall -y huggingface_hub
if %ERRORLEVEL% EQU 0 (
    echo ✓ 卸载成功
) else (
    echo ✗ 卸载失败
)

echo.
echo 2. 安装兼容版本 huggingface_hub^<0.20.0...
pip install huggingface_hub^<0.20.0
if %ERRORLEVEL% EQU 0 (
    echo ✓ 安装成功
) else (
    echo ✗ 安装失败
)

echo.
echo 3. 重新安装 NeMo...
pip install --force-reinstall nemo_toolkit[asr]==2.0.0rc0
if %ERRORLEVEL% EQU 0 (
    echo ✓ NeMo 重新安装成功
) else (
    echo ✗ NeMo 重新安装失败
)

echo.
echo 4. 测试模块导入...
python -c "import nemo; from nemo.collections.asr.models.msdd_models import NeuralDiarizer; print('✓ 所有模块导入成功！')"
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ================================================
    echo 修复完成！现在可以运行转写测试:
    echo   python test_local_transcribe.py your_audio.wav
    echo   python example_transcribe.py
    echo ================================================
) else (
    echo.
    echo ================================================
    echo 修复失败，请检查错误信息
    echo ================================================
)

pause 