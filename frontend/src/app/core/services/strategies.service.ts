import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { Strategy } from '../../shared/models/strategy.model';
import { ApiResponse } from '../../shared/models/api-response.model';

@Injectable({ providedIn: 'root' })
export class StrategiesService {
  private readonly baseUrl = '/api/v1';

  constructor(private http: HttpClient) {}

  getStrategies(limit = 20): Observable<Strategy[]> {
    return this.http
      .get<ApiResponse<Strategy[]>>(`${this.baseUrl}/strategies`, {
        params: { limit },
      })
      .pipe(map((res) => res.data));
  }

  getStrategy(id: string): Observable<Strategy> {
    return this.http
      .get<ApiResponse<Strategy>>(`${this.baseUrl}/strategies/${id}`)
      .pipe(map((res) => res.data));
  }
}
