
import { Scenario, Tender, PipelineStatus, ScenarioItem } from '../types';

const STORAGE_KEY_SCENARIOS = 'tp_scenarios';
const STORAGE_KEY_TENDERS = 'tp_tenders';
const STORAGE_KEY_ANALYSIS = 'tp_analysis';
const STORAGE_KEY_HISTORY = 'tp_history';
const STORAGE_KEY_USAGES = 'tp_llm_usages';
const STORAGE_KEY_SCENARIO_ITEMS = 'tp_scenario_items';

const _get = <T>(key: string): T[] => {
  const data = localStorage.getItem(key);
  if (!data || data === 'undefined') return [];
  try {
    return JSON.parse(data);
  } catch (e) {
    console.error(`Error parsing JSON from localStorage for key ${key}:`, e);
    return [];
  }
};

const _set = <T>(key: string, data: T[]) => {
  localStorage.setItem(key, JSON.stringify(data));
};

export const db = {
  // SCENARIOS
  queryScenarios: (): Scenario[] => {
    return _get<Scenario>(STORAGE_KEY_SCENARIOS);
  },

  upsertScenario: (payload: Partial<Scenario>): Scenario => {
    const scenarios = _get<Scenario>(STORAGE_KEY_SCENARIOS);
    let result: Scenario;

    if (payload.id) {
      const index = scenarios.findIndex(t => t.id === Number(payload.id));
      if (index !== -1) {
        scenarios[index] = { ...scenarios[index], ...payload } as Scenario;
        result = scenarios[index];
      } else {
        throw new Error("Scenario not found");
      }
    } else {
      const nextId = scenarios.length > 0 ? Math.max(...scenarios.map(t => t.id)) + 1 : 1;
      const newScenario: Scenario = {
        id: nextId,
        name: payload.name || 'Untitled',
        search_words: payload.search_words || '',
        user_id: 1,
        create_date: new Date().toISOString(),
        last_scan_date: null,
        status: PipelineStatus.CREATED,
      };
      scenarios.push(newScenario);
      result = newScenario;
    }

    _set(STORAGE_KEY_SCENARIOS, scenarios);
    return result;
  },

  deleteScenario: (id: number): void => {
    const scenarios = _get<Scenario>(STORAGE_KEY_SCENARIOS);
    const filtered = scenarios.filter(t => t.id !== Number(id));
    _set(STORAGE_KEY_SCENARIOS, filtered);
    
    // Also delete items
    const items = _get<ScenarioItem>(STORAGE_KEY_SCENARIO_ITEMS);
    const filteredItems = items.filter(i => i.scenario_id !== id);
    _set(STORAGE_KEY_SCENARIO_ITEMS, filteredItems);
  },

  // SCENARIO ITEMS
  queryScenarioItems: (scenarioId: number): ScenarioItem[] => {
    const items = _get<ScenarioItem>(STORAGE_KEY_SCENARIO_ITEMS);
    return items.filter(i => i.scenario_id === scenarioId);
  },

  upsertScenarioItem: (item: ScenarioItem): ScenarioItem => {
    const items = _get<ScenarioItem>(STORAGE_KEY_SCENARIO_ITEMS);
    const index = items.findIndex(i => i.id === item.id);
    if (index !== -1) {
      items[index] = item;
    } else {
      items.push(item);
    }
    _set(STORAGE_KEY_SCENARIO_ITEMS, items);
    return item;
  },

  // TENDERS
  queryTenders: (scenarioId?: number): Tender[] => {
    const tenders = _get<Tender>(STORAGE_KEY_TENDERS);
    return scenarioId ? tenders.filter(t => t.scenario_id === scenarioId) : tenders;
  },

  // ANALYSIS
  queryAnalysis: (tenderId: number) => {
    const analyses = _get<any>(STORAGE_KEY_ANALYSIS);
    return analyses.find((a: any) => a.tender_id === tenderId);
  },

  // USAGES (for costs)
  queryUsages: (scenarioId: number) => {
    const usages = _get<any>(STORAGE_KEY_USAGES);
    return usages.filter((u: any) => u.template_id === scenarioId); // template_id in usages table
  },

  // HISTORY
  queryHistory: () => {
    return _get<any>(STORAGE_KEY_HISTORY);
  },

  // Инициализация начальными данными, если БД пуста
  initIfEmpty: () => {
    const scenarios = _get<Scenario>(STORAGE_KEY_SCENARIOS);
    const tenders = _get<Tender>(STORAGE_KEY_TENDERS);
    
    if (scenarios.length === 0 || tenders.length === 0) {
      const initialScenario = {
        id: 1,
        name: "IT Инфраструктура",
        search_words: "сервер, ноутбук, по, лицензия",
        user_id: 1,
        create_date: new Date().toISOString(),
        last_scan_date: new Date().toISOString(),
        status: 'finished'
      };
      
      // If scenario 1 doesn't exist, add it
      if (!scenarios.find(s => s.id === 1)) {
        scenarios.push(initialScenario);
        _set(STORAGE_KEY_SCENARIOS, scenarios);
      }
      
      const initialTenders = [
        { 
          id: 1, 
          scenario_id: 1, 
          name: "Поставка серверного оборудования для ЦОД", 
          customer: "ПАО Сбербанк", 
          cost: "12500000", 
          status: 'new', 
          extract_at: new Date().toISOString(), 
          url: "#",
          is_match: true,
          total_margin: 1250000,
          items: [
            { id: 1, tender_id: 1, name: "Сервер стоечный 2U (Dual Xeon Gold 6230, 256GB RAM, 8x1.2TB SAS)", quantity: 5, unit: "шт", matched_article: "SRV-PRO-2U-G2", margin: 1000000, is_matched: true },
            { id: 2, tender_id: 1, name: "Комплект направляющих для шкафа 19\" (глубина 800-1000мм)", quantity: 5, unit: "шт", matched_article: "RAIL-KIT-UNIV-02", margin: 250000, is_matched: true }
          ]
        },
        { 
          id: 2, 
          scenario_id: 1, 
          name: "Закупка ноутбуков и периферии для сотрудников", 
          customer: "Мэрия Москвы", 
          cost: "4200000", 
          status: 'new', 
          extract_at: new Date(Date.now() - 86400000).toISOString(), 
          url: "#",
          is_match: true,
          total_margin: 680000,
          items: [
            { id: 3, tender_id: 2, name: "Ноутбук 15.6\" IPS FHD, i7-12700H, 16GB, 512GB SSD, Win11 Pro", quantity: 20, unit: "шт", matched_article: "NB-WORK-X1-GEN2", margin: 600000, is_matched: true },
            { id: 4, tender_id: 2, name: "Мышь беспроводная оптическая (Bluetooth/2.4GHz, 1600 DPI)", quantity: 20, unit: "шт", matched_article: "MS-WL-SILENT-PRO", margin: 80000, is_matched: true },
            { id: 5, tender_id: 2, name: "Сумка-чехол для ноутбука 15.6\" (противоударная, черная)", quantity: 20, unit: "шт", is_matched: false }
          ]
        },
        { 
          id: 3, 
          scenario_id: 1, 
          name: "Поставка МФУ и расходных материалов", 
          customer: "РЖД", 
          cost: "1800000", 
          status: 'new', 
          extract_at: new Date(Date.now() - 172800000).toISOString(), 
          url: "#",
          is_match: true,
          total_margin: 0,
          items: [
            { id: 6, tender_id: 3, name: "МФУ Лазерное A3 (Печать/Сканер/Копир, 25 стр/мин, сетевое)", quantity: 2, unit: "шт", is_matched: false },
            { id: 7, tender_id: 3, name: "Картридж черный повышенной емкости (до 15000 стр)", quantity: 10, unit: "шт", is_matched: false }
          ]
        },
        { 
          id: 4, 
          scenario_id: 1, 
          name: "Сетевое оборудование для филиальной сети", 
          customer: "Газпром", 
          cost: "8900000", 
          status: 'new', 
          extract_at: new Date(Date.now() - 3600000).toISOString(), 
          url: "#",
          is_match: true,
          total_margin: 950000,
          items: [
            { id: 8, tender_id: 4, name: "Коммутатор управляемый L3, 48 портов 10/100/1000Base-T PoE+, 4xSFP+", quantity: 3, unit: "шт", matched_article: "SW-NET-48P-L3-ADV", margin: 950000, is_matched: true }
          ]
        },
        { 
          id: 5, 
          scenario_id: 1, 
          name: "Закупка персональных компьютеров", 
          customer: "ПАО Газпром", 
          cost: "123456", 
          status: 'new', 
          extract_at: new Date().toISOString(), 
          url: "#",
          is_match: true,
          total_margin: 456,
          items: [
            { id: 9, tender_id: 5, name: "Компьютер (Арт. 10000)", quantity: 1, unit: "шт", matched_article: "77", margin: 456, is_matched: true }
          ]
        }
      ];
      _set(STORAGE_KEY_TENDERS, initialTenders);

      const initialAnalysis = [
        { id: 1, tender_id: 1, verdict: true, reason: "Ок", doc_summary: "Кратко" },
        { id: 2, tender_id: 2, verdict: true, reason: "Ок", doc_summary: "Кратко" }
      ];
      _set(STORAGE_KEY_ANALYSIS, initialAnalysis);

      const initialUsages = [
        { id: 1, template_id: 1, cost_usd: 1.5, created_at: new Date().toISOString() }
      ];
      _set(STORAGE_KEY_USAGES, initialUsages);

      const initialItems = [
        { id: 1, scenario_id: 1, article: "SRV-001", name: "Сервер Dell R740", category: "Серверы", price: 450000, description: "2x Xeon Gold, 128GB RAM" },
        { id: 2, scenario_id: 1, article: "SW-WIN-10", name: "Windows 10 Pro", category: "ПО", price: 15000, description: "Лицензия OEM" }
      ];
      _set(STORAGE_KEY_SCENARIO_ITEMS, initialItems);
    }
  }
};
