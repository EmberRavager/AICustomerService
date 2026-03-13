import React from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';
import { Layout } from 'antd';
import './App.css';
import ChatPage from './pages/ChatPage';
import WidgetPage from './pages/WidgetPage';
import PublicChatPage from './pages/PublicChatPage';
import SettingsPage from './pages/SettingsPage';
import Header from './components/Header';
import Footer from './components/Footer';

/**
 * 应用程序主组件
 * 定义应用的整体布局和路由配置
 */

const { Content } = Layout;

const App: React.FC = () => {
  const location = useLocation();
  const isPublic = location.pathname.startsWith('/widget') || location.pathname.startsWith('/support');

  if (isPublic) {
    return (
      <Routes>
        <Route path="/support" element={<PublicChatPage />} />
        <Route path="/widget" element={<WidgetPage />} />
      </Routes>
    );
  }

  return (
    <Layout className="app-layout">
      <Header />
      <Content className="app-content">
        <Routes>
          <Route path="/" element={<ChatPage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/chat/:sessionId" element={<ChatPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </Content>
      <Footer />
    </Layout>
  );
};

export default App;
