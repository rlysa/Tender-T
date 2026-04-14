
import React, { useState, useEffect } from 'react';
import { mockApi } from '../services/api';
import { Tender, Scenario } from '../types';

type DateFilterType = 'all' | 'today' | '3days' | 'week';

type CoverageFilterType = 'all' | 'full' | 'partial' | 'zero';

const TenderList: React.FC = () => {
  const [templates, setTemplates] = useState<Scenario[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<number | null>(null);
  const [tenders, setTenders] = useState<Tender[]>([]);
  const [loading, setLoading] = useState(false);
  const [favLoading, setFavLoading] = useState(false);
  const [statusLoading, setStatusLoading] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [coverageFilter, setCoverageFilter] = useState<CoverageFilterType>('all');
  const [dateFilter, setDateFilter] = useState<DateFilterType>('all');

  // State for the detail modal
  const [detailTender, setDetailTender] = useState<Tender | null>(null);

  const loadInitialData = async () => {
    console.log('TenderList: Loading initial data...');
    setLoading(true);
    setError(null);
    try {
      const data = await mockApi.getTemplates();
      console.log('TenderList: Scenarios received:', data);
      setTemplates(data);
      if (data.length > 0) {
        console.log('TenderList: Setting selected scenario to:', data[0].id);
        setSelectedTemplate(data[0].id);
      } else {
        console.warn('TenderList: No scenarios found');
      }
    } catch (err: any) {
      console.error('TenderList: Failed to load scenarios:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    const fetchTenders = async () => {
      if (!selectedTemplate) {
        console.log('TenderList: No scenario selected, skipping fetch');
        return;
      }
      console.log('TenderList: Fetching tenders for scenario:', selectedTemplate);
      setLoading(true);
      setError(null);
      try {
        const data = await mockApi.getTenders(selectedTemplate);
        console.log('TenderList: Tenders received:', data);
        setTenders(data);
      } catch (err: any) {
        console.error('TenderList: Failed to fetch tenders:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchTenders();
  }, [selectedTemplate]);

  const filteredTenders = tenders.filter(t => {
    console.log('TenderList: Filtering tender:', t.id, t.name);
    const matchedItems = t.items?.filter(i => i.is_matched).length || 0;
    const totalItems = t.items?.length || 0;

    let matchesCoverage = true;
    if (coverageFilter === 'full') {
      matchesCoverage = matchedItems === totalItems && totalItems > 0;
    } else if (coverageFilter === 'partial') {
      matchesCoverage = matchedItems > 0 && matchedItems < totalItems;
    } else if (coverageFilter === 'zero') {
      matchesCoverage = matchedItems === 0;
    }

    if (!matchesCoverage) return false;

    if (dateFilter === 'all') return true;
    if (!t.extract_at) return false;

    const extractDate = new Date(t.extract_at);
    const now = new Date();
    const diffTime = now.getTime() - extractDate.getTime();
    const diffDays = diffTime / (1000 * 3600 * 24);

    if (dateFilter === 'today') {
      return extractDate.toDateString() === now.toDateString();
    }
    if (dateFilter === '3days') {
      return diffDays <= 3;
    }
    if (dateFilter === 'week') {
      return diffDays <= 7;
    }

    return true;
  });

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return 'Н/Д';
    const date = new Date(dateStr);
    return date.toLocaleString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatCost = (cost: string | null) => {
    if (!cost || cost === '0' || cost === '0.00' || cost === 'Н/Д') return 'Н/Д';
    // Если знак рубля уже есть, возвращаем как есть, иначе добавляем
    const trimmed = cost.trim();
    return trimmed.endsWith('₽') ? trimmed : `${trimmed} ₽`;
  };

  const handleMarkAsFavorite = async (tenderId: number) => {
    setFavLoading(true);
    try {
      const res = await mockApi.markAsFavorite(tenderId);
      // Mark as viewed as requested
      await mockApi.updateTenderStatus(tenderId, 'favorite');
      setTenders(prev => prev.map(t => t.id === tenderId ? { ...t, status: 'favorite' } : t));
      alert(res.message);
    } catch (err: any) {
      alert(`Ошибка: ${err.message}`);
    } finally {
      setFavLoading(false);
    }
  };

  const handleUpdateStatus = async (tenderId: number, status: string) => {
    setStatusLoading(tenderId);
    try {
      await mockApi.updateTenderStatus(tenderId, status);
      setTenders(prev => prev.map(t => t.id === tenderId ? { ...t, status } : t));
      if (detailTender && detailTender.id === tenderId) {
        setDetailTender({ ...detailTender, status });
      }
    } catch (err: any) {
      alert(`Ошибка при обновлении статуса: ${err.message}`);
    } finally {
      setStatusLoading(null);
    }
  };

  if (error) {
    return (
      <div className="p-8 flex flex-col items-center justify-center h-[70vh] text-center">
        <div className="w-16 h-16 bg-rose-50 rounded-2xl flex items-center justify-center text-rose-500 mb-6">
          <i className="fas fa-wifi-slash text-2xl"></i>
        </div>
        <h3 className="text-xl font-bold text-slate-800 mb-2">Ошибка подключения</h3>
        <p className="text-slate-500 max-w-sm mb-8">{error}</p>
        <button
          onClick={loadInitialData}
          className="bg-indigo-600 text-white px-6 py-2 rounded-xl font-bold hover:bg-indigo-700 transition"
        >
          Повторить попытку
        </button>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="flex flex-col xl:flex-row justify-between items-start xl:items-end mb-10 gap-6">
        <div className="flex-1">
          <h2 className="text-3xl font-black text-slate-800 tracking-tight whitespace-nowrap">Анализ тендеров</h2>
          <div className="flex flex-wrap items-center gap-4 mt-2">
            <select
              value={selectedTemplate || ''}
              onChange={(e) => setSelectedTemplate(Number(e.target.value))}
              disabled={loading || templates.length === 0}
              className="bg-white border border-slate-200 px-4 py-2 rounded-xl text-sm font-bold text-indigo-600 focus:outline-none focus:ring-4 focus:ring-indigo-500/10 shadow-sm disabled:opacity-50"
            >
              {templates.length === 0 ? (
                <option value="">Сценарии не найдены</option>
              ) : (
                templates.map(t => <option key={t.id} value={t.id}>{t.name}</option>)
              )}
            </select>
            <div className="h-6 w-px bg-slate-200 hidden md:block"></div>
            <p className="text-slate-400 text-sm">Найдено записей: {filteredTenders.length}</p>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row gap-4 w-full xl:w-auto">
          <div className="bg-slate-100 p-1.5 rounded-2xl flex gap-1 shadow-inner">
            {(['all', 'today', '3days', 'week'] as const).map(f => (
              <button
                key={f}
                onClick={() => setDateFilter(f)}
                className={`flex-1 sm:flex-none px-4 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${
                  dateFilter === f ? 'bg-white text-indigo-600 shadow-md' : 'text-slate-400 hover:text-slate-600'
                }`}
              >
                {f === 'today' ? 'Сегодня' : f === '3days' ? '3 дня' : f === 'week' ? 'Неделя' : 'Все время'}
              </button>
            ))}
          </div>

          <div className="bg-slate-100 p-1.5 rounded-2xl flex gap-1 shadow-inner">
            {(['all', 'full', 'partial', 'zero'] as const).map(f => (
              <button
                key={f}
                onClick={() => setCoverageFilter(f)}
                className={`flex-1 sm:flex-none px-5 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${
                  coverageFilter === f ? 'bg-white text-indigo-600 shadow-md' : 'text-slate-400 hover:text-slate-600'
                }`}
              >
                {f === 'full' ? 'Полная' : f === 'partial' ? 'Частичная' : f === 'zero' ? 'Нулевая' : 'Все'}
              </button>
            ))}
          </div>
        </div>
      </div>

      {loading ? (
        <div className="py-20 text-center">
           <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600 mx-auto mb-4"></div>
           <p className="text-slate-400 animate-pulse font-medium">Получение данных...</p>
        </div>
      ) : (
        <div className="space-y-6">
          {filteredTenders.map(tender => (
            <div
              key={tender.id}
              onClick={() => setDetailTender(tender)}
              className="bg-white rounded-[32px] border border-slate-200 overflow-hidden shadow-sm hover:shadow-xl hover:border-indigo-300 transition-all group cursor-pointer"
            >
              <div className="p-8">
                <div className="flex justify-between items-start mb-6">
                  <div className="flex-1">
                    <div className="flex flex-wrap items-center gap-3 mb-3">
                      <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest flex items-center gap-1">
                        <i className="far fa-clock"></i> {formatDate(tender.extract_at)}
                      </span>
                      <span className="text-slate-200 hidden sm:inline">/</span>
                      <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">ID {tender.id}</span>
                      {tender.status === 'favorite' && (
                        <span className="text-[10px] font-black bg-slate-100 text-slate-500 uppercase tracking-widest px-2 py-0.5 rounded flex items-center gap-1">
                          <i className="fas fa-eye text-[8px]"></i> В избранном
                        </span>
                      )}
                      {tender.status === 'correct' && (
                        <span className="text-[10px] font-black bg-emerald-50 text-emerald-600 uppercase tracking-widest px-2 py-0.5 rounded flex items-center gap-1">
                          <i className="fas fa-check text-[8px]"></i> Верно
                        </span>
                      )}
                      {tender.status === 'incorrect' && (
                        <span className="text-[10px] font-black bg-rose-50 text-rose-600 uppercase tracking-widest px-2 py-0.5 rounded flex items-center gap-1">
                          <i className="fas fa-times text-[8px]"></i> Неверно
                        </span>
                      )}
                    </div>
                    <h3 className="text-2xl font-black text-slate-800 leading-tight group-hover:text-indigo-600 transition-colors">{tender.name}</h3>
                    <p className="text-slate-500 font-bold mt-2 flex items-center gap-2">
                      <i className="fas fa-building text-slate-300"></i> {tender.customer}
                    </p>
                    
                    <div className="mt-4 flex flex-wrap gap-3">
                      {tender.total_margin !== undefined && (
                        <div className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-2xl shadow-lg shadow-emerald-600/20">
                          <span className="text-[10px] font-black uppercase tracking-widest opacity-80">Прогноз маржи:</span>
                          <span className="text-lg font-black">{tender.total_margin.toLocaleString('ru-RU')} ₽</span>
                        </div>
                      )}
                      <div className="inline-flex items-center gap-2 px-4 py-2 bg-slate-100 text-slate-600 rounded-2xl border border-slate-200">
                        <span className="text-[10px] font-black uppercase tracking-widest opacity-60">Стоимость:</span>
                        <span className="text-lg font-black">{formatCost(tender.cost)}</span>
                      </div>
                    </div>
                  </div>
                  <div className="text-right hidden sm:block shrink-0">
                    <div className="flex flex-col items-end">
                      <span className={`text-[10px] font-black uppercase tracking-widest px-3 py-1 rounded-full mb-2 ${
                        tender.is_match ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'
                      }`}>
                        {tender.is_match ? (
                          tender.items?.every(i => i.is_matched) ? 'Полное покрытие' : 'Частичное покрытие'
                        ) : 'Нет покрытия'}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="p-6 bg-slate-50 rounded-3xl border border-slate-100">
                  <div className="flex justify-between items-center mb-4">
                    <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-[2px]">Сопоставление товаров</h4>
                    <span className="text-[10px] font-black text-indigo-600 uppercase tracking-widest">
                      {tender.items?.filter(i => i.is_matched).length || 0} / {tender.items?.length || 0} позиций
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {tender.items?.slice(0, 3).map(item => (
                      <div key={item.id} className={`px-3 py-1.5 rounded-xl text-xs font-bold flex items-center gap-2 ${
                        item.is_matched ? 'bg-emerald-50 text-emerald-700 border border-emerald-100' : 'bg-slate-100 text-slate-400'
                      }`}>
                        <i className={`fas ${item.is_matched ? 'fa-check-circle' : 'fa-times-circle'}`}></i>
                        {item.name}
                      </div>
                    ))}
                    {(tender.items?.length || 0) > 3 && (
                      <div className="px-3 py-1.5 rounded-xl text-xs font-bold bg-slate-100 text-slate-500">
                        +{ (tender.items?.length || 0) - 3 } еще
                      </div>
                    )}
                  </div>
                </div>
              </div>
              <div className="px-8 py-4 bg-slate-50/50 border-t border-slate-100 flex justify-between items-center">
                 <span className="text-xs text-slate-400 font-medium tracking-tight">Нажмите для просмотра деталей</span>
                 <div className="text-sm font-black text-indigo-600 flex items-center gap-2 group-hover:translate-x-1 transition-transform">
                   Подробнее <i className="fas fa-arrow-right text-[10px]"></i>
                 </div>
              </div>
            </div>
          ))}

          {filteredTenders.length === 0 && !loading && (
            <div className="py-32 text-center bg-white border-2 border-dashed border-slate-200 rounded-[40px]">
              <i className="fas fa-ghost text-slate-200 text-5xl mb-4"></i>
              <h3 className="text-xl font-bold text-slate-400">Тендеры не найдены.</h3>
              <p className="text-slate-400 text-sm mt-1 mb-6">Попробуйте изменить фильтры покрытия или времени.</p>
              {templates.length === 0 && (
                <button 
                  onClick={async () => {
                    const { db } = await import('../services/db');
                    localStorage.clear(); // Clear all to force fresh init
                    db.initIfEmpty();
                    window.location.reload();
                  }}
                  className="bg-indigo-600 text-white px-8 py-3 rounded-2xl font-black shadow-xl shadow-indigo-600/20 hover:bg-indigo-700 transition"
                >
                  Загрузить демо-данные
                </button>
              )}
            </div>
          )}
        </div>
      )}

      {/* Detail Modal */}
      {detailTender && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6 md:p-10">
          <div className="absolute inset-0 bg-slate-900/80 backdrop-blur-md" onClick={() => setDetailTender(null)}></div>
          <div className="bg-white w-full max-w-4xl max-h-[90vh] rounded-[40px] shadow-2xl relative z-10 overflow-hidden flex flex-col animate-in zoom-in duration-300">
            <div className="p-8 border-b border-slate-100 flex justify-between items-start sticky top-0 bg-white z-20">
              <div className="flex-1 pr-8">
                 <div className="flex items-center gap-3 mb-2">
                    <span className={`text-[10px] font-black uppercase tracking-[2px] px-3 py-1 rounded-full ${
                      detailTender.items?.every(i => i.is_matched) ? 'bg-emerald-100 text-emerald-700' : 
                      detailTender.items?.some(i => i.is_matched) ? 'bg-indigo-100 text-indigo-700' : 'bg-rose-100 text-rose-700'
                    }`}>
                      {detailTender.items?.every(i => i.is_matched) ? 'Полное покрытие' : 
                       detailTender.items?.some(i => i.is_matched) ? 'Частичное покрытие' : 'Нет покрытия'}
                    </span>
                    <span className="text-[10px] font-black text-slate-400 uppercase tracking-[2px]">{formatDate(detailTender.extract_at)}</span>
                 </div>
                 <h3 className="text-2xl font-black text-slate-800 leading-tight">{detailTender.name}</h3>
                 <p className="text-slate-500 font-bold mt-2">{detailTender.customer}</p>
              </div>
              <button onClick={() => setDetailTender(null)} className="w-12 h-12 flex items-center justify-center rounded-full bg-slate-50 text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition shrink-0">
                <i className="fas fa-times fa-lg"></i>
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-8 space-y-10 custom-scrollbar">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="bg-slate-50 p-6 rounded-[28px] border border-slate-100">
                  <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-[2px] mb-2">Стоимость</h4>
                  <p className="text-2xl font-black text-slate-900 tracking-tighter">
                    {formatCost(detailTender.cost)}
                  </p>
                </div>
                <div className="bg-emerald-50 p-6 rounded-[28px] border border-emerald-100">
                  <h4 className="text-[10px] font-black text-emerald-400 uppercase tracking-[2px] mb-2">Прогноз маржи</h4>
                  <p className="text-2xl font-black text-emerald-600 tracking-tighter">
                    {detailTender.total_margin ? `+${detailTender.total_margin.toLocaleString('ru-RU')} ₽` : '0 ₽'}
                  </p>
                </div>
                <div className="bg-indigo-50 p-6 rounded-[28px] border border-indigo-100">
                  <h4 className="text-[10px] font-black text-indigo-400 uppercase tracking-[2px] mb-2">Покрытие</h4>
                  <p className="text-2xl font-black text-indigo-600 tracking-tighter">
                    {detailTender.items?.filter(i => i.is_matched).length || 0} / {detailTender.items?.length || 0}
                  </p>
                </div>
              </div>

              <div className="space-y-6">
                 <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-[3px] flex items-center gap-2">
                   <i className="fas fa-boxes text-indigo-500"></i> Сопоставление товаров
                 </h4>
                 <div className="bg-white border border-slate-100 rounded-[32px] overflow-hidden shadow-sm">
                   <table className="w-full border-collapse">
                     <thead>
                       <tr className="bg-slate-50 border-b border-slate-100">
                         <th className="text-left py-4 px-6 text-[10px] font-black text-slate-400 uppercase tracking-widest">Запрашиваемый товар</th>
                         <th className="text-left py-4 px-6 text-[10px] font-black text-slate-400 uppercase tracking-widest">Кол-во</th>
                         <th className="text-left py-4 px-6 text-[10px] font-black text-slate-400 uppercase tracking-widest">Наш артикул</th>
                         <th className="text-right py-4 px-6 text-[10px] font-black text-slate-400 uppercase tracking-widest">Маржа</th>
                       </tr>
                     </thead>
                     <tbody>
                       {detailTender.items?.map(item => (
                         <tr key={item.id} className="border-b border-slate-50 last:border-0 hover:bg-slate-50/50 transition-colors">
                           <td className="py-4 px-6">
                             <div className="font-bold text-slate-800">{item.name}</div>
                           </td>
                           <td className="py-4 px-6">
                             <div className="text-sm text-slate-500 font-medium">{item.quantity} {item.unit}</div>
                           </td>
                           <td className="py-4 px-6">
                             {item.is_matched ? (
                               <span className="px-2 py-1 bg-emerald-50 text-emerald-700 rounded font-mono text-xs font-bold border border-emerald-100">
                                 {item.matched_article}
                               </span>
                             ) : (
                               <span className="text-rose-400 text-xs font-medium italic">Не найдено</span>
                             )}
                           </td>
                           <td className="py-4 px-6 text-right">
                             {item.margin ? (
                               <span className="font-black text-indigo-600">+{item.margin.toLocaleString('ru-RU')} ₽</span>
                             ) : (
                               <span className="text-slate-300">—</span>
                             )}
                           </td>
                         </tr>
                       ))}
                       {!detailTender.items?.length && (
                         <tr>
                           <td colSpan={4} className="py-10 text-center text-slate-400 italic">Товары не распознаны</td>
                         </tr>
                       )}
                     </tbody>
                   </table>
                 </div>
                 
                 {detailTender.total_margin !== undefined && detailTender.total_margin > 0 && (
                   <div className="flex justify-end">
                      <div className="bg-indigo-600 text-white p-6 rounded-[32px] shadow-xl shadow-indigo-600/20 flex items-center gap-6">
                        <div className="text-right">
                          <p className="text-[10px] font-black uppercase tracking-widest opacity-70">Итоговая маржа по тендеру</p>
                          <p className="text-3xl font-black">{detailTender.total_margin.toLocaleString('ru-RU')} ₽</p>
                        </div>
                        <div className="w-12 h-12 bg-white/20 rounded-2xl flex items-center justify-center">
                          <i className="fas fa-calculator text-xl"></i>
                        </div>
                      </div>
                   </div>
                 )}
              </div>
            </div>

            <div className="p-8 border-t border-slate-100 bg-slate-50/30 flex items-center justify-end">
              <div className="flex flex-wrap gap-3 w-full sm:w-auto justify-end items-center">
                <a
                  href={detailTender.url}
                  target="_blank"
                  rel="noreferrer"
                  className="px-6 py-3 bg-indigo-600 text-white rounded-2xl font-bold hover:bg-indigo-700 shadow-xl shadow-indigo-600/20 text-center transition active:scale-95 flex items-center gap-2"
                >
                  Источник <i className="fas fa-external-link-alt text-[10px]"></i>
                </a>
                
                <div className="h-8 w-px bg-slate-200 mx-2 hidden sm:block"></div>

                <button
                  onClick={() => handleUpdateStatus(detailTender.id, 'correct')}
                  disabled={statusLoading === detailTender.id}
                  className={`px-6 py-3 rounded-2xl font-bold transition flex items-center gap-2 ${
                    detailTender.status === 'correct'
                      ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-600/20'
                      : 'bg-emerald-50 text-emerald-600 hover:bg-emerald-100'
                  }`}
                >
                  {statusLoading === detailTender.id ? <i className="fas fa-spinner fa-spin"></i> : <i className="fas fa-check-circle"></i>}
                  Ответ AI корректен
                </button>
                <button
                  onClick={() => handleUpdateStatus(detailTender.id, 'incorrect')}
                  disabled={statusLoading === detailTender.id}
                  className={`px-6 py-3 rounded-2xl font-bold transition flex items-center gap-2 ${
                    detailTender.status === 'incorrect'
                      ? 'bg-rose-600 text-white shadow-lg shadow-rose-600/20'
                      : 'bg-rose-50 text-rose-600 hover:bg-rose-100'
                  }`}
                >
                  {statusLoading === detailTender.id ? <i className="fas fa-spinner fa-spin"></i> : <i className="fas fa-times-circle"></i>}
                  Ответ AI некорректен
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TenderList;
