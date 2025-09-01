@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM 智能客服系统 Docker 部署脚本 (Windows)
REM 作者: AI Assistant
REM 版本: 1.0.0

set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

REM 日志函数
:log_info
echo %BLUE%[INFO]%NC% %~1
goto :eof

:log_success
echo %GREEN%[SUCCESS]%NC% %~1
goto :eof

:log_warning
echo %YELLOW%[WARNING]%NC% %~1
goto :eof

:log_error
echo %RED%[ERROR]%NC% %~1
goto :eof

REM 检查 Docker 和 Docker Compose
:check_dependencies
call :log_info "检查依赖项..."

docker --version >nul 2>&1
if errorlevel 1 (
    call :log_error "Docker 未安装，请先安装 Docker Desktop"
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    call :log_error "Docker Compose 未安装，请先安装 Docker Compose"
    pause
    exit /b 1
)

call :log_success "依赖项检查完成"
goto :eof

REM 创建必要的目录
:create_directories
call :log_info "创建必要的目录..."

if not exist "data" mkdir data
if not exist "data\chroma" mkdir data\chroma
if not exist "logs" mkdir logs
if not exist "docker" mkdir docker

call :log_success "目录创建完成"
goto :eof

REM 检查环境变量文件
:check_env_file
call :log_info "检查环境变量文件..."

if not exist ".env" (
    call :log_warning ".env 文件不存在，从示例文件创建..."
    if exist "backend\.env.example" (
        copy "backend\.env.example" ".env" >nul
        call :log_info "请编辑 .env 文件配置必要的环境变量（如 OPENAI_API_KEY）"
    ) else (
        call :log_error "找不到 .env.example 文件"
        pause
        exit /b 1
    )
)

call :log_success "环境变量文件检查完成"
goto :eof

REM 构建镜像
:build_images
call :log_info "构建 Docker 镜像..."

docker-compose build --no-cache
if errorlevel 1 (
    call :log_error "镜像构建失败"
    pause
    exit /b 1
)

call :log_success "镜像构建完成"
goto :eof

REM 启动服务
:start_services
call :log_info "启动服务..."

docker-compose up -d
if errorlevel 1 (
    call :log_error "服务启动失败"
    pause
    exit /b 1
)

call :log_success "服务启动完成"
goto :eof

REM 检查服务状态
:check_services
call :log_info "检查服务状态..."

REM 等待服务启动
timeout /t 10 /nobreak >nul

REM 检查后端服务
curl -f http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    call :log_error "后端服务启动失败，查看日志:"
    docker-compose logs backend
    pause
    exit /b 1
) else (
    call :log_success "后端服务运行正常"
)

REM 检查前端服务
curl -f http://localhost:80/health >nul 2>&1
if errorlevel 1 (
    call :log_error "前端服务启动失败，查看日志:"
    docker-compose logs frontend
    pause
    exit /b 1
) else (
    call :log_success "前端服务运行正常"
)

goto :eof

REM 显示访问信息
:show_access_info
call :log_success "部署完成！"
echo.
echo === 访问信息 ===
echo 前端地址: http://localhost
echo 后端API: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo.
echo === 管理命令 ===
echo 查看日志: docker-compose logs -f
echo 停止服务: docker-compose down
echo 重启服务: docker-compose restart
echo 查看状态: docker-compose ps
echo.
goto :eof

REM 主函数
:main
echo === 智能客服系统 Docker 部署脚本 ===
echo.

call :check_dependencies
call :create_directories
call :check_env_file
call :build_images
call :start_services
call :check_services
call :show_access_info

echo 按任意键退出...
pause >nul
goto :eof

REM 处理命令行参数
if "%1"=="" goto main
if "%1"=="build" goto build_only
if "%1"=="start" goto start_only
if "%1"=="stop" goto stop_only
if "%1"=="restart" goto restart_only
if "%1"=="logs" goto logs_only
if "%1"=="status" goto status_only
if "%1"=="clean" goto clean_only
goto usage

:build_only
call :log_info "仅构建镜像..."
call :check_dependencies
call :build_images
pause
goto :eof

:start_only
call :log_info "启动服务..."
call :start_services
pause
goto :eof

:stop_only
call :log_info "停止服务..."
docker-compose down
call :log_success "服务已停止"
pause
goto :eof

:restart_only
call :log_info "重启服务..."
docker-compose restart
call :log_success "服务已重启"
pause
goto :eof

:logs_only
docker-compose logs -f
goto :eof

:status_only
docker-compose ps
pause
goto :eof

:clean_only
call :log_warning "清理所有容器和镜像..."
docker-compose down -v --rmi all
call :log_success "清理完成"
pause
goto :eof

:usage
echo 用法: %0 [build^|start^|stop^|restart^|logs^|status^|clean]
echo.
echo 命令说明:
echo   build   - 仅构建镜像
echo   start   - 启动服务
echo   stop    - 停止服务
echo   restart - 重启服务
echo   logs    - 查看日志
echo   status  - 查看状态
echo   clean   - 清理所有容器和镜像
echo   (无参数) - 完整部署流程
pause
exit /b 1