import React from 'react';
import { Layout, Menu } from 'antd';
import {
  HomeOutlined,
  RobotOutlined,
  MessageOutlined,
  BookOutlined,
  ApartmentOutlined,
  SettingOutlined,
  AppstoreOutlined,
  ToolOutlined
} from '@ant-design/icons';
import { useLocation, useNavigate } from 'react-router-dom';
import './SideNav.css';

const { Sider } = Layout;

const SideNav: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const items = [
    { key: '/overview', icon: <HomeOutlined />, label: '概览' },
    { key: '/robots', icon: <RobotOutlined />, label: '机器人管理' },
    { key: '/chat', icon: <MessageOutlined />, label: '测试聊天' },
    { key: '/knowledge', icon: <BookOutlined />, label: '知识库' },
    { key: '/policies', icon: <ApartmentOutlined />, label: '策略配置' },
    { key: '/models', icon: <AppstoreOutlined />, label: '模型管理' },
    { key: '/chat-settings', icon: <SettingOutlined />, label: '聊天设置' },
    { key: '/ops', icon: <ToolOutlined />, label: '运维工具' }
  ];

  const selectedKey = items.find(item => location.pathname.startsWith(item.key))?.key || '/overview';

  return (
    <Sider width={220} className="app-sider">
      <div className="sider-brand">
        <div className="brand-dot" />
        <span>客服机器人</span>
      </div>
      <Menu
        mode="inline"
        selectedKeys={[selectedKey]}
        items={items}
        onClick={(info) => navigate(info.key)}
        className="sider-menu"
      />
    </Sider>
  );
};

export default SideNav;
