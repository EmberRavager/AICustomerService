import React, { useEffect, useState } from 'react';
import { Layout, Card, Typography, Input, Button, Space, message, Tabs, Select, Table, Tag, Popconfirm, Divider } from 'antd';
import { chatService } from '../services/chatService';
import { KnowledgeItem } from '../types/chat';
import './SettingsPage.css';

const { Content } = Layout;
const { Title, Text } = Typography;
const { TextArea } = Input;

const KnowledgeBasePage: React.FC = () => {
  const [knowledgeItems, setKnowledgeItems] = useState<KnowledgeItem[]>([]);
  const [knowledgeLoading, setKnowledgeLoading] = useState(false);
  const [knowledgeCategories, setKnowledgeCategories] = useState<string[]>([]);
  const [knowledgeCategoryFilter, setKnowledgeCategoryFilter] = useState<string | undefined>(undefined);
  const [knowledgeSearchQuery, setKnowledgeSearchQuery] = useState('');
  const [knowledgeSearchType, setKnowledgeSearchType] = useState('hybrid');
  const [knowledgeSearchResults, setKnowledgeSearchResults] = useState<KnowledgeItem[] | null>(null);
  const [knowledgeActiveTab, setKnowledgeActiveTab] = useState('list');
  const [knowledgeForm, setKnowledgeForm] = useState({
    id: '',
    title: '',
    content: '',
    category: '',
    tags: ''
  });
  const [batchPayload, setBatchPayload] = useState('');

  const parseTags = (value: string): string[] => {
    return value
      .split(/[,，]/)
      .map(tag => tag.trim())
      .filter(Boolean);
  };

  const formatTags = (tags?: string[]): string => {
    return tags ? tags.join('，') : '';
  };

  const loadKnowledgeCategories = async () => {
    try {
      const data = await chatService.getKnowledgeCategories();
      setKnowledgeCategories(data);
    } catch (error) {
      message.error('加载知识库分类失败');
    }
  };

  const loadKnowledgeList = async () => {
    try {
      setKnowledgeLoading(true);
      const data = await chatService.listKnowledge(knowledgeCategoryFilter, 20, 0);
      setKnowledgeItems(data);
      setKnowledgeSearchResults(null);
    } catch (error) {
      message.error('加载知识库列表失败');
    } finally {
      setKnowledgeLoading(false);
    }
  };

  const searchKnowledge = async () => {
    if (!knowledgeSearchQuery.trim()) {
      message.warning('请输入搜索关键词');
      return;
    }
    try {
      setKnowledgeLoading(true);
      const data = await chatService.searchKnowledge(
        knowledgeSearchQuery.trim(),
        10,
        knowledgeSearchType
      );
      setKnowledgeSearchResults(data);
    } catch (error) {
      message.error('搜索知识库失败');
    } finally {
      setKnowledgeLoading(false);
    }
  };

  const resetKnowledgeForm = () => {
    setKnowledgeForm({
      id: '',
      title: '',
      content: '',
      category: '',
      tags: ''
    });
  };

  const saveKnowledge = async () => {
    if (!knowledgeForm.title.trim() || !knowledgeForm.content.trim()) {
      message.warning('请填写标题和内容');
      return;
    }

    const payload: KnowledgeItem = {
      title: knowledgeForm.title.trim(),
      content: knowledgeForm.content.trim(),
      category: knowledgeForm.category.trim() || undefined,
      tags: parseTags(knowledgeForm.tags)
    };

    try {
      setKnowledgeLoading(true);
      if (knowledgeForm.id) {
        await chatService.updateKnowledge(knowledgeForm.id, payload);
        message.success('知识库条目已更新');
      } else {
        await chatService.addKnowledge(payload);
        message.success('知识库条目已新增');
      }
      await loadKnowledgeList();
      await loadKnowledgeCategories();
      resetKnowledgeForm();
      setKnowledgeActiveTab('list');
    } catch (error) {
      message.error('保存知识库条目失败');
    } finally {
      setKnowledgeLoading(false);
    }
  };

  const deleteKnowledge = async (id?: string) => {
    if (!id) return;
    try {
      setKnowledgeLoading(true);
      await chatService.deleteKnowledge(id);
      message.success('知识库条目已删除');
      await loadKnowledgeList();
      await loadKnowledgeCategories();
    } catch (error) {
      message.error('删除知识库条目失败');
    } finally {
      setKnowledgeLoading(false);
    }
  };

  const batchAddKnowledge = async () => {
    if (!batchPayload.trim()) {
      message.warning('请输入批量数据');
      return;
    }
    try {
      const parsed = JSON.parse(batchPayload);
      if (!Array.isArray(parsed)) {
        message.error('批量数据必须是数组');
        return;
      }
      setKnowledgeLoading(true);
      await chatService.batchAddKnowledge(parsed);
      message.success('批量导入完成');
      setBatchPayload('');
      await loadKnowledgeList();
      await loadKnowledgeCategories();
    } catch (error: any) {
      message.error(error?.message || '批量导入失败');
    } finally {
      setKnowledgeLoading(false);
    }
  };

  useEffect(() => {
    loadKnowledgeCategories();
    loadKnowledgeList();
  }, []);

  useEffect(() => {
    loadKnowledgeList();
  }, [knowledgeCategoryFilter]);

  const knowledgeData = knowledgeSearchResults ?? knowledgeItems;

  const knowledgeColumns = [
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      render: (value: string) => <span className="knowledge-title">{value}</span>
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      render: (value: string) => (value ? <Tag>{value}</Tag> : <span className="muted">未分类</span>)
    },
    {
      title: '标签',
      dataIndex: 'tags',
      key: 'tags',
      render: (tags: string[]) => (
        <Space size={[4, 4]} wrap>
          {(tags || []).length === 0 && <span className="muted">无</span>}
          {(tags || []).map(tag => (
            <Tag key={tag} color="blue">{tag}</Tag>
          ))}
        </Space>
      )
    },
    {
      title: '更新时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      render: (_: string, record: KnowledgeItem) => (
        <span className="muted">{record.updated_at || record.created_at || '-'}</span>
      )
    },
    {
      title: '操作',
      key: 'actions',
      render: (_: any, record: KnowledgeItem) => (
        <Space size="small">
          <Button
            size="small"
            onClick={() => {
              setKnowledgeForm({
                id: record.id || '',
                title: record.title,
                content: record.content,
                category: record.category || '',
                tags: formatTags(record.tags)
              });
              setKnowledgeActiveTab('edit');
            }}
          >
            编辑
          </Button>
          <Popconfirm
            title="确认删除该条目？"
            okText="删除"
            cancelText="取消"
            onConfirm={() => deleteKnowledge(record.id)}
          >
            <Button size="small" danger>删除</Button>
          </Popconfirm>
        </Space>
      )
    }
  ];

  return (
    <Layout className="settings-page">
      <Content className="settings-content">
        <div className="settings-container">
          <div className="settings-header">
            <Title level={2}>知识库管理</Title>
            <Text type="secondary">维护机器人知识库内容与检索效果</Text>
          </div>

          <Card
            title="知识库管理"
            className="settings-card"
            styles={{ body: { padding: '24px' } }}
          >
            <Tabs
              activeKey={knowledgeActiveTab}
              onChange={setKnowledgeActiveTab}
              items={[
                {
                  key: 'list',
                  label: '列表与搜索',
                  children: (
                    <Space direction="vertical" size={16} style={{ width: '100%' }}>
                      <div className="knowledge-toolbar">
                        <Input
                          value={knowledgeSearchQuery}
                          onChange={(e) => setKnowledgeSearchQuery(e.target.value)}
                          placeholder="输入关键词搜索"
                          style={{ width: 240 }}
                        />
                        <Select
                          value={knowledgeSearchType}
                          onChange={setKnowledgeSearchType}
                          style={{ width: 140 }}
                          options={[
                            { label: '混合检索', value: 'hybrid' },
                            { label: '向量检索', value: 'vector' },
                            { label: '关键词检索', value: 'keyword' }
                          ]}
                        />
                        <Select
                          value={knowledgeCategoryFilter}
                          onChange={(value) => setKnowledgeCategoryFilter(value)}
                          placeholder="全部分类"
                          style={{ width: 160 }}
                          allowClear
                          options={knowledgeCategories.map(category => ({ label: category, value: category }))}
                        />
                        <Button onClick={searchKnowledge} loading={knowledgeLoading}>
                          搜索
                        </Button>
                        <Button
                          onClick={() => {
                            setKnowledgeSearchQuery('');
                            setKnowledgeSearchResults(null);
                          }}
                        >
                          清空搜索
                        </Button>
                        <Button onClick={loadKnowledgeList} loading={knowledgeLoading}>
                          刷新列表
                        </Button>
                      </div>
                      <Table
                        rowKey={(record) => record.id || record.title}
                        dataSource={knowledgeData}
                        columns={knowledgeColumns}
                        loading={knowledgeLoading}
                        pagination={false}
                        className="knowledge-table"
                      />
                    </Space>
                  )
                },
                {
                  key: 'edit',
                  label: knowledgeForm.id ? '编辑条目' : '新增条目',
                  children: (
                    <Space direction="vertical" size={16} style={{ width: '100%' }}>
                      <Input
                        value={knowledgeForm.id}
                        disabled
                        placeholder="条目ID（新增时自动生成）"
                      />
                      <Input
                        value={knowledgeForm.title}
                        onChange={(e) => setKnowledgeForm({ ...knowledgeForm, title: e.target.value })}
                        placeholder="标题"
                      />
                      <Input
                        value={knowledgeForm.category}
                        onChange={(e) => setKnowledgeForm({ ...knowledgeForm, category: e.target.value })}
                        placeholder="分类"
                      />
                      <Input
                        value={knowledgeForm.tags}
                        onChange={(e) => setKnowledgeForm({ ...knowledgeForm, tags: e.target.value })}
                        placeholder="标签（用逗号分隔）"
                      />
                      <TextArea
                        value={knowledgeForm.content}
                        onChange={(e) => setKnowledgeForm({ ...knowledgeForm, content: e.target.value })}
                        rows={6}
                        placeholder="内容"
                      />
                      <Space>
                        <Button
                          type="primary"
                          loading={knowledgeLoading}
                          onClick={saveKnowledge}
                        >
                          保存条目
                        </Button>
                        <Button onClick={resetKnowledgeForm}>清空</Button>
                      </Space>
                      <Divider />
                      <Text strong>批量导入（JSON 数组）</Text>
                      <TextArea
                        value={batchPayload}
                        onChange={(e) => setBatchPayload(e.target.value)}
                        rows={4}
                        placeholder='例如: [{"title":"FAQ","content":"...","category":"常见问题","tags":["支付"]}]'
                      />
                      <Button
                        type="primary"
                        loading={knowledgeLoading}
                        onClick={batchAddKnowledge}
                      >
                        批量导入
                      </Button>
                    </Space>
                  )
                }
              ]}
            />
          </Card>
        </div>
      </Content>
    </Layout>
  );
};

export default KnowledgeBasePage;
