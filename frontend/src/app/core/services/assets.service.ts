import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { Asset, PricePoint } from '../../shared/models/asset.model';
import { ApiResponse } from '../../shared/models/api-response.model';

@Injectable({ providedIn: 'root' })
export class AssetsService {
  private readonly baseUrl = '/api/v1';

  constructor(private http: HttpClient) {}

  getAssets(limit = 20): Observable<Asset[]> {
    return this.http
      .get<ApiResponse<Asset[]>>(`${this.baseUrl}/assets`, {
        params: { limit },
      })
      .pipe(map((res) => res.data));
  }

  getAsset(symbol: string): Observable<Asset> {
    return this.http
      .get<ApiResponse<Asset>>(`${this.baseUrl}/assets/${symbol}`)
      .pipe(map((res) => res.data));
  }

  getPriceSeries(symbol: string): Observable<PricePoint[]> {
    return this.http
      .get<ApiResponse<PricePoint[]>>(`${this.baseUrl}/assets/${symbol}/price-series`)
      .pipe(map((res) => res.data));
  }
}
