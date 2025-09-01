@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM 智能客服系统部署测试脚本 (Windows)
REM 用于验证 Docker 部署是否正常工作

set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

set TEST_COUNT=0
set PASS_COUNT=0
set FAIL_COUNT=0

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

REM 测试函数
:run_test
set "test_name=%~1"
set "test_command=%~2"
set /a TEST_COUNT+=1

call :log_info "测试 !TEST_COUNT!: %test_name%"

%test_command% >nul 2>&1
if errorlevel 1 (
    call :log_error "✗ %test_name% 失败"
    set /a FAIL_COUNT+=1
    goto :eof
) else (
    call :log_success "✓ %test_name% 通过"
    set /a PASS_COUNT+=1
)
goto :eof

REM 等待服务启动
:wait_for_service
set "url=%~1"
set "service_name=%~2"
set max_attempts=30
set attempt=1

call :log_info "等待 %service_name% 服务启动..."

:wait_loop
if %attempt% gtr %max_attempts% (
    call :log_error "%service_name% 服务启动超时"
    exit /b 1
)

curl -f -s "%url%" >nul 2>&1
if errorlevel 1 (
    echo|set /p="."
    timeout /t 2 /nobreak >nul
    set /a attempt+=1
    goto wait_loop
)

echo.
call :log_success "%service_name% 服务已启动"
goto :eof

REM 检查依赖
:check_dependencies
call :log_info "检查依赖项..."

call :run_test "Docker 可用性" "docker --version"
if !FAIL_COUNT! gtr 0 exit /b 1

call :run_test "Docker Compose 可用性" "docker-compose --version"
if !FAIL_COUNT! gtr 0 exit /b 1

call :run_test "curl 可用性" "curl --version"
if !FAIL_COUNT! gtr 0 exit /b 1

goto :eof

REM 检查项目文件
:check_project_files
call :log_info "检查项目文件..."

call :run_test "Dockerfile.backend 存在" "if exist Dockerfile.backend (exit 0) else (exit 1)"
call :run_test "Dockerfile.frontend 存在" "if exist Dockerfile.frontend (exit 0) else (exit 1)"
call :run_test "docker-compose.yml 存在" "if exist docker-compose.yml (exit 0) else (exit 1)"
call :run_test "nginx 配置文件存在" "if exist docker\nginx.conf (exit 0) else (exit 1)"
call :run_test "后端代码存在" "if exist backend\ (exit 0) else (exit 1)"
call :run_test "前端代码存在" "if exist frontend\ (exit 0) else (exit 1)"

goto :eof

REM 检查环境配置
:check_environment
call :log_info "检查环境配置..."

if not exist ".env" (
    call :log_warning ".env 文件不存在，从示例创建..."
    if exist "backend\.env.example" (
        copy "backend\.env.example" ".env" >nul
        call :log_info "请编辑 .env 文件配置 OPENAI_API_KEY"
    ) else (
        call :log_error "找不到 .env.example 文件"
        exit /b 1
    )
)

call :run_test ".env 文件存在" "if exist .env (exit 0) else (exit 1)"

REM 检查关键环境变量
findstr /C:"OPENAI_API_KEY=your-openai-api-key-here" .env >nul 2>&1
if not errorlevel 1 (
    call :log_warning "请在 .env 文件中配置有效的 OPENAI_API_KEY"
)

goto :eof

REM 构建镜像
:build_images
call :log_info "构建 Docker 镜像..."

call :run_test "构建后端镜像" "docker-compose build backend"
call :run_test "构建前端镜像" "docker-compose build frontend"

goto :eof

REM 启动服务
:start_services
call :log_info "启动服务..."

REM 清理可能存在的容器
docker-compose down >nul 2>&1

call :run_test "启动所有服务" "docker-compose up -d"

REM 等待服务启动
call :wait_for_service "http://localhost:8000/health" "后端"
call :wait_for_service "http://localhost:80/health" "前端"

goto :eof

REM 测试服务功能
:test_services
call :log_info "测试服务功能..."

REM 测试后端 API
call :run_test "后端健康检查" "curl -f http://localhost:8000/health"
call :run_test "后端 API 文档" "curl -f http://localhost:8000/docs"
call :run_test "后端 OpenAPI 规范" "curl -f http://localhost:8000/openapi.json"

REM 测试前端
call :run_test "前端健康检查" "curl -f http://localhost:80/health"
call :run_test "前端主页" "curl -f http://localhost:80/"

REM 测试 API 端点
call :run_test "聊天会话列表" "curl -f http://localhost:8000/api/chat/sessions"
call :run_test "聊天设置" "curl -f http://localhost:8000/api/chat/settings"

REM 测试容器状态
docker-compose ps backend | findstr "Up" >nul 2>&1
if not errorlevel 1 (
    call :log_success "✓ 后端容器运行 通过"
    set /a PASS_COUNT+=1
) else (
    call :log_error "✗ 后端容器运行 失败"
    set /a FAIL_COUNT+=1
)
set /a TEST_COUNT+=1

docker-compose ps frontend | findstr "Up" >nul 2>&1
if not errorlevel 1 (
    call :log_success "✓ 前端容器运行 通过"
    set /a PASS_COUNT+=1
) else (
    call :log_error "✗ 前端容器运行 失败"
    set /a FAIL_COUNT+=1
)
set /a TEST_COUNT+=1

REM 如果启用了 Redis
docker-compose ps redis | findstr "Up" >nul 2>&1
if not errorlevel 1 (
    call :run_test "Redis 容器运行" "docker-compose ps redis | findstr Up"
    call :run_test "Redis 连接" "docker-compose exec -T redis redis-cli ping | findstr PONG"
)

goto :eof

REM 测试数据持久化
:test_persistence
call :log_info "测试数据持久化..."

call :run_test "数据目录存在" "if exist data\ (exit 0) else (exit 1)"
call :run_test "日志目录存在" "if exist logs\ (exit 0) else (exit 1)"

REM 等待数据库初始化
timeout /t 5 /nobreak >nul

REM 检查数据库文件是否创建
if exist "data\chatbot.db" (
    call :log_success "✓ 数据库文件创建 通过"
    set /a PASS_COUNT+=1
) else if exist "data\chroma\" (
    call :log_success "✓ 数据库文件创建 通过"
    set /a PASS_COUNT+=1
) else (
    call :log_error "✗ 数据库文件创建 失败"
    set /a FAIL_COUNT+=1
)
set /a TEST_COUNT+=1

goto :eof

REM 测试日志
:test_logs
call :log_info "测试日志功能..."

REM 检查容器日志
docker-compose logs backend | find /c /v "" >nul 2>&1
if not errorlevel 1 (
    call :log_success "✓ 后端日志可访问 通过"
    set /a PASS_COUNT+=1
) else (
    call :log_error "✗ 后端日志可访问 失败"
    set /a FAIL_COUNT+=1
)
set /a TEST_COUNT+=1

docker-compose logs frontend | find /c /v "" >nul 2>&1
if not errorlevel 1 (
    call :log_success "✓ 前端日志可访问 通过"
    set /a PASS_COUNT+=1
) else (
    call :log_error "✗ 前端日志可访问 失败"
    set /a FAIL_COUNT+=1
)
set /a TEST_COUNT+=1

goto :eof

REM 性能测试
:performance_test
call :log_info "基础性能测试..."

REM 简单的响应时间测试
for /f %%i in ('powershell -command "Measure-Command { curl -f http://localhost:8000/health } | Select-Object -ExpandProperty TotalSeconds"') do set response_time=%%i

if defined response_time (
    call :log_info "后端响应时间: !response_time!s"
) else (
    call :log_warning "无法测量响应时间"
)

set /a TEST_COUNT+=1
set /a PASS_COUNT+=1

goto :eof

REM 清理测试环境
:cleanup
call :log_info "清理测试环境..."

if "%1"=="--keep-running" (
    call :log_info "保持服务运行状态"
) else (
    docker-compose down >nul 2>&1
    call :log_info "服务已停止"
)

goto :eof

REM 显示测试结果
:show_results
echo.
echo === 测试结果汇总 ===
echo 总测试数: !TEST_COUNT!
echo 通过: !PASS_COUNT!
echo 失败: !FAIL_COUNT!
echo.

if !FAIL_COUNT! equ 0 (
    call :log_success "🎉 所有测试通过！部署成功！"
    echo.
    echo === 访问信息 ===
    echo 前端地址: http://localhost
    echo 后端API: http://localhost:8000
    echo API文档: http://localhost:8000/docs
    echo.
    exit /b 0
) else (
    call :log_error "❌ 有 !FAIL_COUNT! 个测试失败"
    echo.
    echo 请检查以下内容:
    echo 1. Docker 和 Docker Compose 是否正确安装
    echo 2. .env 文件是否正确配置
    echo 3. 端口 80 和 8000 是否被占用
    echo 4. 查看详细日志: docker-compose logs
    echo.
    exit /b 1
)

REM 主函数
:main
echo === 智能客服系统部署测试 ===
echo 开始时间: %date% %time%
echo.

call :check_dependencies
if !FAIL_COUNT! gtr 0 goto show_results

call :check_project_files
call :check_environment
call :build_images
call :start_services
call :test_services
call :test_persistence
call :test_logs
call :performance_test

call :show_results
set result=!errorlevel!

REM 根据参数决定是否清理
if not "%1"=="--keep-running" (
    call :cleanup
)

exit /b !result!

REM 处理命令行参数
if "%1"=="--help" goto help
if "%1"=="-h" goto help
goto main

:help
echo 用法: %0 [选项]
echo.
echo 选项:
echo   --keep-running    测试完成后保持服务运行
echo   --help, -h        显示此帮助信息
echo.
pause
exit /b 0

:main
call :main %*
pause