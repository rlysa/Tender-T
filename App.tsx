
import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import ScenarioManager from './components/ScenarioManager';
import TenderList from './components/TenderList';
import UserProfile from './components/UserProfile';
import AuthScreen from './components/AuthScreen';
import { mockApi } from './services/api';

const App: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(mockApi.isAuthenticated());
  const [activeTab, setActiveTab] = useState('dashboard');
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);
  const [templateCount, setTemplateCount] = useState(0);

  useEffect(() => {
    if (!isAuthenticated) return;

    const checkApi = async () => {
      try {
        const templates = await mockApi.getTemplates();
        setTemplateCount(templates.length);
        setApiOnline(true);
      } catch (e) {
        setApiOnline(false);
      }
    };
    checkApi();
    const interval = setInterval(checkApi, 30000); 
    return () => clearInterval(interval);
  }, [isAuthenticated]);

  const tabNames: Record<string, string> = {
    dashboard: 'Панель управления',
    templates: 'Сценарии',
    tenders: 'Тендеры',
    profile: 'Личный кабинет'
  };

  const handleAuthSuccess = () => {
    setIsAuthenticated(true);
  };

  if (!isAuthenticated) {
    return <AuthScreen onAuthSuccess={handleAuthSuccess} />;
  }

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard': return <Dashboard />;
      case 'templates': return <ScenarioManager />;
      case 'tenders': return <TenderList />;
      case 'profile': return <UserProfile />;
      default: return <Dashboard />;
    }
  };

  return (
    <div className="min-h-screen flex bg-slate-50">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} templateCount={templateCount} />
      <main className="flex-1 ml-72 min-h-screen transition-all duration-300">
        {renderContent()}
      </main>
    </div>
  );
};

export default App;
