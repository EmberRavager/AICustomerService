import React from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';
import { Layout } from 'antd';
import './App.css';
import ChatPage from './pages/ChatPage';
import WidgetPage from './pages/WidgetPage';
import PublicChatPage from './pages/PublicChatPage';
import OverviewPage from './pages/OverviewPage';
import RobotsPage from './pages/RobotsPage';
import KnowledgeBasePage from './pages/KnowledgeBasePage';
import PoliciesPage from './pages/PoliciesPage';
import ModelsPage from './pages/ModelsPage';
import ChatSettingsPage from './pages/ChatSettingsPage';
import OpsPage from './pages/OpsPage';
import Header from './components/Header';
import Footer from './components/Footer';
import SideNav from './components/SideNav';

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
      <Layout className="app-shell">
        <SideNav />
        <Content className="app-content">
          <Routes>
            <Route path="/" element={<OverviewPage />} />
            <Route path="/overview" element={<OverviewPage />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/chat/:sessionId" element={<ChatPage />} />
            <Route path="/robots" element={<RobotsPage />} />
            <Route path="/knowledge" element={<KnowledgeBasePage />} />
            <Route path="/policies" element={<PoliciesPage />} />
            <Route path="/models" element={<ModelsPage />} />
            <Route path="/chat-settings" element={<ChatSettingsPage />} />
            <Route path="/ops" element={<OpsPage />} />
            <Route path="/settings" element={<OverviewPage />} />
          </Routes>
        </Content>
      </Layout>
      <Footer />
    </Layout>
  );
};

export default App;
