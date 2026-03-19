import React, { useState } from 'react';
import { Layout, Card, Typography, Input, Button, Space, message } from 'antd';
import { chatService } from '../services/chatService';
import './SettingsPage.css';

const { Content } = Layout;
const { Title, Text } = Typography;
const { TextArea } = Input;

const OpsPage: React.FC = () => {
  const [healthStatus, setHealthStatus] = useState<any | null>(null);
  const [healthLoading, setHealthLoading] = useState(false);
  const [orderPayload, setOrderPayload] = useState({
    session_id: '',
    user_id: '',
    order_id: '',
    item_id: '',
    status: '',
    raw_status: '',
    reply_text: ''
  });
  const [orderResult, setOrderResult] = useState<any | null>(null);
  const [orderLoading, setOrderLoading] = useState(false);

  const checkHealth = async () => {
    try {
      setHealthLoading(true);
      const data = await chatService.checkHealth();
      setHealthStatus(data);
      message.success('健康检查成功');
    } catch (error) {
      message.error('健康检查失败');
    } finally {
      setHealthLoading(false);
    }
  };

  const sendOrderCallback = async () => {
    try {
      setOrderLoading(true);
      const payload = {
        session_id: orderPayload.session_id || undefined,
        user_id: orderPayload.user_id || undefined,
        order_id: orderPayload.order_id || undefined,
        item_id: orderPayload.item_id || undefined,
        status: orderPayload.status || undefined,
        raw_status: orderPayload.raw_status || undefined,
        reply_text: orderPayload.reply_text || undefined
      };
      const data = await chatService.sendOrderCallback(payload);
      setOrderResult(data);
      message.success('订单回调请求已发送');
    } catch (error) {
      message.error('订单回调请求失败');
    } finally {
      setOrderLoading(false);
    }
  };

  return (
    <Layout className="settings-page">
      <Content className="settings-content">
        <div className="settings-container">
          <div className="settings-header">
            <Title level={2}>运维工具</Title>
            <Text type="secondary">用于诊断系统状态与业务回调</Text>
          </div>

          <Card
            title="系统健康检查"
            className="settings-card"
            styles={{ body: { padding: '24px' } }}
          >
            <Space direction="vertical" size={12} style={{ width: '100%' }}>
              <Text type="secondary">用于检查后端服务运行状态</Text>
              <Button type="primary" loading={healthLoading} onClick={checkHealth}>
                立即检查
              </Button>
              {healthStatus && (
                <div className="health-status">
                  <div className="health-row">
                    <Text type="secondary">状态:</Text>
                    <Text>{healthStatus.status || '-'}</Text>
                  </div>
                  <div className="health-row">
                    <Text type="secondary">版本:</Text>
                    <Text>{healthStatus.version || '-'}</Text>
                  </div>
                  <div className="health-row">
                    <Text type="secondary">服务:</Text>
                    <Text>{healthStatus.services ? JSON.stringify(healthStatus.services) : '-'}</Text>
                  </div>
                </div>
              )}
            </Space>
          </Card>

          <Card
            title="订单回调测试"
            className="settings-card"
            styles={{ body: { padding: '24px' } }}
            style={{ marginTop: 24 }}
          >
            <Space direction="vertical" size={12} style={{ width: '100%' }}>
              <Text type="secondary">模拟订单状态回调，用于验证自动发货逻辑</Text>
              <Input
                value={orderPayload.session_id}
                onChange={(e) => setOrderPayload({ ...orderPayload, session_id: e.target.value })}
                placeholder="会话ID（可选）"
              />
              <Input
                value={orderPayload.user_id}
                onChange={(e) => setOrderPayload({ ...orderPayload, user_id: e.target.value })}
                placeholder="用户ID（可选）"
              />
              <Input
                value={orderPayload.order_id}
                onChange={(e) => setOrderPayload({ ...orderPayload, order_id: e.target.value })}
                placeholder="订单ID"
              />
              <Input
                value={orderPayload.item_id}
                onChange={(e) => setOrderPayload({ ...orderPayload, item_id: e.target.value })}
                placeholder="商品ID"
              />
              <Input
                value={orderPayload.status}
                onChange={(e) => setOrderPayload({ ...orderPayload, status: e.target.value })}
                placeholder="状态字段（status）"
              />
              <Input
                value={orderPayload.raw_status}
                onChange={(e) => setOrderPayload({ ...orderPayload, raw_status: e.target.value })}
                placeholder="原始状态文案（raw_status）"
              />
              <TextArea
                value={orderPayload.reply_text}
                onChange={(e) => setOrderPayload({ ...orderPayload, reply_text: e.target.value })}
                rows={3}
                placeholder="自定义回复内容（可选）"
              />
              <Button type="primary" loading={orderLoading} onClick={sendOrderCallback}>
                发送回调
              </Button>
              {orderResult && (
                <pre className="json-preview">{JSON.stringify(orderResult, null, 2)}</pre>
              )}
            </Space>
          </Card>
        </div>
      </Content>
    </Layout>
  );
};

export default OpsPage;
