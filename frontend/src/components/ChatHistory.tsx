import React, { useState } from 'react';
import { List, Button, Space, Typography, Input, Popconfirm, Empty, Tooltip } from 'antd';
import { PlusOutlined, DeleteOutlined, SearchOutlined, MessageOutlined, ClockCircleOutlined } from '@ant-design/icons';
import { ChatSession } from '../types/chat';
import './ChatHistory.css';

/**
 * 聊天历史组件
 * 用于显示和管理聊天会话列表
 */

const { Text } = Typography;
const { Search } = Input;

interface ChatHistoryProps {
  sessions: ChatSession[];
  currentSessionId: string;
  onSessionSelect: (sessionId: string) => void;
  onNewSession: () => void;
  onSessionDelete: (sessionId: string) => void;
}

const ChatHistory: React.FC<ChatHistoryProps> = ({
  sessions,
  currentSessionId,
  onSessionSelect,
  onNewSession,
  onSessionDelete
}) => {
  const [searchValue, setSearchValue] = useState('');
  
  /**
   * 过滤会话列表
   */
  const filteredSessions = sessions.filter(session => {
    if (!searchValue.trim()) return true;
    
    const searchLower = searchValue.toLowerCase();
    return (
      session.title?.toLowerCase().includes(searchLower) ||
      session.lastMessage?.toLowerCase().includes(searchLower)
    );
  });
  
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
        month: 'short',
        day: 'numeric'
      });
    }
  };
  
  /**
   * 截断文本
   */
  const truncateText = (text: string, maxLength: number = 30) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };
  
  /**
   * 生成会话标题
   */
  const getSessionTitle = (session: ChatSession) => {
    if (session.title) {
      return session.title;
    }
    
    if (session.lastMessage) {
      return truncateText(session.lastMessage, 20);
    }
    
    return `会话 ${session.id.substring(0, 8)}`;
  };
  
  /**
   * 渲染会话项
   */
  const renderSessionItem = (session: ChatSession) => {
    const isActive = session.id === currentSessionId;
    const title = getSessionTitle(session);
    const lastMessage = session.lastMessage ? truncateText(session.lastMessage, 40) : '暂无消息';
    
    return (
      <List.Item
        key={session.id}
        className={`session-item ${isActive ? 'active' : ''}`}
        onClick={() => onSessionSelect(session.id)}
      >
        <div className="session-content">
          {/* 会话头部 */}
          <div className="session-header">
            <div className="session-title">
              <MessageOutlined className="session-icon" />
              <Text strong className="title-text">
                {title}
              </Text>
            </div>
            
            {/* 删除按钮 */}
            <div className="session-actions">
              <Popconfirm
                title="确认删除"
                description="确定要删除这个会话吗？此操作不可恢复。"
                onConfirm={(e) => {
                  e?.stopPropagation();
                  onSessionDelete(session.id);
                }}
                okText="删除"
                cancelText="取消"
                placement="topRight"
              >
                <Button
                  type="text"
                  size="small"
                  icon={<DeleteOutlined />}
                  className="delete-button"
                  onClick={(e) => e.stopPropagation()}
                  danger
                />
              </Popconfirm>
            </div>
          </div>
          
          {/* 最后一条消息 */}
          <div className="session-preview">
            <Text type="secondary" className="preview-text">
              {lastMessage}
            </Text>
          </div>
          
          {/* 会话信息 */}
          <div className="session-info">
            <Space size={8}>
              <Text type="secondary" className="session-time">
                <ClockCircleOutlined className="time-icon" />
                {formatTime(session.updatedAt)}
              </Text>
              
              {session.messageCount && (
                <Text type="secondary" className="message-count">
                  {session.messageCount} 条消息
                </Text>
              )}
            </Space>
          </div>
        </div>
      </List.Item>
    );
  };
  
  return (
    <div className="chat-history">
      {/* 头部 */}
      <div className="history-header">
        <div className="header-title">
          <Text strong>聊天历史</Text>
        </div>
        
        {/* 新建会话按钮 */}
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={onNewSession}
          className="new-session-button"
          size="small"
        >
          新建会话
        </Button>
      </div>
      
      {/* 搜索框 */}
      <div className="search-container">
        <Search
          placeholder="搜索会话..."
          value={searchValue}
          onChange={(e) => setSearchValue(e.target.value)}
          allowClear
          size="small"
          prefix={<SearchOutlined />}
        />
      </div>
      
      {/* 会话列表 */}
      <div className="sessions-container">
        {filteredSessions.length === 0 ? (
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description={
              searchValue ? (
                <span>
                  未找到匹配的会话
                  <br />
                  <Button type="link" onClick={() => setSearchValue('')}>
                    清除搜索
                  </Button>
                </span>
              ) : (
                <span>
                  暂无聊天记录
                  <br />
                  <Button type="link" onClick={onNewSession}>
                    开始新对话
                  </Button>
                </span>
              )
            }
            className="empty-state"
          />
        ) : (
          <List
            dataSource={filteredSessions}
            renderItem={renderSessionItem}
            className="sessions-list"
            split={false}
          />
        )}
      </div>
      
      {/* 底部信息 */}
      <div className="history-footer">
        <Text type="secondary" className="footer-text">
          共 {sessions.length} 个会话
        </Text>
      </div>
    </div>
  );
};

export default ChatHistory;