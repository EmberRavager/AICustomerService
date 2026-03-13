import React, { useEffect, useRef, useState } from 'react';
import { Input, Button, Spin, message } from 'antd';
import { SendOutlined } from '@ant-design/icons';
import { v4 as uuidv4 } from 'uuid';
import ChatMessage from '../components/ChatMessage';
import { chatService } from '../services/chatService';
import { ChatMessage as ChatMessageType } from '../types/chat';
import './PublicChatPage.css';

const { TextArea } = Input;

const PublicChatPage: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  const [itemInfo, setItemInfo] = useState<any | null>(null);
  const [itemInfoLoading, setItemInfoLoading] = useState(false);
  const [itemInfoError, setItemInfoError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setSessionId(uuidv4());
    const params = new URLSearchParams(window.location.search);
    const tenantKey = params.get('tenant_key');
    if (tenantKey) {
      localStorage.setItem('tenant_key', tenantKey);
    }
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const extractItemId = (text: string): string | null => {
    if (!text) return null;
    const patterns = [/itemId=(\d+)/, /\/item\/(\d+)/, /itemId%3D(\d+)/];
    for (const pattern of patterns) {
      const match = text.match(pattern);
      if (match && match[1]) return match[1];
    }
    return null;
  };

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

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: ChatMessageType = {
      id: uuidv4(),
      content: inputValue.trim(),
      type: 'user',
      timestamp: new Date(),
      sessionId
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    const itemId = extractItemId(userMessage.content);
    if (itemId) {
      loadItemInfo(itemId);
    }

    const aiMessageId = uuidv4();
    const aiMessage: ChatMessageType = {
      id: aiMessageId,
      content: '',
      type: 'assistant',
      timestamp: new Date(),
      sessionId,
      isStreaming: true
    };
    setMessages(prev => [...prev, aiMessage]);

    try {
      await chatService.sendMessageStream(
        {
          message: userMessage.content,
          session_id: sessionId,
          user_id: 'visitor',
          context: itemId ? { item_id: itemId } : undefined
        },
        (chunk: string) => {
          setMessages(prev =>
            prev.map(msg =>
              msg.id === aiMessageId ? { ...msg, content: msg.content + chunk } : msg
            )
          );
        },
        (fullContent: string) => {
          setMessages(prev =>
            prev.map(msg =>
              msg.id === aiMessageId ? { ...msg, content: fullContent, isStreaming: false } : msg
            )
          );
          setIsLoading(false);
        },
        () => {
          message.error('发送失败，请重试');
          setIsLoading(false);
        }
      );
    } catch (error) {
      setIsLoading(false);
    }
  };

  return (
    <div className="public-chat">
      <div className="public-header">在线客服</div>

      {(itemInfoLoading || itemInfo || itemInfoError) && (
        <div className="public-item-info">
          {itemInfoLoading && <span>正在加载商品信息...</span>}
          {itemInfoError && <span className="public-item-error">{itemInfoError}</span>}
          {itemInfo && (
            <div className="public-item-content">
              <div className="public-item-title">{itemInfo.title || '未知商品'}</div>
              <div className="public-item-meta">
                <span>ID: {itemInfo.item_id}</span>
                {itemInfo.price_yuan !== null && itemInfo.price_yuan !== undefined && (
                  <span>¥{itemInfo.price_yuan}</span>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      <div className="public-messages">
        {messages.length === 0 && (
          <div className="public-empty">请输入问题开始对话</div>
        )}
        {messages.map((msg) => (
          <ChatMessage key={msg.id} message={msg} />
        ))}
        {isLoading && (
          <div className="public-loading">
            <Spin size="small" />
            <span>AI 正在回复...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="public-input">
        <TextArea
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          autoSize={{ minRows: 1, maxRows: 3 }}
          placeholder="输入问题..."
        />
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={sendMessage}
          disabled={!inputValue.trim() || isLoading}
        >
          发送
        </Button>
      </div>
    </div>
  );
};

export default PublicChatPage;
