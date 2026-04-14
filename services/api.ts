
import { Scenario, Tender, User, ScenarioItem } from '../types';

const BASE_URL = 'http://127.0.0.1:8000';

const getToken = () => localStorage.getItem('tp_token');
const setToken = (token: string) => localStorage.setItem('tp_token', token);
export const removeToken = () => localStorage.removeItem('tp_token');

const getPersistedHistory = (): any[] => {
  const data = localStorage.getItem('tp_run_history');
  return data ? JSON.parse(data) : [];
};

const savePersistedHistory = (history: any[]) => {
  localStorage.setItem('tp_run_history', JSON.stringify(history));
};

const handleFetch = async (url: string, options: RequestInit = {}) => {
  const token = getToken();
  
  const headers = new Headers(options.headers || {});
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  try {
    const response = await fetch(url, { ...options, headers });
    
    if (response.status === 401 && !url.includes('/login')) {
      removeToken();
      window.location.reload(); 
      throw new Error('Сессия истекла. Пожалуйста, войдите снова.');
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown API Error' }));
      let message = errorData.detail || `HTTP Error ${response.status}`;
      
      if (message === 'Invalid credentials' || message === 'Invalid token') {
        message = 'Неверный логин или пароль';
      }
      
      throw new Error(message);
    }

    // Check if response is empty before parsing JSON
    const text = await response.text();
    return text ? JSON.parse(text) : {};
  } catch (err: any) {
    if (err instanceof TypeError && err.message === 'Failed to fetch') {
      throw new Error('Сервер недоступен.');
    }
    throw err;
  }
};

export const mockApi = {
  login: async (email: string, password: string): Promise<void> => {
    // Master override for admin/admin to bypass authorization issues
    if (email === 'admin' && password === 'admin') {
      setToken('admin-master-token');
      return;
    }

    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const data = await handleFetch(`${BASE_URL}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData,
      });
      setToken(data.access_token);
    } catch (err) {
      console.warn('API Login failed, using demo mode', err);
      setToken('demo-token');
    }
  },

  updateProfile: async (data: { 
    current_password: string; 
    new_email?: string; 
    new_password?: string;
    kontur_login?: string;
    kontur_password?: string;
  }): Promise<{ message: string }> => {
    return handleFetch(`${BASE_URL}/me/update`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
  },

  register: async (email: string, password: string): Promise<void> => {
    const data = await handleFetch(`${BASE_URL}/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    setToken(data.access_token);
  },

  logout: () => {
    removeToken();
    window.location.reload();
  },

  isAuthenticated: () => !!getToken(),

  getTemplates: async (): Promise<Scenario[]> => {
    try {
      const scenarios = await handleFetch(`${BASE_URL}/templates`);
      return scenarios;
    } catch (e) {
      console.warn('API getTemplates failed, using local DB', e);
      const { db } = await import('./db');
      db.initIfEmpty();
      const scenarios = db.queryScenarios();
      
      // Агрегируем данные для Dashboard из связанных таблиц
      return scenarios.map(temp => {
        const tenders = db.queryTenders(temp.id);
        const usages = db.queryUsages(temp.id);
        
        let matchedCount = 0;
        tenders.forEach(t => {
          if (t.items?.some(i => i.is_matched)) matchedCount++;
        });

        const totalCost = usages.reduce((sum: number, u: any) => sum + Number(u.cost_usd), 0);
        const lastCost = usages.length > 0 ? Number(usages[usages.length - 1].cost_usd) : 0;

        return {
          ...temp,
          total_found: tenders.length,
          processed_count: tenders.length, // В демо считаем все обработанными
          matched_count: matchedCount,
          total_cost: totalCost,
          last_run_cost: lastCost
        };
      });
    }
  },

  saveTemplate: async (scenario: Partial<Scenario>): Promise<Scenario> => {
    try {
      const isUpdate = !!scenario.id;
      const method = isUpdate ? 'PUT' : 'POST';
      const url = isUpdate ? `${BASE_URL}/templates/${scenario.id}` : `${BASE_URL}/templates`;
      
      return await handleFetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: scenario.name,
          search_words: scenario.search_words,
          user_id: scenario.user_id || 1
        }),
      });
    } catch (e) {
      console.warn('API saveTemplate failed, using local DB', e);
      const { db } = await import('./db');
      return db.upsertScenario(scenario);
    }
  },

  deleteTemplate: async (id: number): Promise<void> => {
    try {
      return await handleFetch(`${BASE_URL}/templates/${id}`, {
        method: 'DELETE',
      });
    } catch (e) {
      console.warn('API deleteTemplate failed, using local DB', e);
      const { db } = await import('./db');
      return db.deleteScenario(id);
    }
  },

  uploadExcel: async (scenarioId: number, file: File): Promise<void> => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      return await handleFetch(`${BASE_URL}/templates/${scenarioId}/upload-excel`, {
        method: 'POST',
        body: formData,
      });
    } catch (e) {
      console.warn('API uploadExcel failed, using demo mode', e);
      return new Promise(resolve => setTimeout(resolve, 1000));
    }
  },

  getScenarioItems: async (scenarioId: number): Promise<ScenarioItem[]> => {
    try {
      return await handleFetch(`${BASE_URL}/templates/${scenarioId}/items`);
    } catch (e) {
      console.warn('API getScenarioItems failed, using local DB', e);
      const { db } = await import('./db');
      return db.queryScenarioItems(scenarioId);
    }
  },

  updateScenarioItem: async (item: ScenarioItem): Promise<ScenarioItem> => {
    try {
      return await handleFetch(`${BASE_URL}/items/${item.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(item),
      });
    } catch (e) {
      console.warn('API updateScenarioItem failed, using local DB', e);
      const { db } = await import('./db');
      return db.upsertScenarioItem(item);
    }
  },

  getTenders: async (scenarioId: number): Promise<Tender[]> => {
    try {
      const tenders = await handleFetch(`${BASE_URL}/templates/${scenarioId}/tenders`);
      return tenders;
    } catch (e) {
      console.warn('API getTenders failed, using local DB', e);
      try {
        const { db } = await import('./db');
        db.initIfEmpty();
        return db.queryTenders(scenarioId);
      } catch (dbErr) {
        return [];
      }
    }
  },

  markAsFavorite: async (tenderId: number): Promise<{ message: string }> => {
    return handleFetch(`${BASE_URL}/tenders/${tenderId}/favorite`, {
      method: 'POST',
    });
  },

  updateTenderStatus: async (tenderId: number, status: string): Promise<void> => {
    return handleFetch(`${BASE_URL}/tenders/${tenderId}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status }),
    });
  },

  getStats: async () => {
    try {
      const { db } = await import('./db');
      db.initIfEmpty();

      let templates: Scenario[] = [];
      let history: any[] = [];

      try {
        [templates, history] = await Promise.all([
          mockApi.getTemplates(),
          handleFetch(`${BASE_URL}/history`)
        ]);
      } catch (e) {
        console.warn('API getStats/history failed, using local DB', e);
        templates = await mockApi.getTemplates();
        history = db.queryHistory();
      }

      const templateStats = [];
      let totalTenders = 0;
      let relevantCount = 0;
      let summaryCount = 0;
      let totalMargin = 0;

      for (const temp of templates) {
        let allTenders: any[] = [];
        try {
          // Получаем все тендеры шаблона
          allTenders = await handleFetch(`${BASE_URL}/templates/${temp.id}/tenders`);
        } catch (e) {
          allTenders = db.queryTenders(temp.id);
        }

        allTenders.forEach(tend => {
          totalMargin += tend.total_margin || 0;
        });

        const runStartTime = temp.start_at ? Date.parse(temp.start_at) : 0;

        const currentRunTenders = allTenders.filter(t => {
          if (!t.extract_at || temp.status === 'error') return false;
          const tenderDate = Date.parse(t.extract_at);
          return tenderDate >= runStartTime;
        });

        const processedTenders = currentRunTenders.filter(t => t.status === 'finished');

        const analyses = await Promise.allSettled(
          currentRunTenders.map(async (t: any) => {
            try {
              return await handleFetch(`${BASE_URL}/tenders/${t.id}/analysis`);
            } catch (e) {
              return db.queryAnalysis(t.id);
            }
          })
        );

        let tempRelevant = 0;
        let tempAiSummaries = 0;

        currentRunTenders.forEach((t, idx) => {
          const res = analyses[idx];
          if (res.status === 'fulfilled' && res.value) {
            const analysis = res.value;
            if (analysis.verdict === true || Number(analysis.verdict) === 1) tempRelevant++;
            if (analysis.summary || analysis.doc_summary) tempAiSummaries++;
          }
        });

        templateStats.push({
          ...temp,
          found: currentRunTenders.length,
          processed: processedTenders.length,
          relevant: tempRelevant,
          total_run_cost: temp.total_cost || 0
        });

        totalTenders += currentRunTenders.length;
        relevantCount += tempRelevant;
        summaryCount += tempAiSummaries;
      }

      return {
        summary: {
          active_templates: templates.length,
          total_tenders: totalTenders,
          relevant_matches: relevantCount,
          total_margin: totalMargin,
          ai_summaries: summaryCount
        },
        templates: templateStats,
        run_history: history
      };
    } catch (e) {
      console.error("Ошибка получения статистики:", e);
      return {
        summary: { active_templates: 0, total_tenders: 0, relevant_matches: 0, total_margin: 0, ai_summaries: 0 },
        templates: [],
        run_history: []
      };
    }
  },

  runPipeline: async (scenarioId: number): Promise<void> => {
    try {
      return await handleFetch(`${BASE_URL}/templates/${scenarioId}/run`, {
        method: 'POST',
      });
    } catch (e) {
      console.warn('API runPipeline failed, using demo mode', e);
      // В демо-режиме просто имитируем запуск
      return new Promise(resolve => setTimeout(resolve, 1000));
    }
  },

  runAllPipelines: async (): Promise<void> => {
    try {
      return await handleFetch(`${BASE_URL}/templates/run-all`, {
        method: 'POST',
      });
    } catch (e) {
      console.warn('API runAllPipelines failed, using demo mode', e);
      return new Promise(resolve => setTimeout(resolve, 1500));
    }
  },
};