#!/bin/bash

# 智能客服系统部署测试脚本
# 用于验证 Docker 部署是否正常工作

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 测试计数器
TEST_COUNT=0
PASS_COUNT=0
FAIL_COUNT=0

# 测试函数
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_result="$3"
    
    TEST_COUNT=$((TEST_COUNT + 1))
    log_info "测试 $TEST_COUNT: $test_name"
    
    if eval "$test_command"; then
        log_success "✓ $test_name 通过"
        PASS_COUNT=$((PASS_COUNT + 1))
        return 0
    else
        log_error "✗ $test_name 失败"
        FAIL_COUNT=$((FAIL_COUNT + 1))
        return 1
    fi
}

# 等待服务启动
wait_for_service() {
    local url="$1"
    local service_name="$2"
    local max_attempts=30
    local attempt=1
    
    log_info "等待 $service_name 服务启动..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url" > /dev/null 2>&1; then
            log_success "$service_name 服务已启动"
            return 0
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    log_error "$service_name 服务启动超时"
    return 1
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖项..."
    
    run_test "Docker 可用性" "docker --version" || exit 1
    run_test "Docker Compose 可用性" "docker-compose --version" || exit 1
    run_test "curl 可用性" "curl --version" || exit 1
}

# 检查项目文件
check_project_files() {
    log_info "检查项目文件..."
    
    run_test "Dockerfile.backend 存在" "test -f Dockerfile.backend"
    run_test "Dockerfile.frontend 存在" "test -f Dockerfile.frontend"
    run_test "docker-compose.yml 存在" "test -f docker-compose.yml"
    run_test "nginx 配置文件存在" "test -f docker/nginx.conf"
    run_test "后端代码存在" "test -d backend"
    run_test "前端代码存在" "test -d frontend"
}

# 检查环境配置
check_environment() {
    log_info "检查环境配置..."
    
    if [ ! -f ".env" ]; then
        log_warning ".env 文件不存在，从示例创建..."
        if [ -f "backend/.env.example" ]; then
            cp backend/.env.example .env
            log_info "请编辑 .env 文件配置 OPENAI_API_KEY"
        else
            log_error "找不到 .env.example 文件"
            return 1
        fi
    fi
    
    run_test ".env 文件存在" "test -f .env"
    
    # 检查关键环境变量
    if grep -q "OPENAI_API_KEY=your-openai-api-key-here" .env || grep -q "OPENAI_API_KEY=$" .env; then
        log_warning "请在 .env 文件中配置有效的 OPENAI_API_KEY"
    fi
}

# 构建镜像
build_images() {
    log_info "构建 Docker 镜像..."
    
    run_test "构建后端镜像" "docker-compose build backend"
    run_test "构建前端镜像" "docker-compose build frontend"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    # 清理可能存在的容器
    docker-compose down > /dev/null 2>&1 || true
    
    run_test "启动所有服务" "docker-compose up -d"
    
    # 等待服务启动
    wait_for_service "http://localhost:8000/health" "后端"
    wait_for_service "http://localhost:80/health" "前端"
}

# 测试服务功能
test_services() {
    log_info "测试服务功能..."
    
    # 测试后端 API
    run_test "后端健康检查" "curl -f http://localhost:8000/health"
    run_test "后端 API 文档" "curl -f http://localhost:8000/docs"
    run_test "后端 OpenAPI 规范" "curl -f http://localhost:8000/openapi.json"
    
    # 测试前端
    run_test "前端健康检查" "curl -f http://localhost:80/health"
    run_test "前端主页" "curl -f http://localhost:80/"
    
    # 测试 API 端点
    run_test "聊天会话列表" "curl -f http://localhost:8000/api/chat/sessions"
    run_test "聊天设置" "curl -f http://localhost:8000/api/chat/settings"
    
    # 测试容器状态
    run_test "后端容器运行" "docker-compose ps backend | grep -q Up"
    run_test "前端容器运行" "docker-compose ps frontend | grep -q Up"
    
    # 如果启用了 Redis
    if docker-compose ps redis | grep -q Up; then
        run_test "Redis 容器运行" "docker-compose ps redis | grep -q Up"
        run_test "Redis 连接" "docker-compose exec -T redis redis-cli ping | grep -q PONG"
    fi
}

# 测试数据持久化
test_persistence() {
    log_info "测试数据持久化..."
    
    run_test "数据目录存在" "test -d data"
    run_test "日志目录存在" "test -d logs"
    
    # 检查数据库文件是否创建
    sleep 5  # 等待数据库初始化
    run_test "数据库文件创建" "test -f data/chatbot.db || test -d data/chroma"
}

# 测试日志
test_logs() {
    log_info "测试日志功能..."
    
    # 检查容器日志
    run_test "后端日志可访问" "docker-compose logs backend | wc -l | awk '{print ($1 > 0)}' | grep -q 1"
    run_test "前端日志可访问" "docker-compose logs frontend | wc -l | awk '{print ($1 > 0)}' | grep -q 1"
}

# 性能测试
performance_test() {
    log_info "基础性能测试..."
    
    # 测试响应时间
    local response_time=$(curl -o /dev/null -s -w '%{time_total}' http://localhost:8000/health)
    if (( $(echo "$response_time < 2.0" | bc -l) )); then
        log_success "✓ 后端响应时间正常 (${response_time}s)"
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        log_warning "后端响应时间较慢 (${response_time}s)"
    fi
    TEST_COUNT=$((TEST_COUNT + 1))
    
    # 测试内存使用
    local memory_usage=$(docker stats --no-stream --format "table {{.Container}}\t{{.MemUsage}}" | grep chatbot-backend | awk '{print $2}' | cut -d'/' -f1)
    if [ -n "$memory_usage" ]; then
        log_info "后端内存使用: $memory_usage"
    fi
}

# 清理测试环境
cleanup() {
    log_info "清理测试环境..."
    
    if [ "$1" = "--keep-running" ]; then
        log_info "保持服务运行状态"
    else
        docker-compose down > /dev/null 2>&1 || true
        log_info "服务已停止"
    fi
}

# 显示测试结果
show_results() {
    echo ""
    echo "=== 测试结果汇总 ==="
    echo "总测试数: $TEST_COUNT"
    echo "通过: $PASS_COUNT"
    echo "失败: $FAIL_COUNT"
    echo ""
    
    if [ $FAIL_COUNT -eq 0 ]; then
        log_success "🎉 所有测试通过！部署成功！"
        echo ""
        echo "=== 访问信息 ==="
        echo "前端地址: http://localhost"
        echo "后端API: http://localhost:8000"
        echo "API文档: http://localhost:8000/docs"
        echo ""
        return 0
    else
        log_error "❌ 有 $FAIL_COUNT 个测试失败"
        echo ""
        echo "请检查以下内容:"
        echo "1. Docker 和 Docker Compose 是否正确安装"
        echo "2. .env 文件是否正确配置"
        echo "3. 端口 80 和 8000 是否被占用"
        echo "4. 查看详细日志: docker-compose logs"
        echo ""
        return 1
    fi
}

# 主函数
main() {
    echo "=== 智能客服系统部署测试 ==="
    echo "开始时间: $(date)"
    echo ""
    
    # 捕获中断信号
    trap 'cleanup; exit 1' INT TERM
    
    check_dependencies
    check_project_files
    check_environment
    build_images
    start_services
    test_services
    test_persistence
    test_logs
    performance_test
    
    show_results
    local result=$?
    
    # 根据参数决定是否清理
    if [ "$1" != "--keep-running" ]; then
        cleanup
    fi
    
    exit $result
}

# 处理命令行参数
case "${1:-}" in
    "--help" | "-h")
        echo "用法: $0 [选项]"
        echo ""
        echo "选项:"
        echo "  --keep-running    测试完成后保持服务运行"
        echo "  --help, -h        显示此帮助信息"
        echo ""
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac