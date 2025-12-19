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
    elements: { line: { tension: 0.1 } }
  };

  constructor(
    private route: ActivatedRoute,
    private assetsService: AssetsService
  ) {}

  ngOnInit(): void {
    this.symbol = this.route.snapshot.paramMap.get('symbol') || '';

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
