/**
 * 聊天相关的TypeScript类型定义
 */

/**
 * 消息类型
 */
export type MessageType = 'user' | 'assistant' | 'system';

/**
 * 聊天消息接口
 */
export interface ChatMessage {
  /** 消息唯一标识 */
  id: string;
  /** 消息内容 */
  content: string;
  /** 消息类型 */
  type: MessageType;
  /** 消息时间戳 */
  timestamp: Date;
  /** 会话ID */
  sessionId: string;
  /** 是否为错误消息 */
  isError?: boolean;
  /** 是否正在流式传输 */
  isStreaming?: boolean;
  /** 消息元数据 */
  metadata?: {
    /** 使用的token数量 */
    tokensUsed?: number;
    /** 使用的模型 */
    modelUsed?: string;
    /** 置信度 */
    confidence?: number;
    /** 响应时间(毫秒) */
    responseTime?: number;
  };
}

/**
 * 聊天会话接口
 */
export interface ChatSession {
  /** 会话唯一标识 */
  id: string;
  /** 会话标题 */
  title?: string;
  /** 最后一条消息内容 */
  lastMessage?: string;
  /** 消息数量 */
  messageCount?: number;
  /** 创建时间 */
  createdAt: Date;
  /** 更新时间 */
  updatedAt: Date;
  /** 用户ID */
  userId?: string;
  /** 会话状态 */
  status?: 'active' | 'archived' | 'deleted';
  /** 会话标签 */
  tags?: string[];
}

/**
 * 聊天请求接口
 */
export interface ChatRequest {
  /** 用户消息 */
  message: string;
  /** 会话ID */
  session_id: string;
  /** 用户ID */
  user_id: string;
  /** 消息上下文 */
  context?: {
    /** 历史消息数量限制 */
    historyLimit?: number;
    /** 是否包含系统消息 */
    includeSystem?: boolean;
    /** 自定义参数 */
    customParams?: Record<string, any>;
  };
}

/**
 * 聊天响应接口
 */
export interface ChatResponse {
  /** AI回复消息 */
  message: string;
  /** 会话ID */
  session_id: string;
  /** 响应时间戳 */
  timestamp: string;
  /** 使用的token数量 */
  tokens_used?: number;
  /** 使用的模型 */
  model_used?: string;
  /** 置信度 */
  confidence?: number;
  /** 响应时间(毫秒) */
  response_time?: number;
  /** 错误信息 */
  error?: string;
  /** 状态码 */
  status?: 'success' | 'error' | 'warning';
}

/**
 * 聊天历史记录接口
 */
export interface ChatHistoryItem {
  /** 记录ID */
  id?: string;
  /** 消息内容 */
  content: string;
  /** 消息类型 */
  message_type: MessageType;
  /** 时间戳 */
  timestamp: string;
  /** 会话ID */
  session_id: string;
  /** 用户ID */
  user_id?: string;
  /** 消息元数据 */
  metadata?: Record<string, any>;
}

/**
 * 聊天设置接口
 */
export interface ChatSettings {
  /** 模型名称 */
  model?: string;
  /** 温度参数 */
  temperature?: number;
  /** 最大token数 */
  maxTokens?: number;
  /** 系统提示 */
  systemPrompt?: string;
  /** 历史消息限制 */
  historyLimit?: number;
  /** 是否启用流式响应 */
  streamResponse?: boolean;
  /** 自动保存设置 */
  autoSave?: boolean;
  /** 主题设置 */
  theme?: 'light' | 'dark' | 'auto';
  /** 语言设置 */
  language?: 'zh-CN' | 'en-US';
}

/**
 * API响应基础接口
 */
export interface ApiResponse<T = any> {
  /** 响应数据 */
  data?: T;
  /** 响应消息 */
  message?: string;
  /** 状态码 */
  code?: number;
  /** 是否成功 */
  success?: boolean;
  /** 错误详情 */
  error?: {
    code: string;
    message: string;
    details?: any;
  };
  /** 时间戳 */
  timestamp?: string;
}

/**
 * 分页参数接口
 */
export interface PaginationParams {
  /** 页码 */
  page?: number;
  /** 每页数量 */
  pageSize?: number;
  /** 排序字段 */
  sortBy?: string;
  /** 排序方向 */
  sortOrder?: 'asc' | 'desc';
}

/**
 * 分页响应接口
 */
export interface PaginatedResponse<T> {
  /** 数据列表 */
  items: T[];
  /** 总数量 */
  total: number;
  /** 当前页码 */
  page: number;
  /** 每页数量 */
  pageSize: number;
  /** 总页数 */
  totalPages: number;
  /** 是否有下一页 */
  hasNext: boolean;
  /** 是否有上一页 */
  hasPrev: boolean;
}

/**
 * 知识库条目接口
 */
export interface KnowledgeItem {
  /** 条目ID */
  id: string;
  /** 标题 */
  title: string;
  /** 内容 */
  content: string;
  /** 分类 */
  category?: string;
  /** 标签 */
  tags?: string[];
  /** 创建时间 */
  createdAt: Date;
  /** 更新时间 */
  updatedAt: Date;
  /** 相关性评分 */
  relevanceScore?: number;
}

/**
 * 用户信息接口
 */
export interface UserInfo {
  /** 用户ID */
  id: string;
  /** 用户名 */
  username?: string;
  /** 昵称 */
  nickname?: string;
  /** 头像URL */
  avatar?: string;
  /** 邮箱 */
  email?: string;
  /** 角色 */
  role?: 'user' | 'admin' | 'guest';
  /** 创建时间 */
  createdAt?: Date;
  /** 最后登录时间 */
  lastLoginAt?: Date;
}

/**
 * 系统状态接口
 */
export interface SystemStatus {
  /** 服务状态 */
  status: 'healthy' | 'degraded' | 'down';
  /** 版本信息 */
  version: string;
  /** 启动时间 */
  uptime: number;
  /** 内存使用情况 */
  memory?: {
    used: number;
    total: number;
    percentage: number;
  };
  /** CPU使用情况 */
  cpu?: {
    usage: number;
  };
  /** 数据库状态 */
  database?: {
    status: 'connected' | 'disconnected';
    responseTime?: number;
  };
  /** AI服务状态 */
  aiService?: {
    status: 'available' | 'unavailable';
    model: string;
    responseTime?: number;
  };
}

/**
 * 错误类型枚举
 */
export enum ErrorType {
  NETWORK_ERROR = 'NETWORK_ERROR',
  API_ERROR = 'API_ERROR',
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  AUTH_ERROR = 'AUTH_ERROR',
  RATE_LIMIT_ERROR = 'RATE_LIMIT_ERROR',
  UNKNOWN_ERROR = 'UNKNOWN_ERROR'
}

/**
 * 自定义错误接口
 */
export interface CustomError {
  type: ErrorType;
  message: string;
  code?: string | number;
  details?: any;
  timestamp: Date;
}