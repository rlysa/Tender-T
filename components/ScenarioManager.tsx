
import React, { useState, useEffect } from 'react';
import { mockApi } from '../services/api';
import { Scenario, ScenarioItem } from '../types';

const ScenarioManager: React.FC = () => {
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isItemsModalOpen, setIsItemsModalOpen] = useState(false);
  const [selectedScenario, setSelectedScenario] = useState<Scenario | null>(null);
  const [scenarioItems, setScenarioItems] = useState<ScenarioItem[]>([]);
  const [itemsLoading, setItemsLoading] = useState(false);

  const [actionLoading, setActionLoading] = useState<number | null>(null);
  const [runAllLoading, setRunAllLoading] = useState(false);
  const [uploadLoading, setUploadLoading] = useState(false);
  
  const [editingScenario, setEditingScenario] = useState<Scenario | null>(null);
  const [formData, setFormData] = useState({ name: '', search_words: '' });
  const [newWord, setNewWord] = useState('');

  const loadData = async (showGlobalLoader = false) => {
    if (showGlobalLoader) setLoading(true);
    setError(null);
    try {
      const data = await mockApi.getTemplates();
      setScenarios(data || []);
    } catch (err) {
      setError("Не удается подключиться к серверу");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData(true);
  }, []);

  const handleRun = async (id: number) => {
    setActionLoading(id);
    try {
      await mockApi.runPipeline(id);
      alert('Сбор тендеров запущен в фоновом режиме.');
    } catch (e) {
      alert(e instanceof Error ? e.message : 'Ошибка при запуске сбора');
    } finally {
      setActionLoading(null);
    }
  };

  const handleRunAll = async () => {
    if (scenarios.length === 0) return;
    setRunAllLoading(true);
    try {
      await mockApi.runAllPipelines();
      alert('Запущен процесс сканирования по всем активным сценариям.');
    } catch (e) {
      alert('Ошибка при запуске общего сбора');
    } finally {
      setRunAllLoading(false);
    }
  };

  const handleDelete = async (e: React.MouseEvent, id: number) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (window.confirm('Вы уверены, что хотите удалить этот сценарий из базы данных?')) {
      setActionLoading(id);
      try {
        await mockApi.deleteTemplate(id);
        setScenarios(prev => prev.filter(t => t.id !== id));
      } catch (err: any) {
        alert(`Ошибка удаления: ${err.message}`);
      } finally {
        setActionLoading(null);
      }
    }
  };

  const handleOpenEdit = (e: React.MouseEvent, scenario: Scenario) => {
    e.preventDefault();
    e.stopPropagation();
    setEditingScenario(scenario);
    setFormData({ name: scenario.name, search_words: scenario.search_words || '' });
    setIsModalOpen(true);
  };

  const addWord = () => {
    if (!newWord.trim()) return;
    const words = formData.search_words ? formData.search_words.split(',').map(w => w.trim()) : [];
    if (!words.includes(newWord.trim())) {
      const updatedWords = [...words, newWord.trim()].join(', ');
      setFormData({ ...formData, search_words: updatedWords });
    }
    setNewWord('');
  };

  const removeWord = (wordToRemove: string) => {
    const words = formData.search_words.split(',').map(w => w.trim());
    const updatedWords = words.filter(w => w !== wordToRemove).join(', ');
    setFormData({ ...formData, search_words: updatedWords });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await mockApi.saveTemplate({
        id: editingScenario?.id,
        name: formData.name,
        search_words: formData.search_words,
        user_id: editingScenario?.user_id || 1
      });
      setIsModalOpen(false);
      await loadData();
    } catch (err: any) {
      alert(`Ошибка при сохранении: ${err.message}`);
    }
  };

  const handleFileUpload = async (scenarioId: number, file: File) => {
    setUploadLoading(true);
    try {
      await mockApi.uploadExcel(scenarioId, file);
      alert('Файл успешно загружен и обрабатывается.');
      if (selectedScenario?.id === scenarioId) {
        loadScenarioItems(scenarioId);
      }
    } catch (err: any) {
      alert(`Ошибка загрузки: ${err.message}`);
    } finally {
      setUploadLoading(false);
    }
  };

  const loadScenarioItems = async (scenarioId: number) => {
    setItemsLoading(true);
    try {
      const items = await mockApi.getScenarioItems(scenarioId);
      setScenarioItems(items);
    } catch (err: any) {
      console.error('Failed to load items', err);
    } finally {
      setItemsLoading(false);
    }
  };

  const handleOpenItems = (scenario: Scenario) => {
    setSelectedScenario(scenario);
    loadScenarioItems(scenario.id);
    setIsItemsModalOpen(true);
  };

  const handleUpdateItem = async (item: ScenarioItem, field: keyof ScenarioItem, value: string | number) => {
    const updatedItem = { ...item, [field]: value };
    try {
      await mockApi.updateScenarioItem(updatedItem);
      setScenarioItems(prev => prev.map(i => i.id === item.id ? updatedItem : i));
    } catch (err: any) {
      alert(`Ошибка обновления: ${err.message}`);
    }
  };

  if (loading) return (
    <div className="flex items-center justify-center h-96">
      <div className="flex flex-col items-center gap-4">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-600"></div>
        <p className="text-slate-400 font-medium animate-pulse">Синхронизация с сервером...</p>
      </div>
    </div>
  );

  if (error) return (
    <div className="p-8 flex flex-col items-center justify-center h-96 text-center">
      <div className="w-20 h-20 bg-rose-50 rounded-full flex items-center justify-center mb-6">
        <i className="fas fa-plug text-rose-500 text-3xl"></i>
      </div>
      <h3 className="text-2xl font-bold text-slate-800 mb-2">Ошибка подключения</h3>
      <p className="text-slate-500 max-w-md mb-8">{error}</p>
      <button onClick={() => loadData(true)} className="bg-slate-800 text-white px-8 py-3 rounded-2xl font-bold hover:bg-slate-700 transition flex items-center gap-2">
        <i className="fas fa-sync"></i> Повторить попытку
      </button>
    </div>
  );

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-10">
        <div>
          <h2 className="text-3xl font-black text-slate-800 tracking-tight">Сценарии поиска</h2>
          <p className="text-slate-500 mt-1">Настройте параметры мониторинга и ключевые слова</p>
        </div>
        <div className="flex gap-3">
          <button 
            onClick={handleRunAll}
            disabled={runAllLoading || scenarios.length === 0}
            className="bg-emerald-600 text-white px-8 py-3 rounded-2xl font-bold hover:bg-emerald-700 shadow-xl shadow-emerald-600/30 flex items-center gap-2 transition-all active:scale-95 disabled:opacity-50 disabled:grayscale disabled:scale-100"
          >
            <i className={`fas ${runAllLoading ? 'fa-spinner fa-spin' : 'fa-play-circle'}`}></i>
            Запустить всё
          </button>
          <button 
            onClick={() => { setEditingScenario(null); setFormData({name:'', search_words: ''}); setIsModalOpen(true); }}
            className="bg-indigo-600 text-white px-8 py-3 rounded-2xl font-bold hover:bg-indigo-700 shadow-xl shadow-indigo-600/30 flex items-center gap-2 transition-transform active:scale-95"
          >
            <i className="fas fa-plus"></i> Создать новый
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {scenarios.map(temp => (
          <div key={temp.id} className={`bg-white border border-slate-200 rounded-3xl p-6 flex items-center justify-between shadow-sm transition-all hover:shadow-md ${actionLoading === temp.id ? 'opacity-50 pointer-events-none' : ''}`}>
            <div className="flex items-center gap-6 flex-1">
              <div className="flex-1">
                <div className="flex items-center gap-2">
                   <h3 className="text-xl font-bold text-slate-800">{temp.name}</h3>
                </div>
                <div className="flex flex-wrap items-center gap-3 mt-1">
                   {temp.last_run_cost !== undefined && temp.last_run_cost > 0 && (
                     <div className="flex items-center gap-1.5 px-2 py-0.5 bg-amber-50 text-amber-700 rounded text-[10px] font-black uppercase tracking-wider">
                       <i className="fas fa-coins text-[8px]"></i> 
                       Запуск: {temp.last_run_cost.toLocaleString('ru-RU')} ₽
                     </div>
                   )}
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button 
                onClick={() => handleOpenItems(temp)}
                className="px-4 py-2 bg-slate-100 text-slate-600 rounded-xl font-bold text-sm hover:bg-slate-200 transition flex items-center gap-2"
              >
                <i className="fas fa-table"></i> Данные
              </button>
              <button 
                onClick={() => handleRun(temp.id)}
                className="px-4 py-2 bg-emerald-50 text-emerald-600 rounded-xl font-bold text-sm hover:bg-emerald-600 hover:text-white transition"
                title="Запустить сбор"
              >
                <i className="fas fa-play mr-2"></i> Пуск
              </button>
              <button 
                onClick={(e) => handleOpenEdit(e, temp)}
                className="w-10 h-10 flex items-center justify-center bg-slate-50 text-slate-400 rounded-xl hover:bg-indigo-50 hover:text-indigo-600 transition"
                title="Редактировать"
              >
                <i className="fas fa-pen text-sm"></i>
              </button>
              <button 
                onClick={(e) => handleDelete(e, temp.id)}
                className="w-10 h-10 flex items-center justify-center bg-slate-50 text-rose-400 rounded-xl hover:bg-rose-500 hover:text-white transition"
                title="Удалить из БД"
              >
                <i className="fas fa-trash-alt text-sm"></i>
              </button>
            </div>
          </div>
        ))}

        {scenarios.length === 0 && (
          <div className="py-24 text-center border-2 border-dashed border-slate-200 rounded-[40px] flex flex-col items-center">
            <div className="w-20 h-20 bg-slate-50 rounded-full flex items-center justify-center mb-4">
               <i className="fas fa-inbox text-slate-200 text-3xl"></i>
            </div>
            <p className="text-slate-400 font-bold text-lg">База данных пуста</p>
            <p className="text-slate-400 text-sm mt-1">Создайте первый сценарий, чтобы начать мониторинг тендеров.</p>
          </div>
        )}
      </div>

      {/* Scenario Edit Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-slate-900/70 backdrop-blur-sm z-50 flex items-center justify-center p-6">
          <div className="bg-white w-full max-w-2xl max-h-[85vh] rounded-[32px] shadow-2xl animate-in zoom-in duration-300 overflow-hidden flex flex-col">
             <div className="p-8 border-b border-slate-50 flex justify-between items-center bg-slate-50/50 shrink-0">
                <h3 className="text-2xl font-black text-slate-800">
                  {editingScenario ? 'Обновить сценарий' : 'Новый сценарий'}
                </h3>
                <button onClick={() => setIsModalOpen(false)} className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-slate-200 transition text-slate-400"><i className="fas fa-times"></i></button>
             </div>
             <form onSubmit={handleSubmit} className="p-8 space-y-6 overflow-y-auto custom-scrollbar flex-1">
                <div className="space-y-2">
                   <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest block ml-1">Название сценария</label>
                   <input 
                      type="text" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})}
                      required placeholder="Например: Поставка серверов"
                      className="w-full bg-slate-50 border border-slate-200 px-6 py-4 rounded-2xl focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 focus:outline-none transition-all font-medium"
                   />
                </div>
                <div className="space-y-2">
                   <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest block ml-1">Ключевые слова</label>
                   <div className="flex gap-2">
                      <input 
                         type="text" 
                         value={newWord} 
                         onChange={e => setNewWord(e.target.value)}
                         onKeyPress={e => e.key === 'Enter' && (e.preventDefault(), addWord())}
                         placeholder="Добавить слово..."
                         className="flex-1 bg-slate-50 border border-slate-200 px-6 py-4 rounded-2xl focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 focus:outline-none transition-all font-medium"
                      />
                      <button 
                         type="button"
                         onClick={addWord}
                         className="w-14 h-14 bg-indigo-600 text-white rounded-2xl flex items-center justify-center hover:bg-indigo-700 transition shadow-lg shadow-indigo-600/20"
                      >
                         <i className="fas fa-plus"></i>
                      </button>
                   </div>
                   <div className="flex flex-wrap gap-2 mt-3 max-h-[250px] overflow-y-auto p-3 bg-slate-50 rounded-2xl border border-slate-100 custom-scrollbar empty:hidden">
                      {formData.search_words ? formData.search_words.split(',').map((word, idx) => {
                         const trimmed = word.trim();
                         if (!trimmed) return null;
                         return (
                            <div key={idx} className="bg-white border border-slate-200 px-3 py-1.5 rounded-xl flex items-center gap-2 shadow-sm group h-fit w-fit">
                               <span className="text-sm font-bold text-slate-700">{trimmed}</span>
                               <button 
                                  type="button"
                                  onClick={() => removeWord(trimmed)}
                                  className="text-slate-300 hover:text-rose-500 transition"
                               >
                                  <i className="fas fa-times text-xs"></i>
                               </button>
                            </div>
                         );
                      }) : (
                         <p className="text-slate-400 text-xs font-medium m-auto py-2">Слова не добавлены</p>
                      )}
                   </div>
                </div>
                <div className="pt-4 flex gap-3 shrink-0 bg-white sticky bottom-0">
                   <button type="button" onClick={() => setIsModalOpen(false)} className="flex-1 py-4 font-bold text-slate-500 hover:bg-slate-100 rounded-2xl transition">Отмена</button>
                   <button type="submit" className="flex-[2] bg-indigo-600 text-white py-4 font-bold rounded-2xl shadow-lg shadow-indigo-600/30 active:scale-95 hover:bg-indigo-700 transition">
                     {editingScenario ? 'Сохранить изменения' : 'Создать сценарий'}
                   </button>
                </div>
             </form>
          </div>
        </div>
      )}

      {/* Items Management Modal */}
      {isItemsModalOpen && selectedScenario && (
        <div className="fixed inset-0 bg-slate-900/80 backdrop-blur-md z-[60] flex items-center justify-center p-4 sm:p-10">
          <div className="bg-white w-full max-w-6xl max-h-[90vh] rounded-[40px] shadow-2xl relative overflow-hidden flex flex-col animate-in zoom-in duration-300">
            <div className="p-8 border-b border-slate-100 flex justify-between items-center bg-white sticky top-0 z-20">
              <div>
                <h3 className="text-2xl font-black text-slate-800">Данные сценария: {selectedScenario.name}</h3>
                <p className="text-slate-400 text-sm mt-1">Редактируйте данные, загруженные из Excel</p>
              </div>
              <button onClick={() => setIsItemsModalOpen(false)} className="w-12 h-12 flex items-center justify-center rounded-full bg-slate-50 text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition">
                <i className="fas fa-times fa-lg"></i>
              </button>
            </div>

            <div className="flex-1 overflow-auto p-8 custom-scrollbar">
              {itemsLoading ? (
                <div className="py-20 text-center">
                  <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600 mx-auto mb-4"></div>
                  <p className="text-slate-400">Загрузка данных...</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse">
                    <thead>
                      <tr className="border-b border-slate-100">
                        <th className="text-left py-4 px-4 text-[10px] font-black text-slate-400 uppercase tracking-widest">Артикул</th>
                        <th className="text-left py-4 px-4 text-[10px] font-black text-slate-400 uppercase tracking-widest">Название</th>
                        <th className="text-left py-4 px-4 text-[10px] font-black text-slate-400 uppercase tracking-widest">Категория</th>
                        <th className="text-left py-4 px-4 text-[10px] font-black text-slate-400 uppercase tracking-widest">Цена</th>
                        <th className="text-left py-4 px-4 text-[10px] font-black text-slate-400 uppercase tracking-widest">Описание</th>
                      </tr>
                    </thead>
                    <tbody>
                      {scenarioItems.map(item => (
                        <tr key={item.id} className="border-b border-slate-50 hover:bg-slate-50/50 transition-colors">
                          <td className="py-4 px-4">
                            <input 
                              type="text" value={item.article} 
                              onChange={(e) => handleUpdateItem(item, 'article', e.target.value)}
                              className="bg-transparent border-none focus:ring-2 focus:ring-indigo-500/20 rounded px-2 py-1 w-full font-mono text-xs text-slate-600"
                            />
                          </td>
                          <td className="py-4 px-4">
                            <input 
                              type="text" value={item.name} 
                              onChange={(e) => handleUpdateItem(item, 'name', e.target.value)}
                              className="bg-transparent border-none focus:ring-2 focus:ring-indigo-500/20 rounded px-2 py-1 w-full font-bold text-sm text-slate-800"
                            />
                          </td>
                          <td className="py-4 px-4">
                            <input 
                              type="text" value={item.category} 
                              onChange={(e) => handleUpdateItem(item, 'category', e.target.value)}
                              className="bg-transparent border-none focus:ring-2 focus:ring-indigo-500/20 rounded px-2 py-1 w-full text-sm text-slate-600"
                            />
                          </td>
                          <td className="py-4 px-4">
                            <input 
                              type="number" value={item.price} 
                              onChange={(e) => handleUpdateItem(item, 'price', Number(e.target.value))}
                              className="bg-transparent border-none focus:ring-2 focus:ring-indigo-500/20 rounded px-2 py-1 w-full font-black text-indigo-600"
                            />
                          </td>
                          <td className="py-4 px-4">
                            <textarea 
                              value={item.description} 
                              onChange={(e) => handleUpdateItem(item, 'description', e.target.value)}
                              className="bg-transparent border-none focus:ring-2 focus:ring-indigo-500/20 rounded px-2 py-1 w-full text-xs text-slate-500 resize-none h-10"
                            />
                          </td>
                        </tr>
                      ))}
                      {scenarioItems.length === 0 && (
                        <tr>
                          <td colSpan={5} className="py-20 text-center text-slate-400 font-medium">
                            Данные не загружены. Используйте кнопку Excel для импорта.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
            
            <div className="p-8 border-t border-slate-100 bg-slate-50/30 flex justify-end">
              <button 
                onClick={() => setIsItemsModalOpen(false)}
                className="px-8 py-3 bg-indigo-600 text-white rounded-2xl font-bold hover:bg-indigo-700 transition shadow-lg shadow-indigo-600/20"
              >
                Готово
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ScenarioManager;
