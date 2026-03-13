import React, { useEffect, useState } from 'react';
import { Layout, Card, Typography, Divider, Switch, Input, Button, Space, message } from 'antd';
import { SettingOutlined } from '@ant-design/icons';
import ModelSelector from '../components/ModelSelector';
import { chatService } from '../services/chatService';
import './SettingsPage.css';

/**
 * 设置页面组件
 * 提供系统配置和模型设置功能
 */

const { Content } = Layout;
const { Title, Text } = Typography;
const { TextArea } = Input;

const SettingsPage: React.FC = () => {
  const [policy, setPolicy] = useState<any | null>(null);
  const [saving, setSaving] = useState(false);
  const [tenantKey, setTenantKey] = useState('');
  const [adminUsername, setAdminUsername] = useState('');
  const [adminPassword, setAdminPassword] = useState('');
  const [adminLoading, setAdminLoading] = useState(false);
  const [tenantName, setTenantName] = useState('');
  const [tenantId, setTenantId] = useState('');
  const [tenantApiKey, setTenantApiKey] = useState('');
  const [tenantModelProvider, setTenantModelProvider] = useState('openrouter');
  const [tenantModelConfig, setTenantModelConfig] = useState('{
  "api_key": "",
  "api_base": "https://openrouter.ai/api/v1",
  "model": "openai/gpt-4o-mini"
}');
  const [tenantLoading, setTenantLoading] = useState(false);
  const [tenantList, setTenantList] = useState<any[]>([]);

  /**
   * 处理模型变更
   */
  const handleModelChange = (provider: string, model: string) => {
    console.log('模型已切换:', { provider, model });
  };

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
    setTenantKey(localStorage.getItem('tenant_key') || '');
  }, []);

  const refreshTenants = async () => {
    try {
      const data = await chatService.listTenants();
      setTenantList(data.tenants || []);
    } catch (error) {
      message.error('获取租户列表失败');
    }
  };

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
          {!policy && (
            <Card className="settings-card" styles={{ body: { padding: '24px' } }}>
              <Text type="secondary">正在加载策略配置...</Text>
            </Card>
          )}

          {/* 页面标题 */}
          <div className="settings-header">
            <Title level={2}>
              <SettingOutlined /> 系统设置
            </Title>
            <Text type="secondary">
              在这里配置您的智能客服系统参数
            </Text>
          </div>

          <Card
            title="租户接入"
            className="settings-card"
            styles={{ body: { padding: '24px' } }}
          >
            <Space direction="vertical" size={12} style={{ width: '100%' }}>
              <Text type="secondary">用于隔离不同用户的模型配置与知识库内容</Text>
              <Input
                value={tenantKey}
                onChange={(e) => setTenantKey(e.target.value)}
                placeholder="输入租户 Key（X-Tenant-Key）"
              />
              <Button
                type="primary"
                onClick={() => {
                  localStorage.setItem('tenant_key', tenantKey.trim());
                  message.success('租户 Key 已保存');
                }}
              >
                保存租户 Key
              </Button>
            </Space>
          </Card>

          <Divider />

          <Card
            title="管理员登录"
            className="settings-card"
            styles={{ body: { padding: '24px' } }}
          >
            <Space direction="vertical" size={12} style={{ width: '100%' }}>
              <Input
                value={adminUsername}
                onChange={(e) => setAdminUsername(e.target.value)}
                placeholder="管理员账号"
              />
              <Input.Password
                value={adminPassword}
                onChange={(e) => setAdminPassword(e.target.value)}
                placeholder="管理员密码"
              />
              <Space>
                <Button
                  type="primary"
                  loading={adminLoading}
                  onClick={async () => {
                    try {
                      setAdminLoading(true);
                      await chatService.adminLogin(adminUsername, adminPassword);
                      message.success('管理员登录成功');
                    } catch (error) {
                      message.error('管理员登录失败');
                    } finally {
                      setAdminLoading(false);
                    }
                  }}
                >
                  登录
                </Button>
                <Button
                  onClick={() => {
                    chatService.clearAuthToken();
                    message.success('已退出登录');
                  }}
                >
                  退出
                </Button>
              </Space>
            </Space>
          </Card>

          <Divider />

          <Card
            title="租户管理（管理员）"
            className="settings-card"
            styles={{ body: { padding: '24px' } }}
          >
            <Space direction="vertical" size={12} style={{ width: '100%' }}>
              <Text type="secondary">创建租户并配置模型，返回的 Key 用于对外接入</Text>
              <Input
                value={tenantName}
                onChange={(e) => setTenantName(e.target.value)}
                placeholder="租户名称（如 shop_a）"
              />
              <Input
                value={tenantId}
                onChange={(e) => setTenantId(e.target.value)}
                placeholder="租户 ID（用于读取/更新）"
              />
              <Input
                value={tenantApiKey}
                onChange={(e) => setTenantApiKey(e.target.value)}
                placeholder="租户 API Key（可留空自动生成）"
              />
              <Input
                value={tenantModelProvider}
                onChange={(e) => setTenantModelProvider(e.target.value)}
                placeholder="模型提供商（openrouter/openai/custom）"
              />
              <TextArea
                value={tenantModelConfig}
                onChange={(e) => setTenantModelConfig(e.target.value)}
                rows={6}
                placeholder="模型配置 JSON"
              />
              <Space>
                <Button
                  type="primary"
                  loading={tenantLoading}
                  onClick={async () => {
                    try {
                      setTenantLoading(true);
                      const config = tenantModelConfig ? JSON.parse(tenantModelConfig) : undefined;
                      const data = await chatService.createTenant({
                        name: tenantName,
                        api_key: tenantApiKey || undefined,
                        model_provider: tenantModelProvider || undefined,
                        model_config: config
                      });
                      setTenantId(data.tenant_id || '');
                      setTenantApiKey(data.api_key || '');
                      message.success('租户创建成功');
                    } catch (error) {
                      message.error('租户创建失败');
                    } finally {
                      setTenantLoading(false);
                    }
                  }}
                >
                  创建租户
                </Button>
                <Button
                  onClick={async () => {
                    try {
                      setTenantLoading(true);
                      const data = await chatService.getTenantConfig(tenantId);
                      setTenantModelProvider(data.model_provider || tenantModelProvider);
                      setTenantModelConfig(JSON.stringify(data.model_config || {}, null, 2));
                      message.success('已加载租户配置');
                    } catch (error) {
                      message.error('获取租户配置失败');
                    } finally {
                      setTenantLoading(false);
                    }
                  }}
                >
                  读取配置
                </Button>
                <Button
                  onClick={async () => {
                    try {
                      setTenantLoading(true);
                      const config = tenantModelConfig ? JSON.parse(tenantModelConfig) : undefined;
                      await chatService.updateTenantConfig(tenantId, {
                        api_key: tenantApiKey || undefined,
                        model_provider: tenantModelProvider || undefined,
                        model_config: config
                      });
                      message.success('租户配置更新成功');
                    } catch (error) {
                      message.error('更新租户配置失败');
                    } finally {
                      setTenantLoading(false);
                    }
                  }}
                >
                  更新配置
                </Button>
                <Button
                  onClick={async () => {
                    await refreshTenants();
                  }}
                >
                  刷新列表
                </Button>
              </Space>
              {tenantList.length > 0 && (
                <div className="tenant-list">
                  {tenantList.map((tenant) => (
                    <div key={tenant.tenant_id} className="tenant-item">
                      <div className="tenant-info">
                        <div className="tenant-name">{tenant.name}</div>
                        <div className="tenant-meta">ID: {tenant.tenant_id}</div>
                        <div className="tenant-meta">Key: {tenant.api_key}</div>
                      </div>
                      <Space>
                        <Button
                          size="small"
                          onClick={() => {
                            setTenantId(tenant.tenant_id);
                            setTenantApiKey(tenant.api_key);
                            message.success('已填充租户信息');
                          }}
                        >
                          填充
                        </Button>
                        <Button
                          size="small"
                          onClick={async () => {
                            try {
                              const data = await chatService.resetTenantKey(tenant.tenant_id);
                              message.success('Key 已重置');
                              await refreshTenants();
                              setTenantApiKey(data.api_key || '');
                            } catch (error) {
                              message.error('重置Key失败');
                            }
                          }}
                        >
                          重置Key
                        </Button>
                      </Space>
                    </div>
                  ))}
                </div>
              )}
            </Space>
          </Card>

          <Divider />
          {policy && (
            <>
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

              {/* 自动发货配置 */}
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

              {/* 意图路由配置 */}
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

              {/* 风控配置 */}
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

              {/* 人工接管策略 */}
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
                  <Text type="secondary">
                    开启后，可在聊天页对单个会话手动切换人工接管。
                  </Text>
                </Space>
              </Card>
            </>
          )}
        </div>
      </Content>
    </Layout>
  );
};

export default SettingsPage;
