import React, { useState, useEffect } from 'react';
import {
  Card,
  Select,
  Button,
  Tag,
  Alert,
  Modal,
  Spin,
  Space,
  Typography,
  Tooltip,
  message,
  Row,
  Col
} from 'antd';
import {
  SettingOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  ThunderboltOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import { modelAPI } from '../services/api';

const { Title, Text } = Typography;
const { Option } = Select;

/**
 * 模型配置接口
 */
interface ModelConfig {
  provider: string;
  model: string;
  api_base: string;
  is_configured: boolean;
  is_current: boolean;
}

/**
 * 测试结果接口
 */
interface TestResult {
  provider: string;
  success: boolean;
  response?: string;
  error?: string;
  latency_ms?: number;
}

/**
 * 模型选择器组件属性
 */
interface ModelSelectorProps {
  onModelChange?: (provider: string, model: string) => void;
}

/**
 * 模型选择器组件
 * 提供模型切换和管理功能
 */
const ModelSelector: React.FC<ModelSelectorProps> = ({ onModelChange }) => {
  const [models, setModels] = useState<ModelConfig[]>([]);
  const [currentModel, setCurrentModel] = useState<ModelConfig | null>(null);
  const [selectedProvider, setSelectedProvider] = useState<string>('');
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [testLoading, setTestLoading] = useState<boolean>(false);
  const [testResult, setTestResult] = useState<TestResult | null>(null);
  const [testModalVisible, setTestModalVisible] = useState<boolean>(false);

  // 提供商显示名称映射
  const providerNames: Record<string, string> = {
    openai: 'OpenAI',
    gemini: 'Google Gemini',
    deepseek: 'DeepSeek',
    zhipu: '智谱AI',
    baichuan: '百川智能',
    qwen: '通义千问',
    moonshot: '月之暗面',
    yi: '零一万物'
  };

  /**
   * 加载模型列表
   */
  const loadModels = async () => {
    try {
      setLoading(true);
      const [modelList, current] = await Promise.all([
        modelAPI.listModels(),
        modelAPI.getCurrentModel()
      ]);
      setModels(modelList);
      setCurrentModel(current);
      setSelectedProvider(current.provider);
      
      // 加载当前提供商的可用模型
      if (current.provider) {
        await loadProviderModels(current.provider);
        setSelectedModel(current.config.model);
      }
    } catch (err: any) {
      message.error('加载模型列表失败: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  /**
   * 加载提供商的可用模型
   */
  const loadProviderModels = async (provider: string) => {
    try {
      const providerModels = await modelAPI.getProviderModels(provider);
      setAvailableModels(providerModels.models);
      // 设置默认模型
      const defaultModel = models.find(m => m.provider === provider)?.model;
      setSelectedModel(defaultModel || providerModels.models[0]);
    } catch (err: any) {
      console.error('加载提供商模型失败:', err);
      setAvailableModels([]);
    }
  };

  /**
   * 切换模型提供商
   */
  const handleProviderChange = async (provider: string) => {
    setSelectedProvider(provider);
    await loadProviderModels(provider);
  };

  /**
   * 切换模型
   */
  const handleSwitchModel = async () => {
    try {
      setLoading(true);
      
      await modelAPI.switchModel({
        provider: selectedProvider,
        model: selectedModel
      });
      
      message.success(`成功切换到 ${providerNames[selectedProvider]} - ${selectedModel}`);
      await loadModels(); // 重新加载当前配置
      
      // 通知父组件模型已更改
      if (onModelChange) {
        onModelChange(selectedProvider, selectedModel);
      }
      
    } catch (err: any) {
      message.error('切换模型失败: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  /**
   * 测试模型
   */
  const handleTestModel = async (provider: string) => {
    try {
      setTestLoading(true);
      const result = await modelAPI.testModel({
        provider,
        test_message: '你好，请简单介绍一下自己。'
      });
      setTestResult({ provider, ...result });
      setTestModalVisible(true);
    } catch (err: any) {
      setTestResult({
        provider,
        success: false,
        error: err.message
      });
      setTestModalVisible(true);
    } finally {
      setTestLoading(false);
    }
  };

  useEffect(() => {
    loadModels();
  }, []);

  return (
    <Card
      title={
        <Space>
          <SettingOutlined />
          <span>模型配置</span>
          <Tooltip title="刷新模型列表">
            <Button
              type="text"
              icon={<ReloadOutlined />}
              onClick={loadModels}
              loading={loading}
              size="small"
            />
          </Tooltip>
        </Space>
      }
      size="small"
    >
      {/* 当前模型显示 */}
      {currentModel && (
        <div style={{ marginBottom: 16 }}>
          <Text type="secondary">当前模型:</Text>
          <div style={{ marginTop: 4 }}>
            <Tag
              color="blue"
              icon={<CheckCircleOutlined />}
            >
              {`${providerNames[currentModel.provider]} - ${currentModel.model}`}
            </Tag>
            <Text type="secondary" style={{ fontSize: 12 }}>
              {currentModel.api_base}
            </Text>
          </div>
        </div>
      )}

      {/* 模型切换 */}
      <Row gutter={8} align="middle">
        <Col span={8}>
          <Select
            value={selectedProvider}
            onChange={handleProviderChange}
            disabled={loading}
            size="small"
            style={{ width: '100%' }}
            placeholder="选择提供商"
          >
            {models.map((model) => (
              <Option key={model.provider} value={model.provider}>
                <Space>
                  <span>{providerNames[model.provider]}</span>
                  {model.is_configured ? (
                    <CheckCircleOutlined style={{ color: '#52c41a' }} />
                  ) : (
                    <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />
                  )}
                </Space>
              </Option>
            ))}
          </Select>
        </Col>

        <Col span={8}>
          <Select
            value={selectedModel}
            onChange={setSelectedModel}
            disabled={loading || !selectedProvider}
            size="small"
            style={{ width: '100%' }}
            placeholder="选择模型"
          >
            {availableModels.map((model) => (
              <Option key={model} value={model}>
                {model}
              </Option>
            ))}
          </Select>
        </Col>

        <Col span={8}>
          <Space size={4}>
            <Button
              type="primary"
              onClick={handleSwitchModel}
              disabled={loading || !selectedProvider || !selectedModel}
              size="small"
              loading={loading}
            >
              切换
            </Button>
            <Button
              onClick={() => handleTestModel(selectedProvider)}
              disabled={testLoading || !selectedProvider}
              size="small"
              loading={testLoading}
              icon={<ThunderboltOutlined />}
            >
              测试
            </Button>
          </Space>
        </Col>
      </Row>

      {/* 模型列表 */}
      <div style={{ marginTop: 16 }}>
        <Text type="secondary" style={{ fontSize: 12 }}>所有模型:</Text>
        <div style={{ marginTop: 4 }}>
          <Space size={[4, 4]} wrap>
            {models.map((model) => (
              <Tooltip
                key={model.provider}
                title={`${model.api_base} - ${model.is_configured ? '已配置' : '未配置'}`}
              >
                <Tag
                  color={model.is_current ? 'blue' : model.is_configured ? 'default' : 'red'}
                  style={{
                    cursor: model.is_configured ? 'pointer' : 'default',
                    opacity: model.is_configured ? 1 : 0.6
                  }}
                  onClick={() => {
                    if (model.is_configured) {
                      setSelectedProvider(model.provider);
                      loadProviderModels(model.provider);
                    }
                  }}
                >
                  {`${providerNames[model.provider]} (${model.model})`}
                </Tag>
              </Tooltip>
            ))}
          </Space>
        </div>
      </div>

      {/* 测试结果对话框 */}
      <Modal
        title={testResult && `${providerNames[testResult.provider]} 测试结果`}
        open={testModalVisible}
        onCancel={() => setTestModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setTestModalVisible(false)}>
            关闭
          </Button>
        ]}
        width={600}
      >
        {testResult && (
          <div>
            {testResult.success ? (
              <div>
                <Alert
                  message="模型响应正常"
                  description={testResult.latency_ms && `延迟: ${testResult.latency_ms}ms`}
                  type="success"
                  style={{ marginBottom: 16 }}
                />
                <div>
                  <Text strong>模型回复:</Text>
                  <div
                    style={{
                      marginTop: 8,
                      padding: 12,
                      backgroundColor: '#f5f5f5',
                      borderRadius: 4,
                      fontFamily: 'monospace',
                      whiteSpace: 'pre-wrap'
                    }}
                  >
                    {testResult.response}
                  </div>
                </div>
              </div>
            ) : (
              <Alert
                message="测试失败"
                description={testResult.error}
                type="error"
              />
            )}
          </div>
        )}
      </Modal>
    </Card>
  );
};

export default ModelSelector;