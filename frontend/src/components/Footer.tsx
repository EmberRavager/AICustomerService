import React from 'react';
import { Layout, Typography, Space, Divider } from 'antd';
import { HeartFilled, GithubOutlined, MailOutlined } from '@ant-design/icons';
import './Footer.css';

/**
 * 底部组件
 * 显示版权信息、联系方式和相关链接
 */

const { Footer: AntFooter } = Layout;
const { Text, Link } = Typography;

const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <AntFooter className="app-footer">
      <div className="footer-content">
        {/* 主要信息区域 */}
        <div className="footer-main">
          <Space split={<Divider type="vertical" />} size="large" className="footer-links">
            {/* 版权信息 */}
            <Text className="footer-text">
              © {currentYear} 智能客服系统
            </Text>
            
            {/* 技术栈信息 */}
            <Text className="footer-text">
              基于 React + LangChain 构建
            </Text>
            
            {/* 联系邮箱 */}
            <Link 
              href="mailto:support@example.com" 
              className="footer-link"
              target="_blank"
            >
              <MailOutlined /> 联系我们
            </Link>
            
            {/* GitHub链接 */}
            <Link 
              href="https://github.com" 
              className="footer-link"
              target="_blank"
              rel="noopener noreferrer"
            >
              <GithubOutlined /> GitHub
            </Link>
          </Space>
        </div>
        
        {/* 底部信息 */}
        <div className="footer-bottom">
          <Text className="footer-love">
            Made with <HeartFilled className="heart-icon" /> by AI Assistant
          </Text>
        </div>
      </div>
    </AntFooter>
  );
};

export default Footer;