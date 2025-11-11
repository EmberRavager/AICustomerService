@echo off
chcp 65001 >nul
echo ========================================
echo 智能客服系统启动脚本 (UV版本)
echo ========================================
echo.

:: 检查uv是否安装
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到uv，正在自动安装...
    echo 💡 使用命令: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    if %errorlevel% neq 0 (
        echo ❌ uv安装失败，请手动安装: https://github.com/astral-sh/uv
        pause
        exit /b 1
    )
    echo ✅ uv 安装成功！
)

:: 检查Node.js是否安装
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到Node.js，请先安装Node.js 16+
    pause
    exit /b 1
)

echo ✅ uv 和 Node.js 环境检查通过
echo.

:: 检查后端依赖
echo 📦 使用 uv 管理后端依赖...
cd /d "%~dp0backend"

:: 检查环境配置文件
if not exist ".env" (
    echo 🔧 创建环境配置文件...
    copy ".env.example" ".env"
    echo ⚠️  请编辑 backend\.env 文件，配置您的API密钥等信息
    echo.
)

:: 使用 uv sync 同步依赖（比 pip install 快很多）
echo 📥 使用 uv 同步依赖...
uv sync
if %errorlevel% neq 0 (
    echo ❌ uv sync 失败
    pause
    exit /b 1
)

:: 检查前端依赖
echo 📦 检查前端依赖...
cd /d "%~dp0frontend"
if not exist "node_modules" (
    echo 📥 安装前端依赖...
    npm install
    if %errorlevel% neq 0 (
        echo ❌ 安装前端依赖失败
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo 🚀 启动智能客服系统
echo ========================================
echo.

:: 启动后端服务（使用 uv run）
echo 🔧 启动后端服务...
cd /d "%~dp0backend"
start "智能客服系统-后端" cmd /k "uv run python main.py"

:: 等待后端启动
echo ⏳ 等待后端服务启动...
timeout /t 5 /nobreak >nul

:: 启动前端服务
echo 🔧 启动前端服务...
cd /d "%~dp0frontend"
start "智能客服系统-前端" cmd /k "npm start"

echo.
echo ========================================
echo ✅ 启动完成！
echo ========================================
echo.
echo 📱 前端地址: http://localhost:1111
echo 🔧 后端API: http://localhost:8000
echo 📚 API文档: http://localhost:8000/docs
echo.
echo 💡 提示:
echo   - 首次运行请确保已配置 backend\.env 文件
echo   - 如需停止服务，请关闭对应的命令行窗口
echo   - 如遇问题，请检查日志文件
echo.
echo 按任意键退出...
pause >nul