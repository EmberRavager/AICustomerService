import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Layout } from 'antd';
import './App.css';
import ChatPage from './pages/ChatPage';
import SettingsPage from './pages/SettingsPage';
import Header from './components/Header';
import Footer from './components/Footer';

/**
 * 应用程序主组件
 * 定义应用的整体布局和路由配置
 */

const { Content } = Layout;

const App: React.FC = () => {
  return (
    <Layout className="app-layout">
      {/* 头部组件 */}
      <Header />
      
      {/* 主要内容区域 */}
      <Content className="app-content">
        <Routes>
          {/* 聊天页面路由 */}
          <Route path="/" element={<ChatPage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/chat/:sessionId" element={<ChatPage />} />
          {/* 设置页面路由 */}
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </Content>
      
      {/* 底部组件 */}
      <Footer />
    </Layout>
  );
};

export default App;