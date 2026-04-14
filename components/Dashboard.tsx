
import React, { useState, useEffect } from 'react';
import { mockApi } from '../services/api';
import { PipelineStatus } from '../types';

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<{
    summary: {
      active_templates: number;
      total_tenders: number;
      relevant_matches: number;
      total_margin: number;
      ai_summaries: number;
    };
    templates: any[];
    run_history: any[];
  }>({
    summary: {
      active_templates: 0,
      total_tenders: 0,
      relevant_matches: 0,
      total_margin: 0,
      ai_summaries: 0
    },
    templates: [],
    run_history: []
  });
  const [isConnected, setIsConnected] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      try {
        const data = await mockApi.getStats();
        setStats(data);
        setIsConnected(true);
      } catch (err) {
        setIsConnected(false);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 60000);
    return () => clearInterval(interval);
  }, []);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case PipelineStatus.CREATED:
        return <span className="px-2.5 py-1 bg-amber-100 text-amber-700 rounded-md text-[11px] font-bold uppercase tracking-wider">Создан</span>;
      case PipelineStatus.STARTED:
        return <span className="px-2.5 py-1 bg-blue-100 text-blue-700 rounded-md text-[11px] font-bold uppercase tracking-wider">Запущен</span>;
      case PipelineStatus.SEARCHING:
        return <span className="px-2.5 py-1 bg-emerald-100 text-emerald-700 rounded-md text-[11px] font-bold uppercase tracking-wider">Поиск</span>;
      case PipelineStatus.PROCESSING:
        return <span className="px-2.5 py-1 bg-indigo-100 text-indigo-700 rounded-md text-[11px] font-bold uppercase tracking-wider">Обработка</span>;
      case PipelineStatus.FINISHED:
        return <span className="px-2.5 py-1 bg-emerald-100 text-emerald-700 rounded-md text-[11px] font-bold uppercase tracking-wider">Завершен</span>;
      case PipelineStatus.ERROR:
        return <span className="px-2.5 py-1 bg-rose-100 text-rose-700 rounded-md text-[11px] font-bold uppercase tracking-wider">Ошибка</span>;
      default:
        return <span className="px-2.5 py-1 bg-slate-100 text-slate-700 rounded-md text-[11px] font-bold uppercase tracking-wider">Ожидание</span>;
    }
  };

  const formatDuration = (start: string, end: string) => {
    const durationMs = new Date(end).getTime() - new Date(start).getTime();
    const minutes = Math.floor(durationMs / 60000);
    const seconds = Math.floor((durationMs % 60000) / 1000);
    return `${minutes}м ${seconds}с`;
  };

  return (
    <div className="p-8 pb-20">
      <div className="mb-10 flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-black text-slate-800 tracking-tight">Панель управления</h2>
          <p className="text-slate-400 text-sm mt-1">Мониторинг активности и эффективности шаблонов</p>
        </div>
        {!isConnected && isConnected !== null && (
          <div className="bg-rose-50 text-rose-600 px-4 py-2 rounded-xl flex items-center gap-2 text-sm font-bold animate-pulse border border-rose-100 shadow-sm">
             <i className="fas fa-exclamation-triangle"></i>
             API недоступно
          </div>
        )}
        {loading && stats.templates.length === 0 && (
          <div className="flex items-center gap-2 text-indigo-600 text-sm font-bold">
            <i className="fas fa-spinner fa-spin"></i> Расчет статистики...
          </div>
        )}
      </div>

      <div className="bg-white rounded-[32px] border border-slate-200 shadow-sm overflow-hidden mb-12">
        <div className="p-8 border-b border-slate-100 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <h3 className="text-xl font-black text-slate-800 tracking-tight">Статус шаблонов</h3>
            <button
              onClick={() => {
                const fetchDashboardData = async () => {
                  setLoading(true);
                  try {
                    const data = await mockApi.getStats();
                    setStats(data);
                    setIsConnected(true);
                  } catch (err) {
                    setIsConnected(false);
                  } finally {
                    setLoading(false);
                  }
                };
                fetchDashboardData();
              }}
              disabled={loading}
              className="w-8 h-8 flex items-center justify-center rounded-full bg-slate-50 text-slate-400 hover:bg-indigo-50 hover:text-indigo-600 transition-all active:rotate-180 duration-500 disabled:opacity-50"
              title="Обновить данные"
            >
              <i className={`fas fa-sync-alt text-xs ${loading ? 'fa-spin' : ''}`}></i>
            </button>
          </div>
          <div className="flex gap-4">
             <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-emerald-500"></div>
                <span className="text-[10px] font-bold uppercase text-slate-400">Релевантно</span>
             </div>
             <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-slate-300"></div>
                <span className="text-[10px] font-bold uppercase text-slate-400">Всего</span>
             </div>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse table-fixed">
            <thead>
              <tr className="bg-slate-50/50">
                <th className="w-[25%] px-8 py-5 text-[11px] font-black uppercase tracking-widest text-slate-400">Шаблон</th>
                <th className="w-[15%] px-6 py-5 text-[11px] font-black uppercase tracking-widest text-slate-400">Статус</th>
                <th className="w-[15%] px-6 py-5 text-[11px] font-black uppercase tracking-widest text-slate-400">Прогресс</th>
                <th className="w-[15%] px-6 py-5 text-[11px] font-black uppercase tracking-widest text-slate-400 whitespace-nowrap">Стоимость</th>
                <th className="w-[15%] px-8 py-5 text-[11px] font-black uppercase tracking-widest text-slate-400 whitespace-nowrap">Общая стоимость</th>
                <th className="w-[15%] px-8 py-5"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {stats?.templates?.map((template) => (
                <tr key={template.id} className="hover:bg-slate-50/50 transition-colors group">
                  <td className="px-8 py-6">
                    <div className="text-[15px] font-bold text-slate-800 group-hover:text-indigo-600 transition-colors truncate">{template.name}</div>
                    <div className="text-[11px] text-slate-400 mt-1 font-mono truncate">{template.url}</div>
                  </td>
                  <td className="px-6 py-6 align-middle">
                    {getStatusBadge(template.status)}
                  </td>
                  <td className="px-6 py-6 align-middle">
                    <div className="flex flex-col items-start gap-2">
                       <div className="text-[15px] font-black text-slate-700">
                          {template.processed} <span className="text-slate-300 font-normal mx-0.5">/</span> {template.found}
                       </div>
                       <div className="w-full max-w-[100px] h-1.5 bg-slate-100 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-indigo-500 transition-all duration-500"
                            style={{ width: `${template.found > 0 ? (template.processed / template.found) * 100 : 0}%` }}
                          ></div>
                       </div>
                    </div>
                  </td>
                  <td className="px-6 py-6 align-middle">
                    <div className="text-[15px] font-bold text-slate-800">{template.last_run_cost?.toFixed(2) || '0.00'} ₽</div>
                  </td>
                  <td className="px-8 py-6 align-middle">
                    <div className="text-[15px] font-bold text-indigo-600">{template.total_run_cost?.toFixed(2) || '0.00'} ₽</div>
                  </td>
                </tr>
              ))}
              {stats.templates.length === 0 && !loading && (
                <tr>
                  <td colSpan={6} className="px-8 py-12 text-center text-slate-400 italic">
                    Шаблоны не найдены
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div className="bg-white rounded-[32px] border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-8 border-b border-slate-100">
          <h3 className="text-xl font-black text-slate-800 tracking-tight">История прогонов</h3>
          <p className="text-slate-400 text-[10px] font-bold uppercase tracking-widest mt-1">Последние запуски системы</p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse table-fixed">
            <thead>
              <tr className="bg-slate-50/50">
                <th className="w-[25%] px-8 py-5 text-[11px] font-black uppercase tracking-widest text-slate-400">Шаблон</th>
                <th className="w-[15%] px-6 py-5 text-[11px] font-black uppercase tracking-widest text-slate-400">Дата и время</th>
                <th className="w-[15%] px-6 py-5 text-[11px] font-black uppercase tracking-widest text-slate-400">Найдено</th>
                <th className="w-[15%] px-6 py-5 text-[11px] font-black uppercase tracking-widest text-slate-400">Стоимость</th>
                <th className="w-[15%] px-8 py-5"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {stats?.run_history?.map((run) => (
                <tr key={run.id} className="hover:bg-slate-50/50 transition-colors">
                  <td className="px-8 py-6 align-middle">
                    <div className="text-[15px] font-medium text-slate-800 truncate">{run.template_name}</div>
                  </td>
                  <td className="px-6 py-6 align-middle">
                    <div className="text-[15px] font-bold text-slate-800">
                      {run.start_at ? new Date(run.start_at).toLocaleDateString('ru-RU') : '—'}
                      <span className="ml-2 text-[15px] font-bold text-slate-800">
                        {run.start_at ? new Date(run.start_at).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' }) : '--:--'}
                      </span>
                    </div>
                    <div className="flex items-center gap-1.5 mt-1">
                      <i className="far fa-clock text-[11px] text-slate-400"></i>
                      <div className="text-[13px] text-slate-400 font-medium">
                        {formatDuration(run.start_at, run.end_at)}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-6 align-middle">
                    <span className="text-[15px] font-bold text-slate-700">{run.found}</span>
                  </td>
                  <td className="px-6 py-6 align-middle">
                    <div className="text-[15px] font-black text-slate-800">{typeof run.cost === 'number' ? run.cost.toFixed(2) : '0.00'} ₽</div>
                  </td>
                  <td className="px-8 py-6"></td>
                </tr>
              ))}
              {stats.run_history.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-8 py-10 text-center text-slate-400 italic">
                    История пуста
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
