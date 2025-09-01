import axios, { AxiosInstance, AxiosResponse } from 'axios';
import {
  ChatRequest,
  ChatResponse,
  ChatHistoryItem,
  ChatSession,
  ChatSettings,
  ApiResponse,
  PaginationParams,
  PaginatedResponse,
  SystemStatus,
  ErrorType,
  CustomError
} from '../types/chat';

/**
 * 聊天服务类
 * 负责与后端API进行通信，处理聊天相关的所有请求
 */

class ChatService {
  private api: AxiosInstance;
  private baseURL: string;
  
  constructor() {
    // 从环境变量或配置中获取API基础URL
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    
    // 创建axios实例
    this.api = axios.create({
      baseURL: this.baseURL,
      timeout: 30000, // 30秒超时
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    // 设置请求拦截器
    this.setupRequestInterceptor();
    
    // 设置响应拦截器
    this.setupResponseInterceptor();
  }
  
  /**
   * 设置请求拦截器
   */
  private setupRequestInterceptor(): void {
    this.api.interceptors.request.use(
      (config) => {
        // 添加认证token（如果有）
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        
        // 添加请求ID用于追踪
        config.headers['X-Request-ID'] = this.generateRequestId();
        
        console.log('发送请求:', config.method?.toUpperCase(), config.url);
        return config;
      },
      (error) => {
        console.error('请求拦截器错误:', error);
        return Promise.reject(this.createCustomError(ErrorType.NETWORK_ERROR, '请求配置错误', error));
      }
    );
  }
  
  /**
   * 设置响应拦截器
   */
  private setupResponseInterceptor(): void {
    this.api.interceptors.response.use(
      (response: AxiosResponse) => {
        console.log('收到响应:', response.status, response.config.url);
        return response;
      },
      (error) => {
        console.error('响应错误:', error);
        
        if (error.response) {
          // 服务器响应了错误状态码
          const { status, data } = error.response;
          
          switch (status) {
            case 400:
              return Promise.reject(this.createCustomError(ErrorType.VALIDATION_ERROR, '请求参数错误', data));
            case 401:
              return Promise.reject(this.createCustomError(ErrorType.AUTH_ERROR, '未授权访问', data));
            case 429:
              return Promise.reject(this.createCustomError(ErrorType.RATE_LIMIT_ERROR, '请求过于频繁', data));
            case 500:
              return Promise.reject(this.createCustomError(ErrorType.API_ERROR, '服务器内部错误', data));
            default:
              return Promise.reject(this.createCustomError(ErrorType.API_ERROR, `服务器错误 (${status})`, data));
          }
        } else if (error.request) {
          // 请求已发送但没有收到响应
          return Promise.reject(this.createCustomError(ErrorType.NETWORK_ERROR, '网络连接失败', error));
        } else {
          // 其他错误
          return Promise.reject(this.createCustomError(ErrorType.UNKNOWN_ERROR, '未知错误', error));
        }
      }
    );
  }
  
  /**
   * 生成请求ID
   */
  private generateRequestId(): string {
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
  
  /**
   * 创建自定义错误
   */
  private createCustomError(type: ErrorType, message: string, details?: any): CustomError {
    return {
      type,
      message,
      details,
      timestamp: new Date()
    };
  }
  
  /**
   * 发送聊天消息
   */
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    try {
      const response = await this.api.post<ApiResponse<ChatResponse>>('/api/chat', request);
      
      if (response.data.success && response.data.data) {
        return response.data.data;
      } else {
        throw this.createCustomError(
          ErrorType.API_ERROR,
          response.data.message || '发送消息失败',
          response.data.error
        );
      }
    } catch (error) {
      console.error('发送消息失败:', error);
      throw error;
    }
  }
  
  /**
   * 流式发送聊天消息
   */
  async sendMessageStream(
    request: ChatRequest,
    onChunk: (chunk: string) => void,
    onComplete: (fullContent: string) => void,
    onError: (error: string) => void
  ): Promise<void> {
    try {
      const response = await fetch(`${this.baseURL}/api/chat/stream`, {
         method: 'POST',
         headers: {
           'Content-Type': 'application/json',
         },
         body: JSON.stringify(request),
       });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('无法获取响应流');
      }

      const decoder = new TextDecoder();
      let fullContent = '';

      try {
        while (true) {
          const { done, value } = await reader.read();
          
          if (done) {
            break;
          }

          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.trim() === '') continue;
            
            try {
              const data = JSON.parse(line);
              
              if (data.type === 'content') {
                onChunk(data.content);
                fullContent += data.content;
              } else if (data.type === 'done') {
                onComplete(fullContent);
                return;
              } else if (data.type === 'error') {
                onError(data.error);
                return;
              }
            } catch (parseError) {
              console.warn('解析流数据失败:', parseError);
            }
          }
        }
      } finally {
        reader.releaseLock();
      }
    } catch (error: any) {
      console.error('流式发送消息失败:', error);
      onError(error.message || '网络请求失败，请检查网络连接');
    }
  }
  
  /**
   * 获取聊天历史
   */
  async getChatHistory(
    sessionId: string,
    pagination?: PaginationParams
  ): Promise<ChatHistoryItem[]> {
    try {
      const params = {
        session_id: sessionId,
        ...pagination
      };
      
      const response = await this.api.get<ApiResponse<ChatHistoryItem[]>>('/api/chat/history', { params });
      
      if (response.data.success && response.data.data) {
        return response.data.data;
      } else {
        throw this.createCustomError(
          ErrorType.API_ERROR,
          response.data.message || '获取聊天历史失败',
          response.data.error
        );
      }
    } catch (error) {
      console.error('获取聊天历史失败:', error);
      throw error;
    }
  }
  
  /**
   * 清除聊天历史
   */
  async clearChatHistory(sessionId: string): Promise<void> {
    try {
      const response = await this.api.delete<ApiResponse>(`/api/chat/history/${sessionId}`);
      
      if (!response.data.success) {
        throw this.createCustomError(
          ErrorType.API_ERROR,
          response.data.message || '清除聊天历史失败',
          response.data.error
        );
      }
    } catch (error) {
      console.error('清除聊天历史失败:', error);
      throw error;
    }
  }
  
  /**
   * 获取聊天会话列表
   */
  async getChatSessions(
    userId?: string,
    pagination?: PaginationParams
  ): Promise<ChatSession[]> {
    try {
      const params = {
        user_id: userId,
        ...pagination
      };
      
      const response = await this.api.get<ApiResponse<ChatSession[]>>('/api/chat/sessions', { params });
      
      if (response.data.success && response.data.data) {
        // 转换日期字符串为Date对象
        return response.data.data.map(session => ({
          ...session,
          createdAt: new Date(session.createdAt),
          updatedAt: new Date(session.updatedAt)
        }));
      } else {
        throw this.createCustomError(
          ErrorType.API_ERROR,
          response.data.message || '获取会话列表失败',
          response.data.error
        );
      }
    } catch (error) {
      console.error('获取会话列表失败:', error);
      throw error;
    }
  }
  
  /**
   * 创建新的聊天会话
   */
  async createChatSession(title?: string, userId?: string): Promise<ChatSession> {
    try {
      const request = {
        title,
        user_id: userId
      };
      
      const response = await this.api.post<ApiResponse<ChatSession>>('/api/chat/sessions', request);
      
      if (response.data.success && response.data.data) {
        const session = response.data.data;
        return {
          ...session,
          createdAt: new Date(session.createdAt),
          updatedAt: new Date(session.updatedAt)
        };
      } else {
        throw this.createCustomError(
          ErrorType.API_ERROR,
          response.data.message || '创建会话失败',
          response.data.error
        );
      }
    } catch (error) {
      console.error('创建会话失败:', error);
      throw error;
    }
  }
  
  /**
   * 删除聊天会话
   */
  async deleteChatSession(sessionId: string): Promise<void> {
    try {
      const response = await this.api.delete<ApiResponse>(`/api/chat/sessions/${sessionId}`);
      
      if (!response.data.success) {
        throw this.createCustomError(
          ErrorType.API_ERROR,
          response.data.message || '删除会话失败',
          response.data.error
        );
      }
    } catch (error) {
      console.error('删除会话失败:', error);
      throw error;
    }
  }
  
  /**
   * 更新聊天设置
   */
  async updateChatSettings(settings: Partial<ChatSettings>): Promise<ChatSettings> {
    try {
      const response = await this.api.put<ApiResponse<ChatSettings>>('/api/chat/settings', settings);
      
      if (response.data.success && response.data.data) {
        return response.data.data;
      } else {
        throw this.createCustomError(
          ErrorType.API_ERROR,
          response.data.message || '更新设置失败',
          response.data.error
        );
      }
    } catch (error) {
      console.error('更新设置失败:', error);
      throw error;
    }
  }
  
  /**
   * 获取聊天设置
   */
  async getChatSettings(): Promise<ChatSettings> {
    try {
      const response = await this.api.get<ApiResponse<ChatSettings>>('/api/chat/settings');
      
      if (response.data.success && response.data.data) {
        return response.data.data;
      } else {
        throw this.createCustomError(
          ErrorType.API_ERROR,
          response.data.message || '获取设置失败',
          response.data.error
        );
      }
    } catch (error) {
      console.error('获取设置失败:', error);
      throw error;
    }
  }
  
  /**
   * 检查系统健康状态
   */
  async checkHealth(): Promise<SystemStatus> {
    try {
      const response = await this.api.get<ApiResponse<SystemStatus>>('/api/health');
      
      if (response.data.success && response.data.data) {
        return response.data.data;
      } else {
        throw this.createCustomError(
          ErrorType.API_ERROR,
          response.data.message || '获取系统状态失败',
          response.data.error
        );
      }
    } catch (error) {
      console.error('检查系统健康状态失败:', error);
      throw error;
    }
  }
  
  /**
   * 测试连接
   */
  async testConnection(): Promise<boolean> {
    try {
      await this.checkHealth();
      return true;
    } catch (error) {
      console.error('连接测试失败:', error);
      return false;
    }
  }
  
  /**
   * 获取API基础URL
   */
  getBaseURL(): string {
    return this.baseURL;
  }
  
  /**
   * 设置认证token
   */
  setAuthToken(token: string): void {
    localStorage.setItem('auth_token', token);
  }
  
  /**
   * 清除认证token
   */
  clearAuthToken(): void {
    localStorage.removeItem('auth_token');
  }
  
  /**
   * 获取认证token
   */
  getAuthToken(): string | null {
    return localStorage.getItem('auth_token');
  }
}

// 创建并导出服务实例
export const chatService = new ChatService();
export default ChatService;