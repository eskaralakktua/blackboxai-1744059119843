// Tipos para la API
export interface APIResponse<T = any> {
  success: boolean;
  data: T;
  error?: string;
}

export interface UploadResponse {
  analysis_id: string;
  wallets_count: number;
  status: string;
}

export interface AnalysisStatus {
  status: 'processing' | 'completed' | 'error';
  progress: number;
  message?: string;
  error?: string;
}

export interface AnalysisReport {
  analysis_id: string;
  timestamp: string;
  summary: string;
  graph_data: GraphData;
  ai_insights: AIInsight[];
  wallets_analyzed: WalletStats[];
}

// Tipos para el grafo
export interface GraphData {
  nodes: Node[];
  edges: Edge[];
}

export interface Node {
  id: string;
  label: string;
  size: number;
  color: string;
  properties?: Record<string, any>;
}

export interface Edge {
  source: string;
  target: string;
  weight: number;
  properties?: Record<string, any>;
}

// Tipos para los componentes
export interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  color?: 'blue' | 'green' | 'red' | 'yellow' | 'gray';
}

export interface NotificationProps {
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration?: number;
  onClose?: () => void;
}

export interface DropzoneProps {
  onFileAccepted: (file: File) => Promise<void>;
}

export interface GraphViewerProps {
  data: GraphData;
  onNodeClick?: (nodeId: string) => void;
  onEdgeClick?: (edge: Edge) => void;
}

// Tipos para los datos de análisis
export interface AIInsight {
  wallet_address: string;
  behavior_pattern: string;
  entity_type: string;
  risk_score: number;
  observations: string[];
}

export interface WalletStats {
  address: string;
  blockchain: string;
  first_transaction_date: string;
  last_transaction_date: string;
  total_sent_usd: number;
  total_received_usd: number;
  transaction_count: number;
  unique_tokens: TokenInfo[];
  most_frequent_contracts: string[];
}

export interface TokenInfo {
  address: string;
  name: string;
  symbol: string;
  total_value_usd: number;
  transaction_count: number;
}

// Tipos para el estado global (si se necesita)
export interface AppState {
  currentAnalysis?: {
    id: string;
    status: AnalysisStatus;
  };
  notifications: NotificationProps[];
}