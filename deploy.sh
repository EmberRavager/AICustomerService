#!/bin/bash

# 智能客服系统 Docker 部署脚本
# 作者: AI Assistant
# 版本: 1.0.0

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# 检查 Docker 和 Docker Compose
check_dependencies() {
    log_info "检查依赖项..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    log_success "依赖项检查完成"
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    
    mkdir -p data/chroma
    mkdir -p logs
    mkdir -p docker
    
    log_success "目录创建完成"
}

# 检查环境变量文件
check_env_file() {
    log_info "检查环境变量文件..."
    
    if [ ! -f ".env" ]; then
        log_warning ".env 文件不存在，从示例文件创建..."
        if [ -f "backend/.env.example" ]; then
            cp backend/.env.example .env
            log_info "请编辑 .env 文件配置必要的环境变量（如 OPENAI_API_KEY）"
        else
            log_error "找不到 .env.example 文件"
            exit 1
        fi
    fi
    
    log_success "环境变量文件检查完成"
}

# 构建镜像
build_images() {
    log_info "构建 Docker 镜像..."
    
    docker-compose build --no-cache
    
    log_success "镜像构建完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    docker-compose up -d
    
    log_success "服务启动完成"
}

# 检查服务状态
check_services() {
    log_info "检查服务状态..."
    
    sleep 10  # 等待服务启动
    
    # 检查后端服务
    if curl -f http://localhost:8000/health &> /dev/null; then
        log_success "后端服务运行正常"
    else
        log_error "后端服务启动失败"
        docker-compose logs backend
        exit 1
    fi
    
    # 检查前端服务
    if curl -f http://localhost:80/health &> /dev/null; then
        log_success "前端服务运行正常"
    else
        log_error "前端服务启动失败"
        docker-compose logs frontend
        exit 1
    fi
}

# 显示访问信息
show_access_info() {
    log_success "部署完成！"
    echo ""
    echo "=== 访问信息 ==="
    echo "前端地址: http://localhost"
    echo "后端API: http://localhost:8000"
    echo "API文档: http://localhost:8000/docs"
    echo ""
    echo "=== 管理命令 ==="
    echo "查看日志: docker-compose logs -f"
    echo "停止服务: docker-compose down"
    echo "重启服务: docker-compose restart"
    echo "查看状态: docker-compose ps"
    echo ""
}

# 主函数
main() {
    echo "=== 智能客服系统 Docker 部署脚本 ==="
    echo ""
    
    check_dependencies
    create_directories
    check_env_file
    build_images
    start_services
    check_services
    show_access_info
}

# 处理命令行参数
case "${1:-}" in
    "build")
        log_info "仅构建镜像..."
        check_dependencies
        build_images
        ;;
    "start")
        log_info "启动服务..."
        start_services
        ;;
    "stop")
        log_info "停止服务..."
        docker-compose down
        log_success "服务已停止"
        ;;
    "restart")
        log_info "重启服务..."
        docker-compose restart
        log_success "服务已重启"
        ;;
    "logs")
        docker-compose logs -f
        ;;
    "status")
        docker-compose ps
        ;;
    "clean")
        log_warning "清理所有容器和镜像..."
        docker-compose down -v --rmi all
        log_success "清理完成"
        ;;
    "")
        main
        ;;
    *)
        echo "用法: $0 [build|start|stop|restart|logs|status|clean]"
        echo ""
        echo "命令说明:"
        echo "  build   - 仅构建镜像"
        echo "  start   - 启动服务"
        echo "  stop    - 停止服务"
        echo "  restart - 重启服务"
        echo "  logs    - 查看日志"
        echo "  status  - 查看状态"
        echo "  clean   - 清理所有容器和镜像"
        echo "  (无参数) - 完整部署流程"
        exit 1
        ;;
esac