import React, { useEffect, useState } from 'react';
import { Layout, Card, Typography, Divider, Switch, Input, Button, Space, message } from 'antd';
import { chatService } from '../services/chatService';
import './SettingsPage.css';

const { Content } = Layout;
const { Title, Text } = Typography;
const { TextArea } = Input;

const PoliciesPage: React.FC = () => {
  const [policy, setPolicy] = useState<any | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const loadPolicy = async () => {
      try {
        const data = await chatService.getPolicy();
        setPolicy(data);
      } catch (error) {
        message.error('加载策略配置失败');
      }
    };
    loadPolicy();
  }, []);

  const savePolicy = async (updates: any) => {
    if (!policy) return;
    try {
      setSaving(true);
      const newPolicy = await chatService.updatePolicy(updates);
      setPolicy(newPolicy);
      message.success('策略已保存');
    } catch (error) {
      message.error('保存策略失败');
    } finally {
      setSaving(false);
    }
  };

  return (
    <Layout className="settings-page">
      <Content className="settings-content">
        <div className="settings-container">
          <div className="settings-header">
            <Title level={2}>策略配置</Title>
            <Text type="secondary">统一管理机器人自动回复与风控策略</Text>
          </div>

          {policy && (
            <>
              <Card
                title="自动发货（虚拟交易）"
                className="settings-card"
                styles={{ body: { padding: '24px' } }}
              >
                <Space direction="vertical" size={12} style={{ width: '100%' }}>
                  <Space size={12}>
                    <Text>启用自动发货</Text>
                    <Switch
                      checked={!!policy?.auto_ship?.enabled}
                      onChange={(checked) =>
                        savePolicy({ auto_ship: { ...policy?.auto_ship, enabled: checked } })
                      }
                    />
                  </Space>
                  <TextArea
                    value={policy?.auto_ship?.reply_text}
                    onChange={(e) =>
                      setPolicy({
                        ...policy,
                        auto_ship: { ...policy?.auto_ship, reply_text: e.target.value }
                      })
                    }
                    rows={3}
                    placeholder="自动发货回复内容"
                  />
                  <Button
                    type="primary"
                    loading={saving}
                    onClick={() => savePolicy({ auto_ship: policy?.auto_ship })}
                  >
                    保存自动发货配置
                  </Button>
                </Space>
              </Card>

              <Divider />

              <Card
                title="意图路由与议价"
                className="settings-card"
                styles={{ body: { padding: '24px' } }}
              >
                <Space direction="vertical" size={12} style={{ width: '100%' }}>
                  <Text type="secondary">用于识别技术咨询与议价场景</Text>
                  <TextArea
                    value={(policy?.intent_routing?.price_keywords || []).join('，')}
                    onChange={(e) =>
                      setPolicy({
                        ...policy,
                        intent_routing: {
                          ...policy?.intent_routing,
                          price_keywords: e.target.value.split('，').map(item => item.trim()).filter(Boolean)
                        }
                      })
                    }
                    rows={2}
                    placeholder="议价关键词（用中文逗号分隔）"
                  />
                  <TextArea
                    value={(policy?.intent_routing?.tech_keywords || []).join('，')}
                    onChange={(e) =>
                      setPolicy({
                        ...policy,
                        intent_routing: {
                          ...policy?.intent_routing,
                          tech_keywords: e.target.value.split('，').map(item => item.trim()).filter(Boolean)
                        }
                      })
                    }
                    rows={2}
                    placeholder="技术关键词（用中文逗号分隔）"
                  />
                  <Button
                    type="primary"
                    loading={saving}
                    onClick={() => savePolicy({ intent_routing: policy?.intent_routing })}
                  >
                    保存意图路由配置
                  </Button>
                </Space>
              </Card>

              <Divider />

              <Card
                title="风控提醒"
                className="settings-card"
                styles={{ body: { padding: '24px' } }}
              >
                <Space direction="vertical" size={12} style={{ width: '100%' }}>
                  <Space size={12}>
                    <Text>启用风控提醒</Text>
                    <Switch
                      checked={!!policy?.risk_guard?.enabled}
                      onChange={(checked) =>
                        savePolicy({ risk_guard: { ...policy?.risk_guard, enabled: checked } })
                      }
                    />
                  </Space>
                  <TextArea
                    value={(policy?.risk_guard?.blocked_keywords || []).join('，')}
                    onChange={(e) =>
                      setPolicy({
                        ...policy,
                        risk_guard: {
                          ...policy?.risk_guard,
                          blocked_keywords: e.target.value.split('，').map(item => item.trim()).filter(Boolean)
                        }
                      })
                    }
                    rows={2}
                    placeholder="风险关键词（用中文逗号分隔）"
                  />
                  <TextArea
                    value={policy?.risk_guard?.reply_text}
                    onChange={(e) =>
                      setPolicy({
                        ...policy,
                        risk_guard: { ...policy?.risk_guard, reply_text: e.target.value }
                      })
                    }
                    rows={2}
                    placeholder="风控提示文案"
                  />
                  <Button
                    type="primary"
                    loading={saving}
                    onClick={() => savePolicy({ risk_guard: policy?.risk_guard })}
                  >
                    保存风控配置
                  </Button>
                </Space>
              </Card>

              <Divider />

              <Card
                title="人工接管"
                className="settings-card"
                styles={{ body: { padding: '24px' } }}
              >
                <Space direction="vertical" size={12} style={{ width: '100%' }}>
                  <Space size={12}>
                    <Text>启用人工接管策略</Text>
                    <Switch
                      checked={!!policy?.manual_takeover?.enabled}
                      onChange={(checked) =>
                        savePolicy({ manual_takeover: { ...policy?.manual_takeover, enabled: checked } })
                      }
                    />
                  </Space>
                  <Text type="secondary">开启后，可在聊天页对单个会话手动切换人工接管。</Text>
                </Space>
              </Card>
            </>
          )}
        </div>
      </Content>
    </Layout>
  );
};

export default PoliciesPage;
