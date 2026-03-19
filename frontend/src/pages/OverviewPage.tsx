import React from 'react';
import { Layout, Card, Typography, Space, Button } from 'antd';
import { useNavigate } from 'react-router-dom';
import './SettingsPage.css';

const { Content } = Layout;
const { Title, Text } = Typography;

const OverviewPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <Layout className="settings-page">
      <Content className="settings-content">
        <div className="settings-container">
          <div className="settings-header">
            <Title level={2}>机器人运营概览</Title>
            <Text type="secondary">以机器人为主体的运营与配置入口</Text>
          </div>

          <Card className="settings-card overview-hero" styles={{ body: { padding: '24px' } }}>
            <div className="overview-hero-inner">
              <div>
                <Title level={4}>标准操作流程</Title>
                <Text type="secondary">创建机器人 → 绑定账号 → 配置知识库与策略 → 进入测试聊天</Text>
              </div>
              <Space>
                <Button type="primary" onClick={() => navigate('/robots')}>创建/管理机器人</Button>
                <Button onClick={() => navigate('/chat')}>开始测试聊天</Button>
              </Space>
            </div>
            <div className="overview-steps">
              <div className="overview-step">
                <div className="step-index">1</div>
                <div>
                  <div className="step-title">机器人管理</div>
                  <div className="step-desc">创建机器人并绑定 Key</div>
                </div>
              </div>
              <div className="overview-step">
                <div className="step-index">2</div>
                <div>
                  <div className="step-title">知识库与策略</div>
                  <div className="step-desc">完善知识与业务策略</div>
                </div>
              </div>
              <div className="overview-step">
                <div className="step-index">3</div>
                <div>
                  <div className="step-title">测试与上线</div>
                  <div className="step-desc">测试聊天与运维检查</div>
                </div>
              </div>
            </div>
          </Card>

          <div className="overview-grid">
            <Card className="settings-card overview-card" title="机器人管理" styles={{ body: { padding: '20px' } }}>
              <Space direction="vertical" size={12} style={{ width: '100%' }}>
                <Text type="secondary">创建机器人、绑定 Key、管理列表</Text>
                <Button type="primary" onClick={() => navigate('/robots')}>进入机器人管理</Button>
              </Space>
            </Card>
            <Card className="settings-card overview-card" title="知识库" styles={{ body: { padding: '20px' } }}>
              <Space direction="vertical" size={12} style={{ width: '100%' }}>
                <Text type="secondary">维护知识条目与检索效果</Text>
                <Button type="primary" onClick={() => navigate('/knowledge')}>进入知识库</Button>
              </Space>
            </Card>
            <Card className="settings-card overview-card" title="策略配置" styles={{ body: { padding: '20px' } }}>
              <Space direction="vertical" size={12} style={{ width: '100%' }}>
                <Text type="secondary">自动发货、风控、意图路由</Text>
                <Button type="primary" onClick={() => navigate('/policies')}>进入策略配置</Button>
              </Space>
            </Card>
            <Card className="settings-card overview-card" title="模型管理" styles={{ body: { padding: '20px' } }}>
              <Space direction="vertical" size={12} style={{ width: '100%' }}>
                <Text type="secondary">模型切换、测试与状态</Text>
                <Button type="primary" onClick={() => navigate('/models')}>进入模型管理</Button>
              </Space>
            </Card>
            <Card className="settings-card overview-card" title="聊天设置" styles={{ body: { padding: '20px' } }}>
              <Space direction="vertical" size={12} style={{ width: '100%' }}>
                <Text type="secondary">提示词、记忆窗口、历史长度</Text>
                <Button type="primary" onClick={() => navigate('/chat-settings')}>进入聊天设置</Button>
              </Space>
            </Card>
            <Card className="settings-card overview-card" title="运维工具" styles={{ body: { padding: '20px' } }}>
              <Space direction="vertical" size={12} style={{ width: '100%' }}>
                <Text type="secondary">健康检查、订单回调测试</Text>
                <Button type="primary" onClick={() => navigate('/ops')}>进入运维工具</Button>
              </Space>
            </Card>
            <Card className="settings-card overview-card" title="测试聊天" styles={{ body: { padding: '20px' } }}>
              <Space direction="vertical" size={12} style={{ width: '100%' }}>
                <Text type="secondary">绑定机器人后进行对话验证</Text>
                <Button type="primary" onClick={() => navigate('/chat')}>进入测试聊天</Button>
              </Space>
            </Card>
          </div>
        </div>
      </Content>
    </Layout>
  );
};

export default OverviewPage;
