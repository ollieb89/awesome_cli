export interface Asset {
  symbol: string;
  name: string;
  type: string;
  active: boolean;
}

export interface PricePoint {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}
