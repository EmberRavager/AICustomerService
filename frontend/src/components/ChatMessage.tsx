import React, { useState, useEffect } from 'react';
import { Avatar, Typography, Space, Tag, Tooltip, Button } from 'antd';
import { UserOutlined, RobotOutlined, CopyOutlined, CheckOutlined, LoadingOutlined } from '@ant-design/icons';
import { ChatMessage as ChatMessageType } from '../types/chat';
import './ChatMessage.css';

/**
 * 聊天消息组件
 * 用于显示单条聊天消息，支持用户消息和AI回复
 */

const { Text, Paragraph } = Typography;

interface ChatMessageProps {
  message: ChatMessageType;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const [copied, setCopied] = useState(false);
  const [showCursor, setShowCursor] = useState(true);
  
  // 流式传输时的光标闪烁效果
  useEffect(() => {
    if (message.isStreaming) {
      const interval = setInterval(() => {
        setShowCursor(prev => !prev);
      }, 500);
      return () => clearInterval(interval);
    } else {
      setShowCursor(false);
      return undefined;
    }
  }, [message.isStreaming]);
  
  /**
   * 复制消息内容到剪贴板
   */
  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('复制失败:', error);
    }
  };
  
  /**
   * 格式化时间显示
   */
  const formatTime = (timestamp: Date) => {
    const now = new Date();
    const diff = now.getTime() - timestamp.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    
    if (minutes < 1) {
      return '刚刚';
    } else if (minutes < 60) {
      return `${minutes}分钟前`;
    } else if (hours < 24) {
      return `${hours}小时前`;
    } else if (days < 7) {
      return `${days}天前`;
    } else {
      return timestamp.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    }
  };
  
  /**
   * 渲染消息内容
   */
  const renderContent = () => {
    // 处理换行
    const lines = message.content.split('\n');
    
    return (
      <div className="message-content">
        {lines.map((line, index) => (
          <div key={index} className="message-line">
            {line || <br />}
            {/* 在最后一行显示流式传输光标 */}
            {message.isStreaming && index === lines.length - 1 && (
              <span className={`typing-cursor ${showCursor ? 'visible' : 'hidden'}`}>|</span>
            )}
          </div>
        ))}
        {/* 如果内容为空且正在流式传输，显示光标 */}
        {message.isStreaming && !message.content && (
          <span className={`typing-cursor ${showCursor ? 'visible' : 'hidden'}`}>|</span>
        )}
      </div>
    );
  };
  
  /**
   * 渲染消息元数据
   */
  const renderMetadata = () => {
    if (!message.metadata) return null;
    
    return (
      <div className="message-metadata">
        <Space size={4} wrap>
          {message.metadata.tokensUsed && (
            <Tag color="blue">
              {message.metadata.tokensUsed} tokens
            </Tag>
          )}
          {message.metadata.modelUsed && (
            <Tag color="green">
              {message.metadata.modelUsed}
            </Tag>
          )}
          {message.metadata.confidence && (
            <Tag color="orange">
              置信度: {(message.metadata.confidence * 100).toFixed(1)}%
            </Tag>
          )}
        </Space>
      </div>
    );
  };
  
  const isUser = message.type === 'user';
  const isError = message.isError;
  
  return (
    <div className={`chat-message ${isUser ? 'user-message' : 'assistant-message'} ${isError ? 'error-message' : ''}`}>
      <div className="message-wrapper">
        {/* 头像 */}
        <div className="message-avatar">
          <Avatar
            size={36}
            icon={isUser ? <UserOutlined /> : <RobotOutlined />}
            style={{
              backgroundColor: isUser ? '#1890ff' : isError ? '#ff4d4f' : '#52c41a',
              color: '#fff'
            }}
          />
        </div>
        
        {/* 消息主体 */}
        <div className="message-body">
          {/* 消息头部信息 */}
          <div className="message-header">
            <Space size={8} align="center">
              <Text strong className="message-sender">
                {isUser ? '您' : 'AI助手'}
              </Text>
              <Tooltip title={message.timestamp.toLocaleString('zh-CN')}>
                <Text type="secondary" className="message-time">
                  {formatTime(message.timestamp)}
                </Text>
              </Tooltip>
              {isError && (
                <Tag color="error">
                  错误
                </Tag>
              )}
              {message.isStreaming && (
                <Tag color="processing" icon={<LoadingOutlined />}>
                  正在输入...
                </Tag>
              )}
            </Space>
          </div>
          
          {/* 消息内容 */}
          <div className="message-content-wrapper">
            <div className={`message-bubble ${isUser ? 'user-bubble' : 'assistant-bubble'} ${isError ? 'error-bubble' : ''} ${message.isStreaming ? 'streaming' : ''}`}>
              {renderContent()}
              
              {/* 复制按钮 */}
              <div className="message-actions">
                <Tooltip title={copied ? '已复制' : '复制消息'}>
                  <Button
                    type="text"
                    size="small"
                    icon={copied ? <CheckOutlined /> : <CopyOutlined />}
                    onClick={copyToClipboard}
                    className="copy-button"
                  />
                </Tooltip>
              </div>
            </div>
            
            {/* 元数据 */}
            {renderMetadata()}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;