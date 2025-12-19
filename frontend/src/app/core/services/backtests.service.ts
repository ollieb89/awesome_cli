import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { Backtest } from '../../shared/models/backtest.model';
import { ApiResponse } from '../../shared/models/api-response.model';

@Injectable({ providedIn: 'root' })
export class BacktestsService {
  private readonly baseUrl = '/api/v1';

  constructor(private http: HttpClient) {}

  getBacktests(limit = 20): Observable<Backtest[]> {
    return this.http
      .get<ApiResponse<Backtest[]>>(`${this.baseUrl}/backtests`, {
        params: { limit },
      })
      .pipe(map((res) => res.data));
  }

  getBacktest(id: string): Observable<Backtest> {
    return this.http
      .get<ApiResponse<Backtest>>(`${this.baseUrl}/backtests/${id}`)
      .pipe(map((res) => res.data));
  }

  getBacktestMetrics(id: string): Observable<any> {
    return this.http
      .get<ApiResponse<any>>(`${this.baseUrl}/backtests/${id}/metrics`)
      .pipe(map((res) => res.data));
  }

  getBacktestLedger(id: string): Observable<any[]> {
    return this.http
      .get<ApiResponse<any[]>>(`${this.baseUrl}/backtests/${id}/ledger`)
      .pipe(map((res) => res.data));
  }
}
