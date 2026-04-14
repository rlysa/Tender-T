
import React from 'react';
import { mockApi } from '../services/api';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  templateCount: number;
}

const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab, templateCount }) => {
  const menuItems = [
    { id: 'dashboard', icon: 'fa-chart-pie', label: 'Панель управления' },
    { id: 'templates', icon: 'fa-layer-group', label: 'Сценарии' },
    { id: 'tenders', icon: 'fa-file-invoice-dollar', label: 'Тендеры' },
    { id: 'profile', icon: 'fa-user-circle', label: 'Личный кабинет' }
  ];

  const getNextRunTime = () => {
    const now = new Date();
    const currentHour = now.getHours();
    
    if (currentHour < 12) {
      return "12:00";
    } else if (currentHour < 18) {
      return "18:00";
    } else {
      return "12:00"; 
    }
  };

  const getTemplateWord = (count: number) => {
    const lastDigit = count % 10;
    const lastTwoDigits = count % 100;
    if (lastTwoDigits >= 11 && lastTwoDigits <= 19) return 'сценариям';
    if (lastDigit === 1) return 'сценарию';
    if (lastDigit >= 2 && lastDigit <= 4) return 'сценариям';
    return 'сценариям';
  };

  const handleLogout = () => {
    if (window.confirm('Вы действительно хотите выйти?')) {
      mockApi.logout();
    }
  };

  return (
    <div className="w-72 bg-slate-900 h-screen text-slate-300 flex flex-col fixed left-0 top-0 z-50 shadow-2xl">
      <div className="p-6 flex items-center gap-3 border-b border-slate-800 shrink-0">
        <div className="w-10 h-10 bg-indigo-600 rounded-lg flex items-center justify-center text-white shadow-lg shadow-indigo-500/20">
          <i className="fas fa-radar fa-lg"></i>
        </div>
        <div className="overflow-hidden">
          <h1 className="text-white font-bold text-lg leading-none truncate">TenderAI</h1>
          <span className="text-[10px] text-indigo-400 font-black tracking-wider uppercase whitespace-nowrap">AI Мониторинг</span>
        </div>
      </div>
      
      <nav className="flex-1 py-6 px-4 space-y-2 overflow-y-auto custom-scrollbar">
        {menuItems.map(item => (
          <button
            key={item.id}
            onClick={() => setActiveTab(item.id)}
            className={`w-full flex items-center gap-4 px-4 py-3 rounded-xl transition-all duration-200 group ${
              activeTab === item.id 
                ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/20' 
                : 'hover:bg-slate-800 hover:text-white'
            }`}
          >
            <div className={`flex items-center justify-center w-8 transition-colors ${activeTab === item.id ? 'text-white' : 'text-slate-500 group-hover:text-indigo-400'}`}>
              <i className={`fas ${item.icon} text-lg`}></i>
            </div>
            <span className="font-semibold text-sm whitespace-nowrap">{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="mt-auto p-4 space-y-4">
        <div className="p-5 bg-slate-800/40 rounded-2xl border border-slate-700/30">
          <div className="flex items-center gap-3 mb-3">
            <div className="relative flex">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <div className="w-2 h-2 bg-green-500 rounded-full absolute animate-ping"></div>
            </div>
            <span className="text-[10px] font-black text-slate-400 uppercase tracking-[1.5px] whitespace-nowrap">
              Запуск: {getNextRunTime()}
            </span>
          </div>
          <div className="space-y-1">
            <p className="text-[11px] text-slate-300 font-medium leading-relaxed">
              Система активна.
            </p>
            <p className="text-[11px] text-slate-500 leading-tight">
              Мониторинг по {templateCount} {getTemplateWord(templateCount)}.
            </p>
          </div>
        </div>

        <button 
          onClick={handleLogout}
          className="w-full flex items-center gap-4 px-4 py-3 rounded-xl text-slate-500 hover:bg-rose-500/10 hover:text-rose-500 transition-all font-bold text-sm"
        >
          <div className="flex items-center justify-center w-8">
            <i className="fas fa-sign-out-alt"></i>
          </div>
          Выйти из аккаунта
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
