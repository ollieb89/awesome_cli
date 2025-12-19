import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { DashboardComponent } from './features/dashboard/dashboard.component';
import { AssetsListComponent } from './features/assets/assets-list/assets-list.component';
import { AssetDetailComponent } from './features/assets/asset-detail/asset-detail.component';
import { StrategiesListComponent } from './features/strategies/strategies-list/strategies-list.component';
import { StrategyDetailComponent } from './features/strategies/strategy-detail/strategy-detail.component';
import { BacktestsListComponent } from './features/backtests/backtests-list/backtests-list.component';
import { BacktestDetailComponent } from './features/backtests/backtest-detail/backtest-detail.component';

const routes: Routes = [
  { path: '', component: DashboardComponent },
  { path: 'assets', component: AssetsListComponent },
  { path: 'assets/:symbol', component: AssetDetailComponent },
  { path: 'strategies', component: StrategiesListComponent },
  { path: 'strategies/:id', component: StrategyDetailComponent },
  { path: 'backtests', component: BacktestsListComponent },
  { path: 'backtests/:id', component: BacktestDetailComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
