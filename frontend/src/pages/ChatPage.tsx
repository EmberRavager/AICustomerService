import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { Layout, Card, Input, Button, Space, message, Spin, Switch, Tag, Select } from 'antd';
import { SendOutlined, ClearOutlined, HistoryOutlined } from '@ant-design/icons';
import { v4 as uuidv4 } from 'uuid';
import ChatMessage from '../components/ChatMessage';
import ChatHistory from '../components/ChatHistory';
import { chatService } from '../services/chatService';
import { ChatMessage as ChatMessageType, ChatSession } from '../types/chat';
import './ChatPage.css';

/**
 * 聊天页面组件
 * 提供完整的聊天界面和功能
 */

const { Content, Sider } = Layout;
const { TextArea } = Input;

const ChatPage: React.FC = () => {
  // 路由参数
  const { sessionId: urlSessionId } = useParams<{ sessionId?: string }>();
  
  // 状态管理
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState<string>('');
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [showHistory, setShowHistory] = useState(true);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [itemInfo, setItemInfo] = useState<any | null>(null);
  const [itemInfoLoading, setItemInfoLoading] = useState(false);
  const [itemInfoError, setItemInfoError] = useState<string | null>(null);
  const [manualMode, setManualMode] = useState(false);
  const [tenantKey, setTenantKey] = useState('');
  const [tenantOptions, setTenantOptions] = useState<Array<{ label: string; value: string }>>([]);
  const [tenantLoading, setTenantLoading] = useState(false);
  
  // 引用
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<any>(null);
  
  /**
   * 滚动到消息底部
   */
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  /**
   * 初始化会话
   */
  const initializeSession = () => {
    const sessionId = urlSessionId || uuidv4();
    setCurrentSessionId(sessionId);
    return sessionId;
  };
  
  /**
   * 加载聊天历史
   */
  const loadChatHistory = async (sessionId: string) => {
    try {
      setIsLoadingHistory(true);
      const history = await chatService.getChatHistory(sessionId);
      
      const formattedMessages: ChatMessageType[] = history.map(item => ({
        id: item.id || uuidv4(),
        content: item.content,
        type: item.message_type,
        timestamp: new Date(item.timestamp),
        sessionId: item.session_id
      }));
      
      setMessages(formattedMessages);

      // 从历史消息中恢复商品信息
      const historyItemId = [...formattedMessages]
        .reverse()
        .map(msg => extractItemId(msg.content))
        .find(id => !!id);

      if (historyItemId) {
        loadItemInfo(historyItemId);
      } else {
        setItemInfo(null);
        setItemInfoError(null);
      }
    } catch (error) {
      console.error('加载聊天历史失败:', error);
      message.error('加载聊天历史失败');
    } finally {
      setIsLoadingHistory(false);
    }
  };
  
  /**
   * 加载会话列表
   */
  const loadSessions = async () => {
    try {
      const sessionList = await chatService.getChatSessions();
      setSessions(sessionList);
    } catch (error) {
      console.error('加载会话列表失败:', error);
    }
  };

  const loadTenants = async () => {
    try {
      setTenantLoading(true);
      const data = await chatService.listTenants();
      const list = data.tenants || [];
      setTenantOptions(
        list.map((tenant: any) => ({
          label: `${tenant.name} (${tenant.tenant_id})`,
          value: tenant.api_key
        }))
      );
    } catch (error) {
      setTenantOptions([]);
    } finally {
      setTenantLoading(false);
    }
  };

  /**
   * 加载会话元信息
   */
  const loadSessionMeta = async (sessionId: string) => {
    try {
      const meta = await chatService.getSessionMeta(sessionId);
      setManualMode(!!meta.manual_mode);
    } catch (error) {
      setManualMode(false);
    }
  };

  /**
   * 从文本中提取商品ID
   */
  const extractItemId = (text: string): string | null => {
    if (!text) return null;
    const patterns = [/itemId=(\d+)/, /\/item\/(\d+)/, /itemId%3D(\d+)/];
    for (const pattern of patterns) {
      const match = text.match(pattern);
      if (match && match[1]) {
        return match[1];
      }
    }
    return null;
  };

  /**
   * 加载商品信息
   */
  const loadItemInfo = async (itemId: string) => {
    try {
      setItemInfoLoading(true);
      setItemInfoError(null);
      const data = await chatService.getItemInfo(itemId);
      setItemInfo(data);
    } catch (error: any) {
      setItemInfo(null);
      setItemInfoError(error?.message || '商品信息加载失败');
    } finally {
      setItemInfoLoading(false);
    }
  };
  
  /**
   * 发送消息（流式传输）
   */
  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) {
      return;
    }
    
    const userMessage: ChatMessageType = {
      id: uuidv4(),
      content: inputValue.trim(),
      type: 'user',
      timestamp: new Date(),
      sessionId: currentSessionId
    };
    
    // 添加用户消息到界面
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    // 提取商品ID并加载商品信息
    const itemId = extractItemId(userMessage.content);
    if (itemId) {
      loadItemInfo(itemId);
    }

    // 人工接管模式不触发AI回复
    if (manualMode) {
      const manualReply: ChatMessageType = {
        id: uuidv4(),
        content: '当前会话已转人工处理，消息已记录。',
        type: 'assistant',
        timestamp: new Date(),
        sessionId: currentSessionId
      };
      setMessages(prev => [...prev, manualReply]);
      setIsLoading(false);
      return;
    }
    
    // 创建AI消息占位符
    const aiMessageId = uuidv4();
    const aiMessage: ChatMessageType = {
      id: aiMessageId,
      content: '',
      type: 'assistant',
      timestamp: new Date(),
      sessionId: currentSessionId,
      isStreaming: true
    };
    
    // 添加AI消息占位符到界面
    setMessages(prev => [...prev, aiMessage]);
    
    try {
      // 调用流式聊天API
      await chatService.sendMessageStream(
        {
          message: userMessage.content,
          session_id: currentSessionId,
          user_id: 'user_001', // 可以从用户上下文获取
          context: itemId ? { item_id: itemId } : undefined
        },
        // onChunk: 处理流式数据块
        (chunk: string) => {
          setMessages(prev => 
            prev.map(msg => 
              msg.id === aiMessageId 
                ? { ...msg, content: msg.content + chunk }
                : msg
            )
          );
        },
        // onComplete: 流式传输完成
        (fullContent: string) => {
          setMessages(prev => 
            prev.map(msg => 
              msg.id === aiMessageId 
                ? { ...msg, content: fullContent, isStreaming: false }
                : msg
            )
          );
          setIsLoading(false);
        },
        // onError: 处理错误
        (error: string) => {
          console.error('发送消息失败:', error);
          message.error('发送消息失败，请重试');
          
          // 更新AI消息为错误消息
          setMessages(prev => 
            prev.map(msg => 
              msg.id === aiMessageId 
                ? { 
                    ...msg, 
                    content: '抱歉，我现在无法回复您的消息，请稍后再试。',
                    isStreaming: false
                  }
                : msg
            )
          );
          setIsLoading(false);
        }
      );
      
    } catch (error) {
      console.error('发送消息失败:', error);
      message.error('发送消息失败，请重试');
      
      // 添加错误消息
      const errorMessage: ChatMessageType = {
        id: uuidv4(),
        content: '抱歉，我现在无法回复您的消息，请稍后再试。',
        type: 'assistant',
        timestamp: new Date(),
        sessionId: currentSessionId,
        isError: true
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };
  
  /**
   * 清除当前会话
   */
  const clearCurrentSession = async () => {
    try {
      await chatService.clearChatHistory(currentSessionId);
      setMessages([]);
      message.success('会话已清除');
    } catch (error) {
      console.error('清除会话失败:', error);
      message.error('清除会话失败');
    }
  };
  
  /**
   * 切换会话
   */
  const switchSession = (sessionId: string) => {
    setCurrentSessionId(sessionId);
    loadChatHistory(sessionId);
    loadSessionMeta(sessionId);
    setShowHistory(false);
  };
  
  /**
   * 创建新会话
   */
  const createNewSession = () => {
    const newSessionId = uuidv4();
    setCurrentSessionId(newSessionId);
    setMessages([]);
    setShowHistory(false);
    setItemInfo(null);
    setItemInfoError(null);
    setManualMode(false);
  };
  
  /**
   * 处理键盘事件
   */
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };
  

  
  // 组件挂载时初始化
  useEffect(() => {
    const sessionId = initializeSession();
    if (urlSessionId) {
      loadChatHistory(sessionId);
    }
    loadSessions();
    loadSessionMeta(sessionId);
    setTenantKey(localStorage.getItem('tenant_key') || '');
    if (chatService.getAuthToken()) {
      loadTenants();
    }
  }, [urlSessionId]);
  
  // 消息变化时滚动到底部
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  // 聚焦输入框
  useEffect(() => {
    if (!isLoading && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isLoading]);

  const applyTenantKey = async () => {
    if (!tenantKey.trim()) {
      message.warning('请输入或选择机器人 Key');
      return;
    }
    localStorage.setItem('tenant_key', tenantKey.trim());
    message.success('机器人绑定已更新');
    setMessages([]);
    setItemInfo(null);
    setItemInfoError(null);
    const newSessionId = uuidv4();
    setCurrentSessionId(newSessionId);
    await loadSessions();
  };
  
  return (
    <Layout className="chat-page">
      {/* 侧边栏 - 聊天历史 */}
      <Sider
        width={300}
        className="chat-sidebar"
        collapsed={!showHistory}
        collapsedWidth={0}
        trigger={null}
        style={{
          background: 'var(--surface)',
          borderRight: '1px solid var(--border)',
        }}
      >
        <ChatHistory
           sessions={sessions}
           currentSessionId={currentSessionId}
           onSessionSelect={switchSession}
           onNewSession={createNewSession}
           onSessionDelete={(sessionId) => {
             setSessions(prev => prev.filter(s => s.id !== sessionId));
           }}
         />
      </Sider>
      
      {/* 主聊天区域 */}
      <Content className="chat-content">
        <Card className="chat-container" styles={{ body: { padding: 0 } }}>
          {/* 聊天头部 */}
          <div className="chat-header">
            <Space className="chat-header-left">
              <Button
                type="text"
                icon={<HistoryOutlined />}
                onClick={() => setShowHistory(!showHistory)}
              >
                {showHistory ? '隐藏历史' : '显示历史'}
              </Button>
              
              <Button
                type="text"
                icon={<ClearOutlined />}
                onClick={clearCurrentSession}
                disabled={messages.length === 0}
              >
                清除会话
              </Button>
            </Space>
            <Space className="chat-header-robot" size={8}>
              <Tag color="gold">当前机器人</Tag>
              <Select
                value={tenantKey || undefined}
                placeholder="选择机器人 Key"
                style={{ minWidth: 220 }}
                loading={tenantLoading}
                options={tenantOptions}
                onChange={(value) => setTenantKey(value || '')}
                allowClear
                showSearch
                optionFilterProp="label"
              />
              <Input
                value={tenantKey}
                onChange={(e) => setTenantKey(e.target.value)}
                placeholder="或手动输入 X-Tenant-Key"
                style={{ width: 240 }}
              />
              <Button type="primary" onClick={applyTenantKey}>
                绑定机器人
              </Button>
            </Space>
            <Space className="chat-header-right" size={6}>
              {manualMode && <Tag color="orange">人工接管中</Tag>}
              <span>人工接管</span>
              <Switch
                checked={manualMode}
                onChange={async (checked) => {
                  try {
                    await chatService.setManualMode(currentSessionId, checked);
                    setManualMode(checked);
                    message.success(checked ? '已切换为人工接管' : '已恢复自动回复');
                  } catch (error) {
                    message.error('切换失败');
                  }
                }}
              />
            </Space>
          </div>

          {/* 商品信息 */}
          {(itemInfoLoading || itemInfo || itemInfoError) && (
            <div className="item-info-bar">
              {itemInfoLoading && (
                <div className="item-info-loading">正在加载商品信息...</div>
              )}
              {itemInfoError && (
                <div className="item-info-error">{itemInfoError}</div>
              )}
              {itemInfo && (
                <div className="item-info-content">
                  <div className="item-info-title">{itemInfo.title || '未知商品'}</div>
                  <div className="item-info-meta">
                    <span>商品ID: {itemInfo.item_id}</span>
                    {itemInfo.price_yuan !== null && itemInfo.price_yuan !== undefined && (
                      <span>价格: ¥{itemInfo.price_yuan}</span>
                    )}
                    {itemInfo.quantity !== null && itemInfo.quantity !== undefined && (
                      <span>库存: {itemInfo.quantity}</span>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
          
          {/* 消息列表区域 */}
          <div className="messages-container">
            {isLoadingHistory ? (
              <div className="loading-container">
                <Spin size="large" />
                <div className="loading-text">加载聊天历史中...</div>
              </div>
            ) : messages.length === 0 ? (
              <div className="welcome-container">
                <div className="welcome-text">👋 欢迎使用智能客服系统</div>
                <div className="welcome-description">
                  我是您的AI助手，可以帮助您解答各种问题。请输入您的问题开始对话。
                </div>
                <div className="feature-grid">
                  <div className="feature-card">
                    <div className="feature-title">商品信息联动</div>
                    <div className="feature-desc">粘贴商品链接或 itemId，自动抓取关键信息</div>
                  </div>
                  <div className="feature-card">
                    <div className="feature-title">议价与技术意图</div>
                    <div className="feature-desc">识别议价/技术咨询场景，生成更贴合的答复</div>
                  </div>
                  <div className="feature-card">
                    <div className="feature-title">风控提醒</div>
                    <div className="feature-desc">命中风险关键词时自动提示安全交易</div>
                  </div>
                  <div className="feature-card">
                    <div className="feature-title">人工接管</div>
                    <div className="feature-desc">一键切换人工处理，保留会话历史</div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="messages-list">
                {messages.map((message) => (
                  <ChatMessage
                    key={message.id}
                    message={message}
                  />
                ))}
                {isLoading && (
                  <div className="typing-indicator">
                    <Spin size="small" />
                    <span>AI正在思考中...</span>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>
          
          {/* 输入区域 */}
          <div className="input-container">
            <div className="input-wrapper">
              <TextArea
                ref={inputRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="请输入您的问题...（按Enter发送，Shift+Enter换行）"
                autoSize={{ minRows: 1, maxRows: 4 }}
                disabled={isLoading}
                className="message-input"
              />
              <Button
                type="primary"
                icon={<SendOutlined />}
                onClick={sendMessage}
                loading={isLoading}
                disabled={!inputValue.trim()}
                className="send-button"
              >
                发送
              </Button>
            </div>
          </div>
        </Card>
      </Content>
    </Layout>
  );
};

export default ChatPage;
