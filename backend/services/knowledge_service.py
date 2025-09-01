#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库服务模块
管理知识库内容、向量检索和语义搜索
"""

import os
import json
import uuid
from typing import List, Dict, Optional, Any
from datetime import datetime
from loguru import logger

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    logger.warning("ChromaDB未安装，知识库功能将受限")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("SentenceTransformers未安装，将使用简单文本匹配")

import jieba
from models.chat_models import KnowledgeBase
from config import get_settings

class KnowledgeService:
    """知识库服务类"""
    
    def __init__(self):
        """初始化知识库服务"""
        self.settings = get_settings()
        self.data_dir = "./data/knowledge"
        self.knowledge_file = os.path.join(self.data_dir, "knowledge_base.json")
        
        # 创建必要的目录
        self._ensure_directories()
        
        # 初始化向量数据库
        self.vector_db = None
        self.embedding_model = None
        self._init_vector_components()
        
        # 加载知识库
        self.knowledge_items: List[KnowledgeBase] = []
        self._load_knowledge_base()
        
        logger.info("知识库服务初始化完成")
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            os.makedirs(self.settings.chroma_persist_directory, exist_ok=True)
            
            # 如果知识库文件不存在，创建默认知识库
            if not os.path.exists(self.knowledge_file):
                self._create_default_knowledge_base()
                
        except Exception as e:
            logger.error(f"创建目录失败: {str(e)}")
            raise
    
    def _init_vector_components(self):
        """初始化向量数据库和嵌入模型"""
        try:
            if CHROMA_AVAILABLE:
                # 初始化ChromaDB
                self.vector_db = chromadb.PersistentClient(
                    path=self.settings.chroma_persist_directory,
                    settings=ChromaSettings(anonymized_telemetry=False)
                )
                
                # 获取或创建集合
                self.collection = self.vector_db.get_or_create_collection(
                    name="knowledge_base",
                    metadata={"description": "智能客服知识库"}
                )
                
                logger.info("ChromaDB初始化成功")
            
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                # 初始化嵌入模型（使用中文模型）
                self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
                logger.info("嵌入模型初始化成功")
                
        except Exception as e:
            logger.error(f"向量组件初始化失败: {str(e)}")
            # 不抛出异常，允许系统在没有向量功能的情况下运行
    
    def _create_default_knowledge_base(self):
        """创建默认知识库"""
        try:
            default_knowledge = [
                {
                    "id": str(uuid.uuid4()),
                    "title": "欢迎使用智能客服系统",
                    "content": "欢迎使用我们的智能客服系统！我可以帮助您解答各种问题，包括产品咨询、技术支持、售后服务等。如果您有任何疑问，请随时告诉我。",
                    "category": "通用",
                    "tags": ["欢迎", "介绍", "帮助"],
                    "created_at": datetime.now().isoformat(),
                    "updated_at": None
                },
                {
                    "id": str(uuid.uuid4()),
                    "title": "产品功能介绍",
                    "content": "我们的产品具有以下主要功能：1. 智能对话：基于先进的AI技术，提供自然流畅的对话体验；2. 知识库管理：支持自定义知识库，快速检索相关信息；3. 多轮对话：支持上下文理解，维持连贯的对话；4. 个性化服务：根据用户需求提供定制化的服务体验。",
                    "category": "产品",
                    "tags": ["功能", "介绍", "产品"],
                    "created_at": datetime.now().isoformat(),
                    "updated_at": None
                },
                {
                    "id": str(uuid.uuid4()),
                    "title": "技术支持",
                    "content": "如果您在使用过程中遇到技术问题，请提供以下信息：1. 问题的详细描述；2. 出现问题的具体步骤；3. 错误信息（如有）；4. 您的操作环境。我们的技术团队会尽快为您解决问题。",
                    "category": "技术支持",
                    "tags": ["技术", "支持", "问题", "解决"],
                    "created_at": datetime.now().isoformat(),
                    "updated_at": None
                }
            ]
            
            with open(self.knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(default_knowledge, f, ensure_ascii=False, indent=2)
            
            logger.info("默认知识库创建成功")
            
        except Exception as e:
            logger.error(f"创建默认知识库失败: {str(e)}")
    
    def _load_knowledge_base(self):
        """加载知识库"""
        try:
            if os.path.exists(self.knowledge_file):
                with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                    knowledge_data = json.load(f)
                
                self.knowledge_items = []
                for item in knowledge_data:
                    try:
                        kb_item = KnowledgeBase(
                            id=item.get("id"),
                            title=item["title"],
                            content=item["content"],
                            category=item.get("category"),
                            tags=item.get("tags", []),
                            created_at=datetime.fromisoformat(item["created_at"]),
                            updated_at=datetime.fromisoformat(item["updated_at"]) if item.get("updated_at") else None
                        )
                        self.knowledge_items.append(kb_item)
                    except Exception as e:
                        logger.warning(f"解析知识库项失败: {str(e)}")
                        continue
                
                logger.info(f"知识库加载成功，共{len(self.knowledge_items)}条记录")
                
                # 如果有向量数据库，同步知识库到向量数据库
                if self.vector_db and self.embedding_model:
                    self._sync_to_vector_db()
            
        except Exception as e:
            logger.error(f"加载知识库失败: {str(e)}")
    
    def _sync_to_vector_db(self):
        """同步知识库到向量数据库"""
        try:
            if not (self.vector_db and self.embedding_model):
                return
            
            # 清空现有集合
            try:
                self.vector_db.delete_collection("knowledge_base")
            except:
                pass
            
            self.collection = self.vector_db.get_or_create_collection(
                name="knowledge_base",
                metadata={"description": "智能客服知识库"}
            )
            
            # 添加知识库项到向量数据库
            for item in self.knowledge_items:
                try:
                    # 组合标题和内容作为文档
                    document = f"{item.title}\n{item.content}"
                    
                    # 生成嵌入向量
                    embedding = self.embedding_model.encode(document).tolist()
                    
                    # 添加到集合
                    self.collection.add(
                        documents=[document],
                        embeddings=[embedding],
                        metadatas=[{
                            "id": item.id,
                            "title": item.title,
                            "category": item.category or "",
                            "tags": ",".join(item.tags)
                        }],
                        ids=[item.id]
                    )
                    
                except Exception as e:
                    logger.warning(f"同步知识库项到向量数据库失败: {str(e)}")
                    continue
            
            logger.info("知识库已同步到向量数据库")
            
        except Exception as e:
            logger.error(f"同步到向量数据库失败: {str(e)}")
    
    async def search_knowledge(self, query: str, limit: int = 5) -> List[KnowledgeBase]:
        """搜索知识库"""
        try:
            # 优先使用向量搜索
            if self.vector_db and self.embedding_model:
                return await self._vector_search(query, limit)
            else:
                # 回退到关键词搜索
                return await self._keyword_search(query, limit)
                
        except Exception as e:
            logger.error(f"知识库搜索失败: {str(e)}")
            return []
    
    async def _vector_search(self, query: str, limit: int) -> List[KnowledgeBase]:
        """向量搜索"""
        try:
            # 生成查询向量
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # 在向量数据库中搜索
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                include=["documents", "metadatas", "distances"]
            )
            
            # 转换结果
            knowledge_results = []
            if results["ids"] and results["ids"][0]:
                for i, doc_id in enumerate(results["ids"][0]):
                    # 从原始知识库中找到对应项
                    for item in self.knowledge_items:
                        if item.id == doc_id:
                            knowledge_results.append(item)
                            break
            
            logger.debug(f"向量搜索完成，找到{len(knowledge_results)}条结果")
            return knowledge_results
            
        except Exception as e:
            logger.error(f"向量搜索失败: {str(e)}")
            return []
    
    async def _keyword_search(self, query: str, limit: int) -> List[KnowledgeBase]:
        """关键词搜索"""
        try:
            # 使用jieba分词
            query_words = list(jieba.cut(query.lower()))
            query_words = [word.strip() for word in query_words if len(word.strip()) > 1]
            
            # 计算相关性得分
            scored_items = []
            for item in self.knowledge_items:
                score = self._calculate_relevance_score(item, query_words)
                if score > 0:
                    scored_items.append((item, score))
            
            # 按得分排序
            scored_items.sort(key=lambda x: x[1], reverse=True)
            
            # 返回前limit个结果
            results = [item for item, score in scored_items[:limit]]
            
            logger.debug(f"关键词搜索完成，找到{len(results)}条结果")
            return results
            
        except Exception as e:
            logger.error(f"关键词搜索失败: {str(e)}")
            return []
    
    def _calculate_relevance_score(self, item: KnowledgeBase, query_words: List[str]) -> float:
        """计算相关性得分"""
        try:
            score = 0.0
            
            # 搜索文本（标题 + 内容 + 标签）
            search_text = f"{item.title} {item.content} {' '.join(item.tags)}".lower()
            
            # 计算匹配得分
            for word in query_words:
                if word in search_text:
                    # 标题匹配权重更高
                    if word in item.title.lower():
                        score += 3.0
                    # 标签匹配权重中等
                    elif any(word in tag.lower() for tag in item.tags):
                        score += 2.0
                    # 内容匹配权重较低
                    else:
                        score += 1.0
            
            return score
            
        except Exception as e:
            logger.warning(f"计算相关性得分失败: {str(e)}")
            return 0.0
    
    async def add_knowledge_item(self, item: KnowledgeBase) -> bool:
        """添加知识库项"""
        try:
            # 生成ID（如果没有）
            if not item.id:
                item.id = str(uuid.uuid4())
            
            # 设置创建时间
            item.created_at = datetime.now()
            
            # 添加到内存列表
            self.knowledge_items.append(item)
            
            # 保存到文件
            await self._save_knowledge_base()
            
            # 如果有向量数据库，添加到向量数据库
            if self.vector_db and self.embedding_model:
                await self._add_to_vector_db(item)
            
            logger.info(f"知识库项已添加: {item.title}")
            return True
            
        except Exception as e:
            logger.error(f"添加知识库项失败: {str(e)}")
            return False
    
    async def update_knowledge_item(self, item_id: str, updated_item: KnowledgeBase) -> bool:
        """更新知识库项"""
        try:
            # 查找并更新项
            for i, item in enumerate(self.knowledge_items):
                if item.id == item_id:
                    updated_item.id = item_id
                    updated_item.created_at = item.created_at
                    updated_item.updated_at = datetime.now()
                    
                    self.knowledge_items[i] = updated_item
                    
                    # 保存到文件
                    await self._save_knowledge_base()
                    
                    # 重新同步到向量数据库
                    if self.vector_db and self.embedding_model:
                        self._sync_to_vector_db()
                    
                    logger.info(f"知识库项已更新: {updated_item.title}")
                    return True
            
            logger.warning(f"未找到要更新的知识库项: {item_id}")
            return False
            
        except Exception as e:
            logger.error(f"更新知识库项失败: {str(e)}")
            return False
    
    async def delete_knowledge_item(self, item_id: str) -> bool:
        """删除知识库项"""
        try:
            # 查找并删除项
            for i, item in enumerate(self.knowledge_items):
                if item.id == item_id:
                    deleted_item = self.knowledge_items.pop(i)
                    
                    # 保存到文件
                    await self._save_knowledge_base()
                    
                    # 从向量数据库删除
                    if self.vector_db:
                        try:
                            self.collection.delete(ids=[item_id])
                        except Exception as e:
                            logger.warning(f"从向量数据库删除失败: {str(e)}")
                    
                    logger.info(f"知识库项已删除: {deleted_item.title}")
                    return True
            
            logger.warning(f"未找到要删除的知识库项: {item_id}")
            return False
            
        except Exception as e:
            logger.error(f"删除知识库项失败: {str(e)}")
            return False
    
    async def get_all_knowledge_items(self) -> List[KnowledgeBase]:
        """获取所有知识库项"""
        return self.knowledge_items.copy()
    
    async def get_knowledge_item_by_id(self, item_id: str) -> Optional[KnowledgeBase]:
        """根据ID获取知识库项"""
        for item in self.knowledge_items:
            if item.id == item_id:
                return item
        return None
    
    async def _save_knowledge_base(self):
        """保存知识库到文件"""
        try:
            knowledge_data = []
            for item in self.knowledge_items:
                knowledge_data.append({
                    "id": item.id,
                    "title": item.title,
                    "content": item.content,
                    "category": item.category,
                    "tags": item.tags,
                    "created_at": item.created_at.isoformat(),
                    "updated_at": item.updated_at.isoformat() if item.updated_at else None
                })
            
            with open(self.knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(knowledge_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"保存知识库失败: {str(e)}")
            raise
    
    async def _add_to_vector_db(self, item: KnowledgeBase):
        """添加单个项到向量数据库"""
        try:
            if not (self.vector_db and self.embedding_model):
                return
            
            # 组合标题和内容作为文档
            document = f"{item.title}\n{item.content}"
            
            # 生成嵌入向量
            embedding = self.embedding_model.encode(document).tolist()
            
            # 添加到集合
            self.collection.add(
                documents=[document],
                embeddings=[embedding],
                metadatas=[{
                    "id": item.id,
                    "title": item.title,
                    "category": item.category or "",
                    "tags": ",".join(item.tags)
                }],
                ids=[item.id]
            )
            
        except Exception as e:
            logger.error(f"添加到向量数据库失败: {str(e)}")