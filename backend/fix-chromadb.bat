@echo off
chcp 65001 >nul
echo ========================================
echo ChromaDB 安装修复工具
echo ========================================
echo.

cd /d "%~dp0"

echo 🔧 方案1: 尝试从 PyPI 安装预编译的轮子...
echo.

:: 设置环境变量，优先使用预编译包
set UV_PREBUILT=1

echo 📥 重新安装 chroma-hnswlib（预编译版本）...
uv pip install --force-reinstall chroma-hnswlib

if %errorlevel% equ 0 (
    echo ✅ 安装成功！
    echo.
    echo 继续同步其他依赖...
    uv sync
    
    if %errorlevel% equ 0 (
        echo.
        echo ========================================
        echo ✅ 所有依赖安装成功！
        echo ========================================
        echo.
        echo 可以运行以下命令启动服务:
        echo   uv run python main.py
        echo   或直接运行: dev.bat
        echo.
    ) else (
        echo ❌ 同步依赖失败
    )
) else (
    echo.
    echo ========================================
    echo ⚠️  预编译包安装失败
    echo ========================================
    echo.
    echo 📝 需要安装 Microsoft C++ Build Tools
    echo.
    echo 请按照以下步骤操作:
    echo.
    echo 1. 访问: https://visualstudio.microsoft.com/visual-cpp-build-tools/
    echo 2. 下载并运行安装程序
    echo 3. 选择 "使用 C++ 的桌面开发"
    echo 4. 等待安装完成（约 5-10 分钟）
    echo 5. 重启终端，再次运行此脚本
    echo.
    echo 或者使用更简单的方案:
    echo   安装 Visual Studio Community（包含所有工具）
    echo   https://visualstudio.microsoft.com/downloads/
    echo.
)

pause

