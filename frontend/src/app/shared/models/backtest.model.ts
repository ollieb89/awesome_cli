export interface Backtest {
  id: number;
  strategy: number; // ID or object depending on serialization depth
  strategy_name?: string;
  asset: string; // Symbol
  start_date: string;
  end_date: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  metrics?: {
    total_return: number;
    sharpe_ratio: number;
    max_drawdown: number;
    win_rate?: number;
  };
}
