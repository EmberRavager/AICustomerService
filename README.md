# 🤖 智能客服系统

基于 LangChain 和 FastAPI 的现代化智能客服系统，支持自然语言对话、知识库管理和多轮对话记忆。

## ✨ 功能特性

### 🎯 核心功能
- **智能对话**: 基于 LangChain 和多种大模型的自然语言处理
- **多模型支持**: 支持 OpenAI、Google Gemini、DeepSeek、智谱AI、百川智能、通义千问、月之暗面、零一万物等多种大模型
- **模型管理**: 可视化模型切换、配置管理和连接测试
- **知识库管理**: 支持向量搜索和关键词搜索的混合检索
- **对话记忆**: 多轮对话上下文管理和会话持久化
- **会话管理**: 支持多会话切换和历史记录管理

### 🛠️ 技术特性
- **前后端分离**: React + TypeScript 前端，FastAPI 后端
- **现代化UI**: 基于 Ant Design 的响应式界面
- **向量数据库**: ChromaDB 支持的语义搜索
- **异步处理**: 全异步架构，高性能并发处理
- **类型安全**: TypeScript 和 Pydantic 提供完整类型支持

## 🏗️ 系统架构

```
智能客服系统/
├── frontend/                 # React 前端应用
│   ├── src/
│   │   ├── components/       # 可复用组件
│   │   ├── pages/           # 页面组件
│   │   ├── services/        # API 服务
│   │   ├── types/           # TypeScript 类型定义
│   │   └── ...
│   ├── public/              # 静态资源
│   └── package.json         # 前端依赖配置
├── backend/                 # FastAPI 后端应用
│   ├── services/            # 业务逻辑服务
│   │   ├── chat_service.py  # 聊天服务
│   │   ├── memory_service.py # 记忆管理服务
│   │   └── knowledge_service.py # 知识库服务
│   ├── models/              # 数据模型
│   ├── routes.py            # API 路由
│   ├── config.py            # 配置管理
│   ├── main.py              # 应用入口
│   └── requirements.txt     # 后端依赖
├── data/                    # 数据存储目录
├── logs/                    # 日志文件
└── start.bat               # 一键启动脚本
```

## 🚀 快速开始

### 环境要求

- **Python**: 3.8+
- **Node.js**: 16+
- **npm**: 8+
- **Docker**: 20.10+ (可选，用于容器化部署)
- **Docker Compose**: 1.29+ (可选)

### 🔒 Git 配置和安全说明

#### 敏感文件保护

项目已配置 `.gitignore` 文件，确保以下敏感文件不会被提交到版本控制：

- **环境配置文件**: `.env`, `backend/.env` 等
- **数据库文件**: `backend/data/chroma_db/`, `backend/data/memory/`
- **日志文件**: `backend/logs/`, `*.log`
- **上传文件**: `backend/uploads/`
- **Python 缓存**: `__pycache__/`, `*.pyc`
- **Node.js 依赖**: `node_modules/`
- **构建文件**: `frontend/build/`, `frontend/dist/`

#### 首次设置建议

1. **检查 git 状态**：
   ```bash
   git status
   ```

2. **如果发现敏感文件已被跟踪，移除它们**：
   ```bash
   git rm --cached .env
   git rm --cached -r backend/data/chroma_db/
   git rm --cached -r backend/logs/
   ```

3. **提交 .gitignore 更改**：
   ```bash
   git add .gitignore
   git commit -m "Add .gitignore to protect sensitive files"
   ```

#### ⚠️ 重要提醒

- **永远不要提交包含真实 API 密钥的 `.env` 文件**
- **使用 `.env.example` 作为配置模板**
- **定期检查 `git status` 确保敏感文件未被跟踪**
- **团队成员应各自配置自己的 `.env` 文件**

### Docker 部署（推荐）

#### 使用部署脚本（推荐）

**Linux/macOS:**
```bash
# 给脚本执行权限
chmod +x deploy.sh

# 完整部署
./deploy.sh

# 或使用特定命令
./deploy.sh build   # 仅构建镜像
./deploy.sh start   # 启动服务
./deploy.sh stop    # 停止服务
./deploy.sh logs    # 查看日志
```

**Windows:**
```cmd
REM 完整部署
deploy.bat

REM 或使用特定命令
deploy.bat build   # 仅构建镜像
deploy.bat start   # 启动服务
deploy.bat stop    # 停止服务
deploy.bat logs    # 查看日志
```

#### 手动 Docker 部署

1. **确保已安装 Docker 和 Docker Compose**
2. **复制环境变量文件：**
   ```bash
   cp backend/.env.example .env
   ```
3. **编辑 `.env` 文件，配置必要的环境变量（如 OPENAI_API_KEY）**
4. **构建并启动服务：**
   ```bash
   docker-compose up -d --build
   ```
5. **访问应用：**
   - 前端界面: http://localhost
   - 后端API: http://localhost:8000
   - API文档: http://localhost:8000/docs

#### 部署测试

为了验证部署是否成功，可以运行测试脚本：

**Linux/macOS:**
```bash
# 给脚本执行权限
chmod +x test-deployment.sh

# 运行测试（测试完成后自动清理）
./test-deployment.sh

# 运行测试并保持服务运行
./test-deployment.sh --keep-running
```

**Windows:**
```cmd
REM 运行测试（测试完成后自动清理）
test-deployment.bat

REM 运行测试并保持服务运行
test-deployment.bat --keep-running
```

测试脚本会自动验证：
- ✅ 依赖项检查（Docker、Docker Compose、curl）
- ✅ 项目文件完整性
- ✅ 环境配置
- ✅ 镜像构建
- ✅ 服务启动
- ✅ API 功能测试
- ✅ 数据持久化
- ✅ 日志功能
- ✅ 基础性能测试

### 传统部署

#### 一键启动（推荐）

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd 智能客服系统
   ```

2. **配置环境变量**
   ```bash
   cd backend
   copy .env.example .env
   # 编辑 .env 文件，填入您的 OpenAI API Key
   ```

3. **一键启动**
   ```bash
   # Windows
   start.bat
   
   # 或者双击 start.bat 文件
   ```

启动脚本会自动：
- 创建 Python 虚拟环境
- 安装所有依赖
- 启动后端和前端服务

#### 手动启动

**后端启动**

1. **创建虚拟环境**
   ```bash
   cd backend
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置环境变量**
   ```bash
   copy .env.example .env
   # 编辑 .env 文件
   ```

4. **启动后端服务**
   ```bash
   python main.py
   ```

**前端启动**

1. **安装依赖**
   ```bash
   cd frontend
   npm install
   ```

2. **启动前端服务**
   ```bash
   npm start
   ```

### 访问应用

- **前端应用**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/api/health

## ⚙️ 配置说明

### 环境变量配置

主要配置项（在 `backend/.env` 文件中）：

```env
# OpenAI API 配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7

# 应用配置
DEBUG=true
HOST=0.0.0.0
PORT=8000

# 数据库配置
DATABASE_URL=sqlite:///./data/chatbot.db
CHROMA_PERSIST_DIRECTORY=./data/chroma_db
```

完整配置说明请参考 `backend/.env.example` 文件。

## 📚 API 文档

### 主要 API 端点

#### 聊天相关
- `POST /api/chat/` - 发送聊天消息
- `GET /api/chat/history` - 获取聊天历史
- `DELETE /api/chat/history/{session_id}` - 清除聊天历史
- `GET /api/chat/sessions` - 获取会话列表
- `POST /api/chat/sessions` - 创建新会话

#### 知识库相关
- `GET /api/knowledge/` - 搜索知识库
- `POST /api/knowledge/` - 添加知识
- `PUT /api/knowledge/{id}` - 更新知识
- `DELETE /api/knowledge/{id}` - 删除知识

#### 系统相关
- `GET /api/health` - 健康检查

详细的 API 文档可在启动后访问 http://localhost:8000/docs 查看。

## 🎨 前端功能

### 主要组件

- **ChatPage**: 主聊天界面
- **ChatMessage**: 消息显示组件
- **ChatHistory**: 会话历史管理
- **Header/Footer**: 页面布局组件

### 功能特性

- 📱 响应式设计，支持移动端
- 🌙 暗色主题支持
- 💬 实时消息显示
- 📋 消息复制功能
- 🔄 会话切换和管理
- 📊 消息状态指示

## 🔧 开发指南

### 项目结构说明

#### 后端结构

```
backend/
├── services/           # 业务逻辑层
│   ├── chat_service.py    # 聊天核心逻辑
│   ├── memory_service.py  # 记忆管理
│   └── knowledge_service.py # 知识库管理
├── models/            # 数据模型
│   └── chat_models.py    # Pydantic 模型
├── routes.py          # API 路由定义
├── config.py          # 配置管理
└── main.py           # 应用入口
```

#### 前端结构

```
frontend/src/
├── components/        # 可复用组件
├── pages/            # 页面组件
├── services/         # API 服务层
├── types/           # TypeScript 类型
└── styles/          # 样式文件
```

### 代码规范

- **后端**: 遵循 PEP 8 Python 代码规范
- **前端**: 使用 ESLint 和 Prettier 格式化
- **注释**: 所有函数和类都有详细的文档字符串
- **类型**: 使用 TypeScript 和 Pydantic 确保类型安全

### 添加新功能

1. **后端新功能**:
   - 在 `services/` 中添加业务逻辑
   - 在 `models/` 中定义数据模型
   - 在 `routes.py` 中添加 API 端点

2. **前端新功能**:
   - 在 `components/` 中创建可复用组件
   - 在 `services/` 中添加 API 调用
   - 在 `types/` 中定义 TypeScript 类型

## Docker 管理命令

### 常用命令

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
docker-compose logs backend  # 仅查看后端日志
docker-compose logs frontend # 仅查看前端日志

# 重启服务
docker-compose restart
docker-compose restart backend  # 仅重启后端
docker-compose restart frontend # 仅重启前端

# 停止服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v

# 重新构建镜像
docker-compose build --no-cache

# 进入容器
docker-compose exec backend bash
docker-compose exec frontend sh
```

### 数据持久化

- **数据库文件**: `./data/chatbot.db`
- **向量数据库**: `./data/chroma/`
- **日志文件**: `./logs/`
- **Redis数据**: Docker 数据卷 `chatbot-redis-data`

## 🐛 故障排除

### Docker 相关问题

1. **容器启动失败**
   ```bash
   # 查看详细日志
   docker-compose logs backend
   docker-compose logs frontend
   
   # 检查容器状态
   docker-compose ps
   ```

2. **端口冲突**
   - 修改 `docker-compose.yml` 中的端口映射
   - 或停止占用端口的其他服务

3. **镜像构建失败**
   ```bash
   # 清理 Docker 缓存
   docker system prune -a
   
   # 重新构建
   docker-compose build --no-cache
   ```

4. **数据丢失**
   - 检查数据卷挂载是否正确
   - 确保 `./data` 目录权限正确

### 传统部署问题

1. **OpenAI API 错误**
   - 检查 API Key 是否正确配置
   - 确认账户有足够的额度
   - 检查网络连接

2. **依赖安装失败**
   - 确保 Python 和 Node.js 版本符合要求
   - 尝试清除缓存后重新安装
   - 检查网络连接和代理设置

3. **端口占用**
   - 检查 3000 和 8000 端口是否被占用
   - 修改配置文件中的端口设置

4. **数据库问题**
   - 检查 `data/` 目录权限
   - 删除数据库文件重新初始化

### 性能优化

1. **Docker 性能优化**
   - 增加 Docker 内存限制
   - 使用 SSD 存储 Docker 数据
   - 启用 Docker BuildKit

2. **应用性能优化**
   - 配置 Redis 缓存
   - 调整数据库连接池大小
   - 启用 Nginx gzip 压缩

### 日志查看

- **后端日志**: `logs/app.log`
- **前端日志**: 浏览器开发者工具控制台
- **Docker日志**: `docker-compose logs`

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [LangChain](https://langchain.com/) - 强大的 LLM 应用开发框架
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的 Python Web 框架
- [React](https://reactjs.org/) - 用户界面构建库
- [Ant Design](https://ant.design/) - 企业级 UI 设计语言
- [ChromaDB](https://www.trychroma.com/) - 向量数据库

## 📞 支持

如果您在使用过程中遇到问题，请：

1. 查看本文档的故障排除部分
2. 检查 [Issues](../../issues) 中是否有类似问题
3. 创建新的 Issue 描述您的问题

---

**Happy Coding! 🚀**#   A I C u s t o m e r S e r v i c e 
 
 