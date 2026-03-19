import React, { useEffect, useState } from 'react';
import { Layout, Card, Typography, Divider, Input, Button, Space, message, Switch, Tag } from 'antd';
import { chatService } from '../services/chatService';
import './SettingsPage.css';

const { Content } = Layout;
const { Title, Text } = Typography;
const { TextArea } = Input;

const RobotsPage: React.FC = () => {
  const [tenantKey, setTenantKey] = useState('');
  const [adminUsername, setAdminUsername] = useState('');
  const [adminPassword, setAdminPassword] = useState('');
  const [adminLoading, setAdminLoading] = useState(false);
  const [adminInfo, setAdminInfo] = useState<any | null>(null);
  const [adminInfoLoading, setAdminInfoLoading] = useState(false);
  const [tenantName, setTenantName] = useState('');
  const [tenantId, setTenantId] = useState('');
  const [tenantApiKey, setTenantApiKey] = useState('');
  const [tenantModelProvider, setTenantModelProvider] = useState('openrouter');
  const [tenantModelApiKey, setTenantModelApiKey] = useState('');
  const [tenantModelConfig, setTenantModelConfig] = useState(`{
  "api_key": "",
  "api_base": "https://openrouter.ai/api/v1",
  "model": "openai/gpt-4o-mini"
}`);
  const [tenantLoading, setTenantLoading] = useState(false);
  const [tenantList, setTenantList] = useState<any[]>([]);
  const [xianyuEnabled, setXianyuEnabled] = useState(true);
  const [xianyuSellerName, setXianyuSellerName] = useState('');
  const [xianyuCookies, setXianyuCookies] = useState('');
  const [xianyuMasked, setXianyuMasked] = useState('');
  const [xianyuHasCookies, setXianyuHasCookies] = useState(false);
  const [xianyuLoading, setXianyuLoading] = useState(false);

  useEffect(() => {
    setTenantKey(localStorage.getItem('tenant_key') || '');
    if (chatService.getAuthToken()) {
      refreshTenants();
    }
  }, []);

  const refreshTenants = async () => {
    try {
      if (!chatService.getAuthToken()) {
        message.warning('请先管理员登录后查看机器人列表');
        return;
      }
      const data = await chatService.listTenants();
      setTenantList(data.tenants || []);
    } catch (error) {
      message.error('获取机器人列表失败');
    }
  };

  const fetchAdminInfo = async () => {
    try {
      setAdminInfoLoading(true);
      const data = await chatService.getAdminMe();
      setAdminInfo(data);
    } catch (error) {
      message.error('获取管理员信息失败');
    } finally {
      setAdminInfoLoading(false);
    }
  };

  const loadXianyuConfig = async () => {
    if (!tenantId) {
      message.warning('请先填写机器人 ID');
      return;
    }
    try {
      setXianyuLoading(true);
      const data = await chatService.getTenantXianyuConfig(tenantId);
      setXianyuEnabled(!!data.enabled);
      setXianyuSellerName(data.seller_name || '');
      setXianyuMasked(data.cookies_masked || '');
      setXianyuHasCookies(!!data.has_cookies);
      setXianyuCookies('');
      message.success('已加载闲鱼账号配置');
    } catch (error) {
      message.error('加载闲鱼账号配置失败');
    } finally {
      setXianyuLoading(false);
    }
  };

  const saveXianyuConfig = async () => {
    if (!tenantId) {
      message.warning('请先填写机器人 ID');
      return;
    }
    try {
      setXianyuLoading(true);
      const payload: { cookies?: string; seller_name?: string; enabled?: boolean } = {
        seller_name: xianyuSellerName,
        enabled: xianyuEnabled
      };
      if (xianyuCookies.trim()) {
        payload.cookies = xianyuCookies.trim();
      }
      const data = await chatService.updateTenantXianyuConfig(tenantId, payload);
      setXianyuMasked(data.cookies_masked || '');
      setXianyuHasCookies(!!data.has_cookies);
      setXianyuCookies('');
      message.success('闲鱼账号配置已保存');
    } catch (error) {
      message.error('保存闲鱼账号配置失败');
    } finally {
      setXianyuLoading(false);
    }
  };

  return (
    <Layout className="settings-page">
      <Content className="settings-content">
        <div className="settings-container">
          <div className="settings-header">
            <Title level={2}>客服机器人管理</Title>
            <Text type="secondary">创建机器人、绑定 Key，并进行管理配置</Text>
          </div>

          <Card
            title="已创建机器人"
            className="settings-card"
            styles={{ body: { padding: '24px' } }}
            extra={<Button onClick={refreshTenants}>刷新列表</Button>}
          >
            <div className="robot-list">
              {tenantList.length === 0 ? (
                <Text type="secondary">暂无机器人，请先创建</Text>
              ) : (
                tenantList.map((tenant) => (
                  <div key={tenant.tenant_id} className="robot-card">
                    <div>
                      <div className="robot-name">{tenant.name}</div>
                      <div className="robot-meta">ID: {tenant.tenant_id}</div>
                      <div className="robot-meta">Key: {tenant.api_key}</div>
                    </div>
                    <Space>
                      <Button
                        size="small"
                        onClick={() => {
                          setTenantId(tenant.tenant_id);
                          setTenantApiKey(tenant.api_key);
                          setTenantName(tenant.name || '');
                          message.success('已选择机器人');
                        }}
                      >
                        选择
                      </Button>
                      <Button
                        size="small"
                        onClick={() => {
                          localStorage.setItem('tenant_key', tenant.api_key);
                          setTenantKey(tenant.api_key);
                          message.success('已设为当前机器人');
                        }}
                      >
                        设为当前
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
                ))
              )}
            </div>
          </Card>

          <Divider />

          <Card
            title="当前机器人 Key"
            className="settings-card"
            styles={{ body: { padding: '24px' } }}
          >
            <Space direction="vertical" size={12} style={{ width: '100%' }}>
              <Text type="secondary">用于聊天测试与数据隔离（X-Tenant-Key）</Text>
              <Input
                value={tenantKey}
                onChange={(e) => setTenantKey(e.target.value)}
                placeholder="输入机器人 Key"
              />
              <Button
                type="primary"
                onClick={() => {
                  localStorage.setItem('tenant_key', tenantKey.trim());
                  message.success('机器人 Key 已保存');
                }}
              >
                保存机器人 Key
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
                      await refreshTenants();
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
                    setTenantList([]);
                  }}
                >
                  退出
                </Button>
              </Space>
            </Space>
          </Card>

          <Divider />

          <Card
            title="管理员信息"
            className="settings-card"
            styles={{ body: { padding: '24px' } }}
          >
            <Space direction="vertical" size={12} style={{ width: '100%' }}>
              <Text type="secondary">需要管理员登录后才能获取信息</Text>
              <Space>
                <Button type="primary" loading={adminInfoLoading} onClick={fetchAdminInfo}>
                  获取管理员信息
                </Button>
                <Button onClick={() => setAdminInfo(null)}>清空</Button>
              </Space>
              <div className="admin-info">
                <div className="admin-info-row">
                  <Text type="secondary">登录状态:</Text>
                  <Text>{chatService.getAuthToken() ? '已登录' : '未登录'}</Text>
                </div>
                <div className="admin-info-row">
                  <Text type="secondary">用户名:</Text>
                  <Text>{adminInfo?.username || '-'}</Text>
                </div>
              </div>
            </Space>
          </Card>

          <Divider />

          <Card
            title="机器人创建与配置"
            className="settings-card"
            styles={{ body: { padding: '24px' } }}
          >
            <Space direction="vertical" size={12} style={{ width: '100%' }}>
              <Text type="secondary">创建机器人并配置模型，返回的 Key 用于对外接入</Text>
              <Input
                value={tenantName}
                onChange={(e) => setTenantName(e.target.value)}
                placeholder="机器人名称（如 shop_a）"
              />
              <Input
                value={tenantId}
                onChange={(e) => setTenantId(e.target.value)}
                placeholder="机器人 ID（用于读取/更新）"
              />
              <Input
                value={tenantApiKey}
                onChange={(e) => setTenantApiKey(e.target.value)}
                placeholder="机器人 Key（可留空自动生成）"
              />
              <Input
                value={tenantModelProvider}
                onChange={(e) => setTenantModelProvider(e.target.value)}
                placeholder="模型提供商（openrouter/openai/custom）"
              />
              <Input
                value={tenantModelApiKey}
                onChange={(e) => setTenantModelApiKey(e.target.value)}
                placeholder="模型 API Key（可选，优先生效）"
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
                      if (config && tenantModelApiKey.trim()) {
                        config.api_key = tenantModelApiKey.trim();
                      }
                      const data = await chatService.createTenant({
                        name: tenantName,
                        api_key: tenantApiKey || undefined,
                        model_provider: tenantModelProvider || undefined,
                        model_config: config
                      });
                      setTenantApiKey(data.api_key || '');
                      setTenantId(data.tenant_id || '');
                      message.success('机器人创建成功');
                      await refreshTenants();
                    } catch (error) {
                      message.error('机器人创建失败');
                    } finally {
                      setTenantLoading(false);
                    }
                  }}
                >
                  创建机器人
                </Button>
                <Button
                  loading={tenantLoading}
                  onClick={async () => {
                    try {
                      setTenantLoading(true);
                      const data = await chatService.getTenantConfig(tenantId);
                      setTenantModelProvider(data.model_provider || tenantModelProvider);
                      setTenantModelConfig(JSON.stringify(data.model_config || {}, null, 2));
                      if (data.model_config?.api_key) {
                        setTenantModelApiKey(data.model_config.api_key);
                      }
                      message.success('已加载机器人配置');
                    } catch (error) {
                      message.error('获取机器人配置失败');
                    } finally {
                      setTenantLoading(false);
                    }
                  }}
                >
                  读取配置
                </Button>
                <Button
                  loading={tenantLoading}
                  onClick={async () => {
                    try {
                      setTenantLoading(true);
                      const config = tenantModelConfig ? JSON.parse(tenantModelConfig) : undefined;
                      if (config && tenantModelApiKey.trim()) {
                        config.api_key = tenantModelApiKey.trim();
                      }
                      await chatService.updateTenantConfig(tenantId, {
                        api_key: tenantApiKey || undefined,
                        model_provider: tenantModelProvider || undefined,
                        model_config: config
                      });
                      message.success('机器人配置更新成功');
                    } catch (error) {
                      message.error('更新机器人配置失败');
                    } finally {
                      setTenantLoading(false);
                    }
                  }}
                >
                  更新配置
                </Button>
              </Space>
            </Space>
          </Card>

          <Divider />

          <Card
            title="闲鱼账号绑定"
            className="settings-card"
            styles={{ body: { padding: '24px' } }}
          >
            <Space direction="vertical" size={12} style={{ width: '100%' }}>
              <Text type="secondary">将闲鱼账号绑定到机器人，用于消息接入与商品信息拉取</Text>
              <Input
                value={tenantId}
                onChange={(e) => setTenantId(e.target.value)}
                placeholder="机器人 ID"
              />
              <Input
                value={xianyuSellerName}
                onChange={(e) => setXianyuSellerName(e.target.value)}
                placeholder="闲鱼账号名称（可选）"
              />
              <TextArea
                value={xianyuCookies}
                onChange={(e) => setXianyuCookies(e.target.value)}
                rows={4}
                placeholder={xianyuHasCookies ? `当前已绑定：${xianyuMasked || '已保存'}` : '粘贴闲鱼 Cookies'}
              />
              <Space>
                <Button type="primary" loading={xianyuLoading} onClick={saveXianyuConfig}>
                  保存绑定
                </Button>
                <Button loading={xianyuLoading} onClick={loadXianyuConfig}>
                  读取配置
                </Button>
                {xianyuHasCookies && (
                  <Tag color="green">已绑定</Tag>
                )}
              </Space>
              <Space size={12}>
                <Text>启用闲鱼接入</Text>
                <Switch checked={xianyuEnabled} onChange={setXianyuEnabled} />
              </Space>
            </Space>
          </Card>
        </div>
      </Content>
    </Layout>
  );
};

export default RobotsPage;
