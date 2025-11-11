@echo off
chcp 65001 >nul
echo ========================================
echo 后端开发快速启动 (UV)
echo ========================================
echo.

cd /d "%~dp0"

:: 检查 uv
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未安装 uv，请运行: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    pause
    exit /b 1
)

:: 检查环境配置
if not exist ".env" (
    echo ⚠️  .env 文件不存在，从示例复制...
    copy ".env.example" ".env"
    echo ✅ 请编辑 .env 文件配置 API Key
    echo.
)

:: 同步依赖
echo 📦 同步依赖...
uv sync
if %errorlevel% neq 0 (
    echo ❌ 依赖同步失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo 🚀 启动开发服务器
echo ========================================
echo.
echo 💡 提示:
echo   - API 文档: http://localhost:8000/docs
echo   - 健康检查: http://localhost:8000/api/health
echo   - 按 Ctrl+C 停止服务
echo.

:: 启动服务（自动热重载）
uv run python main.py

