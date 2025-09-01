# Docker 部署指南

## 概述

本指南详细介绍如何使用 Docker 部署智能客服系统。Docker 部署具有以下优势：

- ✅ **环境一致性**: 消除"在我机器上能运行"的问题
- ✅ **快速部署**: 一键启动所有服务
- ✅ **易于管理**: 统一的容器管理
- ✅ **资源隔离**: 服务间相互独立
- ✅ **扩展性**: 易于水平扩展

## 系统要求

### 最低配置
- **CPU**: 2核心
- **内存**: 4GB RAM
- **存储**: 10GB 可用空间
- **操作系统**: Windows 10/11, macOS 10.14+, Linux

### 推荐配置
- **CPU**: 4核心或更多
- **内存**: 8GB RAM 或更多
- **存储**: 20GB 可用空间（SSD 推荐）

### 软件依赖
- **Docker**: 20.10.0 或更高版本
- **Docker Compose**: 1.29.0 或更高版本

## 安装 Docker

### Windows
1. 下载 [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
2. 运行安装程序并按照提示完成安装
3. 启动 Docker Desktop
4. 验证安装：
   ```cmd
   docker --version
   docker-compose --version
   ```

### macOS
1. 下载 [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop)
2. 拖拽到 Applications 文件夹
3. 启动 Docker Desktop
4. 验证安装：
   ```bash
   docker --version
   docker-compose --version
   ```

### Linux (Ubuntu/Debian)
```bash
# 更新包索引
sudo apt-get update

# 安装必要的包
sudo apt-get install apt-transport-https ca-certificates curl gnupg lsb-release

# 添加 Docker 官方 GPG 密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 设置稳定版仓库
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装 Docker Engine
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker --version
docker-compose --version
```

## 快速部署

### 方法一：使用部署脚本（推荐）

#### Windows
```cmd
# 克隆项目
git clone <repository-url>
cd 智能客服系统

# 运行部署脚本
deploy.bat
```

#### Linux/macOS
```bash
# 克隆项目
git clone <repository-url>
cd 智能客服系统

# 给脚本执行权限
chmod +x deploy.sh

# 运行部署脚本
./deploy.sh
```

### 方法二：手动部署

1. **准备环境变量**
   ```bash
   # 复制环境变量模板
   cp backend/.env.example .env
   
   # 编辑环境变量（重要！）
   # 至少需要配置 OPENAI_API_KEY
   nano .env  # 或使用其他编辑器
   ```

2. **构建并启动服务**
   ```bash
   # 构建镜像
   docker-compose build
   
   # 启动服务
   docker-compose up -d
   ```

3. **验证部署**
   ```bash
   # 检查服务状态
   docker-compose ps
   
   # 查看日志
   docker-compose logs -f
   ```

## 环境变量配置

### 必需配置

```env
# OpenAI API 配置（必需）
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_API_BASE=https://api.openai.com/v1

# JWT 密钥（生产环境必需）
JWT_SECRET_KEY=your-super-secret-jwt-key-here
```

### 可选配置

```env
# 应用配置
ENVIRONMENT=production
LOG_LEVEL=info
CORS_ORIGINS=http://localhost:3000,http://localhost:80

# 数据库配置
DATABASE_URL=sqlite:///./data/chatbot.db
CHROMA_PERSIST_DIRECTORY=/app/data/chroma

# Redis 配置（如果启用）
REDIS_URL=redis://redis:6379/0
REDIS_PASSWORD=

# 聊天配置
MAX_CHAT_HISTORY=50
CHAT_TIMEOUT=300
MAX_MESSAGE_LENGTH=2000

# 知识库配置
MAX_KNOWLEDGE_ITEMS=1000
KNOWLEDGE_SIMILARITY_THRESHOLD=0.7
MAX_SEARCH_RESULTS=10
```

## 服务架构

### 容器组成

1. **frontend** (Nginx + React)
   - 端口：80
   - 功能：前端界面服务
   - 健康检查：`http://localhost:80/health`

2. **backend** (FastAPI + Python)
   - 端口：8000
   - 功能：API 服务
   - 健康检查：`http://localhost:8000/health`

3. **redis** (Redis Cache)
   - 端口：6379
   - 功能：缓存服务（可选）
   - 健康检查：`redis-cli ping`

### 网络配置

- **网络名称**: `chatbot-network`
- **网络类型**: bridge
- **容器间通信**: 通过服务名访问

### 数据持久化

| 数据类型 | 宿主机路径 | 容器路径 | 说明 |
|---------|-----------|----------|------|
| 数据库文件 | `./data` | `/app/data` | SQLite 数据库 |
| 向量数据库 | `./data/chroma` | `/app/data/chroma` | ChromaDB 数据 |
| 日志文件 | `./logs` | `/app/logs` | 应用日志 |
| Redis 数据 | Docker 卷 | `/data` | Redis 持久化 |

## 管理命令

### 基本操作

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 重启所有服务
docker-compose restart

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 单独管理服务

```bash
# 重启单个服务
docker-compose restart backend
docker-compose restart frontend
docker-compose restart redis

# 查看单个服务日志
docker-compose logs backend
docker-compose logs frontend
docker-compose logs redis

# 进入容器
docker-compose exec backend bash
docker-compose exec frontend sh
docker-compose exec redis redis-cli
```

### 镜像管理

```bash
# 重新构建镜像
docker-compose build --no-cache

# 拉取最新镜像
docker-compose pull

# 删除未使用的镜像
docker image prune -a
```

### 数据管理

```bash
# 备份数据
tar -czf backup-$(date +%Y%m%d).tar.gz data/ logs/

# 清理所有数据（谨慎使用）
docker-compose down -v
rm -rf data/ logs/

# 重置数据库
docker-compose down
rm -f data/chatbot.db
docker-compose up -d
```

## 监控和日志

### 健康检查

```bash
# 检查所有服务健康状态
docker-compose ps

# 手动健康检查
curl http://localhost:80/health      # 前端
curl http://localhost:8000/health    # 后端
docker-compose exec redis redis-cli ping  # Redis
```

### 日志管理

```bash
# 实时查看所有日志
docker-compose logs -f

# 查看最近的日志
docker-compose logs --tail=100

# 查看特定时间的日志
docker-compose logs --since="2024-01-01T00:00:00"

# 导出日志
docker-compose logs > app-logs-$(date +%Y%m%d).log
```

### 性能监控

```bash
# 查看容器资源使用情况
docker stats

# 查看容器详细信息
docker-compose exec backend ps aux
docker-compose exec backend df -h
```

## 故障排除

### 常见问题

#### 1. 容器启动失败

**症状**: 容器状态显示 `Exited`

**解决方案**:
```bash
# 查看详细错误信息
docker-compose logs backend

# 检查配置文件
cat .env

# 重新构建镜像
docker-compose build --no-cache backend
docker-compose up -d backend
```

#### 2. 端口冲突

**症状**: `port is already allocated` 错误

**解决方案**:
```bash
# 查看端口占用
netstat -tulpn | grep :80
netstat -tulpn | grep :8000

# 修改 docker-compose.yml 中的端口映射
# 或停止占用端口的服务
```

#### 3. 数据库连接失败

**症状**: 数据库相关错误

**解决方案**:
```bash
# 检查数据目录权限
ls -la data/

# 重新创建数据目录
docker-compose down
rm -rf data/
mkdir -p data/chroma
docker-compose up -d
```

#### 4. API 调用失败

**症状**: OpenAI API 错误

**解决方案**:
```bash
# 检查环境变量
docker-compose exec backend env | grep OPENAI

# 测试 API 连接
docker-compose exec backend python -c "import openai; print('API Key configured')"
```

### 性能优化

#### Docker 配置优化

1. **增加内存限制**
   ```yaml
   # 在 docker-compose.yml 中添加
   services:
     backend:
       mem_limit: 2g
       memswap_limit: 2g
   ```

2. **启用 BuildKit**
   ```bash
   export DOCKER_BUILDKIT=1
   export COMPOSE_DOCKER_CLI_BUILD=1
   ```

3. **使用多阶段构建缓存**
   ```bash
   docker-compose build --build-arg BUILDKIT_INLINE_CACHE=1
   ```

#### 应用性能优化

1. **启用 Redis 缓存**
   ```env
   REDIS_URL=redis://redis:6379/0
   ENABLE_CACHE=true
   ```

2. **调整工作进程数**
   ```env
   WORKERS=4
   MAX_CONNECTIONS=100
   ```

3. **配置日志级别**
   ```env
   LOG_LEVEL=warning  # 生产环境建议使用 warning 或 error
   ```

## 生产环境部署

### 安全配置

1. **使用强密码**
   ```env
   JWT_SECRET_KEY=$(openssl rand -base64 32)
   REDIS_PASSWORD=$(openssl rand -base64 16)
   ```

2. **限制网络访问**
   ```yaml
   # 在 docker-compose.yml 中
   services:
     backend:
       ports:
         - "127.0.0.1:8000:8000"  # 仅本地访问
   ```

3. **使用 HTTPS**
   - 配置 SSL 证书
   - 使用反向代理（如 Nginx）

### 备份策略

1. **自动备份脚本**
   ```bash
   #!/bin/bash
   # backup.sh
   DATE=$(date +%Y%m%d_%H%M%S)
   tar -czf "backup_${DATE}.tar.gz" data/ logs/
   # 上传到云存储或远程服务器
   ```

2. **定期备份**
   ```bash
   # 添加到 crontab
   0 2 * * * /path/to/backup.sh
   ```

### 监控和告警

1. **健康检查脚本**
   ```bash
   #!/bin/bash
   # health_check.sh
   if ! curl -f http://localhost:80/health; then
       echo "Frontend is down!" | mail -s "Alert" admin@example.com
   fi
   ```

2. **日志监控**
   - 使用 ELK Stack 或类似工具
   - 配置错误日志告警

## 升级和维护

### 应用升级

1. **备份数据**
   ```bash
   ./backup.sh
   ```

2. **拉取新版本**
   ```bash
   git pull origin main
   ```

3. **重新构建和部署**
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

4. **验证升级**
   ```bash
   docker-compose ps
   curl http://localhost:80/health
   curl http://localhost:8000/health
   ```

### 定期维护

1. **清理 Docker 资源**
   ```bash
   # 每周执行
   docker system prune -f
   docker volume prune -f
   ```

2. **更新基础镜像**
   ```bash
   # 每月执行
   docker-compose pull
   docker-compose up -d
   ```

3. **检查日志大小**
   ```bash
   # 清理大日志文件
   find logs/ -name "*.log" -size +100M -delete
   ```

## 总结

Docker 部署为智能客服系统提供了一个稳定、可靠的运行环境。通过本指南，您应该能够：

- ✅ 成功部署和运行系统
- ✅ 进行基本的管理和维护
- ✅ 解决常见问题
- ✅ 优化系统性能
- ✅ 实施生产环境最佳实践

如果遇到问题，请参考故障排除部分或查看项目的 GitHub Issues。