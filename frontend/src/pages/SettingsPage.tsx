import React from 'react';
import { Layout, Card, Typography, Divider } from 'antd';
import { SettingOutlined } from '@ant-design/icons';
import ModelSelector from '../components/ModelSelector';
import './SettingsPage.css';

/**
 * 设置页面组件
 * 提供系统配置和模型设置功能
 */

const { Content } = Layout;
const { Title, Text } = Typography;

const SettingsPage: React.FC = () => {
  /**
   * 处理模型变更
   */
  const handleModelChange = (provider: string, model: string) => {
    console.log('模型已切换:', { provider, model });
  };

  return (
    <Layout className="settings-page">
      <Content className="settings-content">
        <div className="settings-container">
          {/* 页面标题 */}
          <div className="settings-header">
            <Title level={2}>
              <SettingOutlined /> 系统设置
            </Title>
            <Text type="secondary">
              在这里配置您的智能客服系统参数
            </Text>
          </div>

          {/* 模型配置卡片 */}
          <Card 
            title="模型配置" 
            className="settings-card"
            styles={{ body: { padding: '24px' } }}
          >
            <div className="model-settings">
              <Text strong style={{ fontSize: '16px', marginBottom: '16px', display: 'block' }}>
                AI模型选择
              </Text>
              <Text type="secondary" style={{ marginBottom: '24px', display: 'block' }}>
                选择适合您需求的AI模型，不同模型具有不同的特点和性能表现。
              </Text>
              
              <ModelSelector onModelChange={handleModelChange} />
            </div>
          </Card>

          <Divider />

          {/* 其他设置卡片 */}
          <Card 
            title="聊天设置" 
            className="settings-card"
            styles={{ body: { padding: '24px' } }}
          >
            <div className="chat-settings">
              <Text type="secondary">
                更多聊天相关设置功能即将推出...
              </Text>
            </div>
          </Card>
        </div>
      </Content>
    </Layout>
  );
};

export default SettingsPage;