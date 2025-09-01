import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { Layout, Card, Input, Button, Space, message, Spin } from 'antd';
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
          user_id: 'user_001' // 可以从用户上下文获取
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
  };
  
  /**
   * 创建新会话
   */
  const createNewSession = () => {
    const newSessionId = uuidv4();
    setCurrentSessionId(newSessionId);
    setMessages([]);
    setShowHistory(false);
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
          background: '#fff',
          borderRight: '1px solid #f0f0f0',
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
            <Space>
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
          </div>
          
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