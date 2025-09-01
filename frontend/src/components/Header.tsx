import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Layout, Typography, Space, Button } from 'antd';
import { MessageOutlined, SettingOutlined, QuestionCircleOutlined, HomeOutlined } from '@ant-design/icons';
import './Header.css';

/**
 * 头部组件
 * 显示应用标题、导航和操作按钮
 */

const { Header: AntHeader } = Layout;
const { Title } = Typography;

interface HeaderProps {
  onHelpClick?: () => void;
}

const Header: React.FC<HeaderProps> = ({ 
  onHelpClick 
}) => {
  const location = useLocation();

  /**
   * 处理帮助按钮点击
   */
  const handleHelpClick = () => {
    if (onHelpClick) {
      onHelpClick();
    } else {
      console.log('帮助功能待实现');
    }
  };

  return (
    <AntHeader className="app-header">
      <div className="header-content">
        {/* 左侧：应用标题和图标 */}
        <div className="header-left">
          <Space size="middle">
            <MessageOutlined className="header-icon" />
            <Title level={3} className="header-title">
              智能客服系统
            </Title>
          </Space>
        </div>

        {/* 右侧：操作按钮 */}
        <div className="header-right">
          <Space size="small">
            {/* 首页按钮 */}
            <Link to="/">
              <Button
                type={location.pathname === '/' || location.pathname.startsWith('/chat') ? 'primary' : 'text'}
                icon={<HomeOutlined />}
                className="header-button"
                title="聊天"
              >
                <span className="desktop-only">聊天</span>
              </Button>
            </Link>

            {/* 设置按钮 */}
            <Link to="/settings">
              <Button
                type={location.pathname === '/settings' ? 'primary' : 'text'}
                icon={<SettingOutlined />}
                className="header-button"
                title="设置"
              >
                <span className="desktop-only">设置</span>
              </Button>
            </Link>

            {/* 帮助按钮 */}
            <Button
              type="text"
              icon={<QuestionCircleOutlined />}
              className="header-button"
              onClick={handleHelpClick}
              title="帮助"
            >
              <span className="desktop-only">帮助</span>
            </Button>
          </Space>
        </div>
      </div>
    </AntHeader>
  );
};

export default Header;