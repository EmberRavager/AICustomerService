import React, { useEffect, useState } from 'react';
import { Layout, Card, Typography, Input, Button, Space, Switch, InputNumber, message } from 'antd';
import { chatService } from '../services/chatService';
import { ChatSettings } from '../types/chat';
import './SettingsPage.css';

const { Content } = Layout;
const { Title, Text } = Typography;
const { TextArea } = Input;

const ChatSettingsPage: React.FC = () => {
  const [chatSettings, setChatSettings] = useState<ChatSettings>({
    model: '',
    temperature: 0.7,
    max_tokens: 1000,
    system_prompt: '',
    enable_memory: true,
    memory_window: 10,
    enable_knowledge_base: true,
    max_history_length: 50
  });
  const [chatSettingsLoading, setChatSettingsLoading] = useState(false);
  const [chatSettingsSaving, setChatSettingsSaving] = useState(false);

  const loadChatSettings = async () => {
    try {
      setChatSettingsLoading(true);
      const data = await chatService.getChatSettings();
      setChatSettings(data);
    } catch (error) {
      message.error('加载聊天设置失败');
    } finally {
      setChatSettingsLoading(false);
    }
  };

  const saveChatSettings = async () => {
    try {
      setChatSettingsSaving(true);
      const data = await chatService.updateChatSettings(chatSettings);
      setChatSettings(data);
      message.success('聊天设置已保存');
    } catch (error) {
      message.error('保存聊天设置失败');
    } finally {
      setChatSettingsSaving(false);
    }
  };

  useEffect(() => {
    loadChatSettings();
  }, []);

  return (
    <Layout className="settings-page">
      <Content className="settings-content">
        <div className="settings-container">
          <div className="settings-header">
            <Title level={2}>聊天设置</Title>
            <Text type="secondary">配置提示词、记忆与上下文窗口</Text>
          </div>

          <Card
            title="聊天参数"
            className="settings-card"
            styles={{ body: { padding: '24px' } }}
          >
            <Space direction="vertical" size={12} style={{ width: '100%' }}>
              <Input
                value={chatSettings?.model || ''}
                onChange={(e) => setChatSettings({ ...chatSettings, model: e.target.value })}
                placeholder="模型名称"
                disabled={chatSettingsLoading}
              />
              <Space size={12} wrap>
                <div className="settings-field">
                  <Text type="secondary">温度</Text>
                  <InputNumber
                    min={0}
                    max={2}
                    step={0.1}
                    value={chatSettings?.temperature}
                    onChange={(value) => setChatSettings({ ...chatSettings, temperature: value || 0 })}
                  />
                </div>
                <div className="settings-field">
                  <Text type="secondary">最大Token</Text>
                  <InputNumber
                    min={1}
                    max={4000}
                    value={chatSettings?.max_tokens}
                    onChange={(value) => setChatSettings({ ...chatSettings, max_tokens: value || 0 })}
                  />
                </div>
                <div className="settings-field">
                  <Text type="secondary">记忆窗口</Text>
                  <InputNumber
                    min={1}
                    max={200}
                    value={chatSettings?.memory_window}
                    onChange={(value) => setChatSettings({ ...chatSettings, memory_window: value || 0 })}
                  />
                </div>
                <div className="settings-field">
                  <Text type="secondary">历史长度</Text>
                  <InputNumber
                    min={1}
                    max={500}
                    value={chatSettings?.max_history_length}
                    onChange={(value) => setChatSettings({ ...chatSettings, max_history_length: value || 0 })}
                  />
                </div>
              </Space>
              <Space size={12} wrap>
                <Space size={8}>
                  <Text>启用记忆</Text>
                  <Switch
                    checked={!!chatSettings?.enable_memory}
                    onChange={(checked) => setChatSettings({ ...chatSettings, enable_memory: checked })}
                  />
                </Space>
                <Space size={8}>
                  <Text>启用知识库</Text>
                  <Switch
                    checked={!!chatSettings?.enable_knowledge_base}
                    onChange={(checked) => setChatSettings({ ...chatSettings, enable_knowledge_base: checked })}
                  />
                </Space>
              </Space>
              <TextArea
                value={chatSettings?.system_prompt || ''}
                onChange={(e) => setChatSettings({ ...chatSettings, system_prompt: e.target.value })}
                rows={4}
                placeholder="系统提示词"
              />
              <Space>
                <Button
                  type="primary"
                  loading={chatSettingsSaving}
                  onClick={saveChatSettings}
                >
                  保存聊天设置
                </Button>
                <Button onClick={loadChatSettings} disabled={chatSettingsLoading}>
                  重新加载
                </Button>
              </Space>
            </Space>
          </Card>
        </div>
      </Content>
    </Layout>
  );
};

export default ChatSettingsPage;
