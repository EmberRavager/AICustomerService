// API 服务配置
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * 通用API请求函数
 * @param {string} endpoint - API端点
 * @param {object} options - 请求选项
 * @returns {Promise} - 响应数据
 */
const apiRequest = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`API请求失败 [${endpoint}]:`, error);
    throw error;
  }
};

/**
 * 聊天API
 */
export const chatAPI = {
  /**
   * 发送聊天消息
   * @param {string} message - 用户消息
   * @param {string} sessionId - 会话ID
   * @returns {Promise} - AI回复
   */
  sendMessage: async (message, sessionId = null) => {
    return apiRequest('/api/chat', {
      method: 'POST',
      body: JSON.stringify({
        message,
        session_id: sessionId,
      }),
    });
  },

  /**
   * 获取聊天历史
   * @param {string} sessionId - 会话ID
   * @returns {Promise} - 聊天历史
   */
  getChatHistory: async (sessionId, limit = 50, offset = 0) => {
    const params = new URLSearchParams({ session_id: sessionId, limit, offset });
    return apiRequest(`/api/chat/history?${params.toString()}`);
  },

  /**
   * 清除聊天历史
   * @param {string} sessionId - 会话ID
   * @returns {Promise} - 操作结果
   */
  clearChatHistory: async (sessionId) => {
    return apiRequest(`/api/chat/history/${sessionId}`, {
      method: 'DELETE',
    });
  },
};

/**
 * 知识库API
 */
export const knowledgeAPI = {
  /**
   * 搜索知识库
   * @param {string} query - 搜索查询
   * @param {number} limit - 结果数量限制
   * @param {string} searchType - 搜索类型
   * @returns {Promise} - 搜索结果
   */
  searchKnowledge: async (query, limit = 10, searchType = 'hybrid') => {
    const params = new URLSearchParams({ query, limit, search_type: searchType });
    return apiRequest(`/api/knowledge?${params.toString()}`);
  },

  /**
   * 获取知识库列表
   * @param {string} category - 分类
   * @param {number} limit - 结果数量限制
   * @param {number} offset - 偏移量
   * @returns {Promise} - 知识库列表
   */
  listKnowledge: async (category = '', limit = 20, offset = 0) => {
    const params = new URLSearchParams({ category, limit, offset });
    return apiRequest(`/api/knowledge/list?${params.toString()}`);
  },

  /**
   * 获取知识库分类
   * @returns {Promise} - 分类列表
   */
  getCategories: async () => {
    return apiRequest('/api/knowledge/categories');
  },

  /**
   * 新增知识库条目
   * @param {object} payload - 知识条目
   * @returns {Promise} - 新增结果
   */
  addKnowledge: async (payload) => {
    return apiRequest('/api/knowledge', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },

  /**
   * 更新知识库条目
   * @param {string} id - 条目ID
   * @param {object} payload - 知识条目
   * @returns {Promise} - 更新结果
   */
  updateKnowledge: async (id, payload) => {
    return apiRequest(`/api/knowledge/${id}`, {
      method: 'PUT',
      body: JSON.stringify(payload)
    });
  },

  /**
   * 删除知识库条目
   * @param {string} id - 条目ID
   * @returns {Promise} - 删除结果
   */
  deleteKnowledge: async (id) => {
    return apiRequest(`/api/knowledge/${id}`, {
      method: 'DELETE'
    });
  },

  /**
   * 批量添加知识库条目
   * @param {Array} payload - 知识条目数组
   * @returns {Promise} - 批量结果
   */
  batchAddKnowledge: async (payload) => {
    return apiRequest('/api/knowledge/batch', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }
};

/**
 * 模型管理API
 */
export const modelAPI = {
  /**
   * 获取支持的模型提供商列表
   * @returns {Promise} - 提供商列表
   */
  getProviders: async () => {
    return apiRequest('/api/models/providers');
  },

  /**
   * 获取当前模型配置
   * @returns {Promise} - 当前模型配置
   */
  getCurrentModel: async () => {
    return apiRequest('/api/models/current');
  },

  /**
   * 列出所有模型配置
   * @returns {Promise} - 所有模型配置
   */
  listModels: async () => {
    return apiRequest('/api/models/list');
  },

  /**
   * 获取指定提供商的可用模型
   * @param {string} provider - 提供商名称
   * @returns {Promise} - 可用模型列表
   */
  getProviderModels: async (provider) => {
    return apiRequest(`/api/models/providers/${provider}/models`);
  },

  /**
   * 切换模型提供商
   * @param {object} config - 模型配置
   * @param {string} config.provider - 提供商名称
   * @param {string} config.model - 模型名称
   * @returns {Promise} - 切换结果
   */
  switchModel: async (config) => {
    return apiRequest('/api/models/switch', {
      method: 'POST',
      body: JSON.stringify(config),
    });
  },

  /**
   * 测试模型连接
   * @param {object} config - 测试配置
   * @param {string} config.provider - 提供商名称
   * @param {string} config.test_message - 测试消息
   * @returns {Promise} - 测试结果
   */
  testModel: async (config) => {
    return apiRequest('/api/models/test', {
      method: 'POST',
      body: JSON.stringify(config),
    });
  },

  /**
   * 获取模型状态
   * @returns {Promise} - 模型状态信息
   */
  getModelStatus: async () => {
    return apiRequest('/api/models/status');
  },
};

/**
 * 健康检查API
 */
export const healthAPI = {
  /**
   * 检查服务健康状态
   * @returns {Promise} - 健康状态
   */
  checkHealth: async () => {
    return apiRequest('/api/health');
  }
};

// 默认导出所有API
export default {
  chat: chatAPI,
  knowledge: knowledgeAPI,
  model: modelAPI,
  health: healthAPI,
};
