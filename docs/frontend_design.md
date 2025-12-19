# Frontend Design: Awesome CLI

This document outlines the design and architecture for the Angular frontend of the `awesome_cli` crypto analytics platform. The frontend consumes the REST API defined in `DESIGN.md`.

## Frontend Requirements from API

Based on the API resources (assets, strategies, backtests, metrics, ledger, automations), the frontend maps these to the following views and components.

### 1. Dashboard / Overview
*   **Goal:** High-level summary of the system state.
*   **Components:**
    *   **Summary Cards:**
        *   Number of active strategies.
        *   Number of completed backtests.
        *   Top analyzed asset.
    *   **Recent Activity:**
        *   `mat-table` listing the 5 most recent backtests with status and return.
    *   **Market Snapshot:**
        *   List of top assets (e.g., BTC, ETH) with current price (if available via `price-series` or metadata).

### 2. Assets Page
*   **Route:** `/assets`
*   **Goal:** Browse supported crypto assets.
*   **Components:**
    *   **List View:** `mat-table` showing Symbol, Name, Type (Crypto/Fiat), Status.
    *   **Actions:** Search bar (`mat-form-field`), Filter by Active status.
    *   **Navigation:** Click on a row to navigate to Asset Detail.

### 3. Asset Detail Page
*   **Route:** `/assets/:symbol`
*   **Goal:** deep dive into a specific asset.
*   **Components:**
    *   **Header:** Asset metadata (Symbol, Name).
    *   **Price Chart:** Interactive Line/Candlestick chart showing `price-series` data (OHLCV).
    *   **Related Backtests:** List of backtests run on this asset.

### 4. Strategies Page
*   **Route:** `/strategies`
*   **Goal:** Manage trading algorithms.
*   **Components:**
    *   **List View:** `mat-table` listing Strategy Name, Code Reference, Description.
    *   **Detail View:** Expandable row or separate page showing default parameters and associated backtests.

### 5. Backtests Page
*   **Route:** `/backtests`
*   **Goal:** Monitor and review strategy simulations.
*   **Components:**
    *   **List View:** `mat-table` listing Strategy Name, Asset, Time Range, Status, Total Return.
    *   **Controls:** "Run New Backtest" button opening a `mat-dialog` form.

### 6. Backtest Detail Page
*   **Route:** `/backtests/:id`
*   **Goal:** Detailed performance analysis.
*   **Components:**
    *   **Metrics Cards:** Total Return, Sharpe Ratio, Max Drawdown, Win Rate.
    *   **Equity Curve:** Chart plotting the portfolio value over time (from ledger).
    *   **Ledger:** Paginated `mat-table` showing individual trades (Buy/Sell, Price, Timestamp).

---

## Angular Architecture & Routes

The application follows a standard Angular modular architecture with a Core module for singletons (services) and Feature modules for domain domains.

### Directory Structure

```text
src/app/
  core/
    services/
      api.service.ts          # Base HTTP wrapper (optional)
      assets.service.ts       # /api/v1/assets...
      strategies.service.ts   # /api/v1/strategies...
      backtests.service.ts    # /api/v1/backtests...
    interceptors/
      auth.interceptor.ts     # Adds Authorization header
  features/
    dashboard/
      dashboard.component.ts
    assets/
      assets-list/
      asset-detail/
    strategies/
      strategies-list/
    backtests/
      backtests-list/
      backtest-detail/
  shared/
    models/
      api-response.model.ts   # { data, meta, errors } interface
      asset.model.ts
      strategy.model.ts
      backtest.model.ts
    components/
      chart/                  # Reusable chart wrapper
  app-routing.module.ts
```

### Route Definitions & Data Flow

| Route | Component | API Calls | Data Flow |
| :--- | :--- | :--- | :--- |
| `/` | `DashboardComponent` | `GET /backtests?limit=5`<br>`GET /strategies/count`<br>`GET /assets?limit=5` | Services fetch data → Observables → Async Pipe in Template. |
| `/assets` | `AssetsListComponent` | `GET /assets` | `AssetsService` returns `Observable<Asset[]>`. |
| `/assets/:symbol` | `AssetDetailComponent` | `GET /assets/:symbol`<br>`GET /assets/:symbol/price-series` | Fetches metadata and OHLCV data. Points mapped to Chart.js dataset. |
| `/strategies` | `StrategiesListComponent` | `GET /strategies` | `StrategiesService` returns `Observable<Strategy[]>`. |
| `/backtests` | `BacktestsListComponent` | `GET /backtests` | `BacktestsService` returns paginated list. |
| `/backtests/:id` | `BacktestDetailComponent` | `GET /backtests/:id`<br>`GET /backtests/:id/metrics`<br>`GET /backtests/:id/ledger` | ForkJoin or separate subscriptions to load Details, Metrics, and Ledger. |

---

## Angular Services & Components

### 1. API Models

**`src/app/shared/models/api-response.model.ts`**

```typescript
export interface ApiResponse<T> {
  data: T;
  meta?: {
    page: number;
    limit: number;
    total: number;
  };
  errors?: any[];
}
```

**`src/app/shared/models/backtest.model.ts`**

```typescript
export interface Backtest {
  id: number;
  strategy: number; // ID
  strategy_name?: string; // Enhanced by backend or mapped on frontend
  asset: string; // Symbol
  start_date: string;
  end_date: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  metrics?: {
    total_return: number;
    sharpe_ratio: number;
    max_drawdown: number;
  };
}
```

### 2. Backtests Service

**`src/app/core/services/backtests.service.ts`**

```typescript
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

  getBacktestLedger(id: string): Observable<any[]> {
    return this.http
      .get<ApiResponse<any[]>>(`${this.baseUrl}/backtests/${id}/ledger`)
      .pipe(map((res) => res.data));
  }
}
```

### 3. Dashboard Component

**`src/app/features/dashboard/dashboard.component.ts`**

```typescript
import { Component, OnInit } from '@angular/core';
import { BacktestsService } from '../../core/services/backtests.service';
import { Observable } from 'rxjs';
import { Backtest } from '../../shared/models/backtest.model';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  recentBacktests$!: Observable<Backtest[]>;

  constructor(private backtestsService: BacktestsService) {}

  ngOnInit(): void {
    this.recentBacktests$ = this.backtestsService.getBacktests(5);
  }
}
```

**`src/app/features/dashboard/dashboard.component.html`**

```html
<div class="dashboard-container">
  <h1>Dashboard</h1>

  <div class="cards-grid">
    <mat-card>
      <mat-card-header>
        <mat-card-title>Recent Backtests</mat-card-title>
      </mat-card-header>
      <mat-card-content>
        <table mat-table [dataSource]="recentBacktests$ | async" class="mat-elevation-z0">

          <!-- Strategy Column -->
          <ng-container matColumnDef="strategy">
            <th mat-header-cell *matHeaderCellDef> Strategy </th>
            <td mat-cell *matCellDef="let b"> {{ b.strategy_name || b.strategy }} </td>
          </ng-container>

          <!-- Asset Column -->
          <ng-container matColumnDef="asset">
            <th mat-header-cell *matHeaderCellDef> Asset </th>
            <td mat-cell *matCellDef="let b"> {{ b.asset }} </td>
          </ng-container>

          <!-- Return Column -->
          <ng-container matColumnDef="return">
            <th mat-header-cell *matHeaderCellDef> Return </th>
            <td mat-cell *matCellDef="let b">
              <span [style.color]="(b.metrics?.total_return || 0) >= 0 ? 'green' : 'red'">
                {{ b.metrics?.total_return | percent:'1.2-2' }}
              </span>
            </td>
          </ng-container>

          <tr mat-header-row *matHeaderRowDef="['strategy', 'asset', 'return']"></tr>
          <tr mat-row *matRowDef="let row; columns: ['strategy', 'asset', 'return'];"></tr>
        </table>
      </mat-card-content>
    </mat-card>
  </div>
</div>
```

---

## Charts & Visual Enhancements

We utilize `ng2-charts` (a wrapper for Chart.js) to render price series and equity curves.

### Asset Detail with Price Chart

**`src/app/features/assets/asset-detail/asset-detail.component.ts`**

```typescript
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { AssetsService } from '../../../core/services/assets.service';
import { Observable, map } from 'rxjs';
import { ChartConfiguration, ChartOptions } from 'chart.js';

@Component({
  selector: 'app-asset-detail',
  templateUrl: './asset-detail.component.html'
})
export class AssetDetailComponent implements OnInit {
  symbol: string = '';
  chartData$!: Observable<ChartConfiguration<'line'>['data']>;
  chartOptions: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: false,
    elements: { line: { tension: 0.1 } } // No interpolation
  };

  constructor(
    private route: ActivatedRoute,
    private assetsService: AssetsService
  ) {}

  ngOnInit(): void {
    this.symbol = this.route.snapshot.paramMap.get('symbol') || '';

    // Transform API PriceSeries (OHLCV) to Chart.js format
    this.chartData$ = this.assetsService.getPriceSeries(this.symbol).pipe(
      map(series => ({
        labels: series.map(p => new Date(p.timestamp).toLocaleDateString()),
        datasets: [
          {
            data: series.map(p => p.close),
            label: `${this.symbol} Price`,
            borderColor: 'blue',
            backgroundColor: 'rgba(0,0,255,0.1)',
            fill: true
          }
        ]
      }))
    );
  }
}
```

**`src/app/features/assets/asset-detail/asset-detail.component.html`**

```html
<div class="asset-detail-container" *ngIf="chartData$ | async as chartData">
  <h2>{{ symbol }} Performance</h2>
  <div style="height: 400px;">
    <canvas baseChart
      [type]="'line'"
      [data]="chartData"
      [options]="chartOptions"
      [legend]="true">
    </canvas>
  </div>
</div>
```

---

## Future Extensibility

This architecture is designed for growth:

1.  **Shared Models:** The TypeScript interfaces in `shared/models` mirror the backend Django models. These can be moved to a shared library (npm package) if multiple frontends (e.g., mobile, admin) are developed.
2.  **Generic Services:** The `ApiService` pattern allows swapping the HTTP client or adding global error handling/caching strategies without modifying components.
3.  **Modular Features:** New capabilities like "Automations" or "Portfolio Management" can be added as new lazy-loaded feature modules (`loadChildren`) without bloating the initial bundle size.
4.  **Component Library:** As the UI grows, common patterns (e.g., "MetricCard", "PriceChart") can be extracted into the `SharedModule` to ensure consistency across the application.
