import { Component, OnInit } from '@angular/core';
import { BacktestsService } from '../../core/services/backtests.service';
import { StrategiesService } from '../../core/services/strategies.service';
import { AssetsService } from '../../core/services/assets.service';
import { Observable } from 'rxjs';
import { Backtest } from '../../shared/models/backtest.model';
import { Strategy } from '../../shared/models/strategy.model';
import { Asset } from '../../shared/models/asset.model';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  backtests$!: Observable<Backtest[]>;
  strategies$!: Observable<Strategy[]>;
  assets$!: Observable<Asset[]>;

  constructor(
    private backtestsService: BacktestsService,
    private strategiesService: StrategiesService,
    private assetsService: AssetsService
  ) {}

  ngOnInit(): void {
    this.backtests$ = this.backtestsService.getBacktests(5);
    this.strategies$ = this.strategiesService.getStrategies(5);
    this.assets$ = this.assetsService.getAssets(5);
  }
}
