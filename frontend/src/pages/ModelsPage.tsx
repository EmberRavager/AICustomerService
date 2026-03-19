import React from 'react';
import { Layout, Card, Typography, Space } from 'antd';
import ModelSelector from '../components/ModelSelector';
import './SettingsPage.css';

const { Content } = Layout;
const { Title, Text } = Typography;

const ModelsPage: React.FC = () => {
  return (
    <Layout className="settings-page">
      <Content className="settings-content">
        <div className="settings-container">
          <div className="settings-header">
            <Title level={2}>模型管理</Title>
            <Text type="secondary">选择与测试机器人使用的模型</Text>
          </div>

          <Card className="settings-card" title="模型配置" styles={{ body: { padding: '24px' } }}>
            <Space direction="vertical" size={16} style={{ width: '100%' }}>
              <ModelSelector />
            </Space>
          </Card>
        </div>
      </Content>
    </Layout>
  );
};

export default ModelsPage;
