
export enum PipelineStatus {
  CREATED = 'created',
  STARTED = 'started',
  SEARCHING = 'searching',
  PROCESSING = 'processing',
  FINISHED = 'finished',
  ERROR = 'error'
}

export interface Scenario {
  id: number;
  name: string;
  user_id: number;
  create_date: string;
  last_scan_date: string | null;
  start_at?: string | null;
  status: string;
  search_words?: string;
  last_run_cost?: number;
  total_cost?: number;
  total_found?: number;
  processed_count?: number;
  matched_count?: number;
}

export interface ScenarioItem {
  id: number;
  scenario_id: number;
  article: string;
  name: string;
  category: string;
  price: number;
  description: string;
}

export interface RunHistory {
  id: number;
  scenario_id: number;
  scenario_name: string;
  start_at: string;
  end_at: string;
  found: number;
  cost: number;
}

export interface TenderItem {
  id: number;
  tender_id: number;
  name: string;
  quantity: number;
  unit: string;
  matched_article?: string;
  margin?: number;
  is_matched: boolean;
}

export interface Tender {
  id: number;
  url: string;
  name: string;
  customer: string;
  cost: string | null;
  status: string;
  scenario_id: number;
  extract_at?: string;
  is_match?: boolean;
  total_margin?: number;
  items?: TenderItem[];
}

export interface User {
  id: number;
  tg_id: number;
  role: 1 | 2;
  access: 0 | 1;
  username?: string;
}
