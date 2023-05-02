import {
  Component,
  Input,
  OnChanges,
  OnInit,
  SimpleChanges,
} from '@angular/core';
import { DateTime } from 'luxon';
import { UrlService } from '../services/url.service';
import { Click, UrlStats } from '../models/common';

interface ClickStats {
  browserCounts: Record<string, number>;
  uniqueVisitors: number;
  totalClicks: number;
  clicksByDate: { date: string; count: number }[];
}

@Component({
  selector: 'app-url-stats',
  templateUrl: './url-stats.component.html',
  styleUrls: ['./url-stats.component.scss'],
})
export class UrlStatsComponent implements OnInit, OnChanges {
  @Input()
  public shortId: string;
  @Input()
  public show = false;
  public collapsed = true;
  public stats: ClickStats;
  public treeChartOptions: any;
  public lineChartOptions: any;
  public hasBrowsers = false;
  public loading = false;
  constructor(private urlService: UrlService) {}

  ngOnInit(): void {}

  ngOnChanges(changes: SimpleChanges): void {
    this.show = !!this.show;
    if (!this.shortId) {
      return;
    }
    this.collapsed = !this.show;
    if (this.show) {
      this.loading = true;
      this.urlService
        .getUrlStats(this.shortId)
        .subscribe((rawStats: UrlStats) => {
          this.stats = {
            ...this.extractClickStats(rawStats.clicks),
            totalClicks: rawStats.total_clicks,
          };

          this.hasBrowsers = Object.keys(this.stats.browserCounts).length > 0;
          this.treeChartOptions = {
            series: [
              {
                data: Object.entries(this.stats.browserCounts).map(
                  ([name, count]) => ({ x: name, y: count })
                ),
              },
            ],
            theme: {
              mode: 'dark',
              palette: 'palette10',
            },
            chart: {
              height: 350,
              type: 'treemap',
              background: 'transparent',
            },
            title: {
              text: 'Browsers',
            },
          };

          this.lineChartOptions = {
            series: [
              {
                name: 'Clicks',
                data: this.stats.clicksByDate.map((e) => e.count),
              },
            ],
            theme: {
              mode: 'dark',
              palette: 'palette5',
            },
            chart: {
              height: 350,
              type: 'line',
              zoom: {
                enabled: false,
              },
              background: 'transparent',
            },
            dataLabels: {
              enabled: false,
            },
            stroke: {
              curve: 'straight',
            },
            title: {
              text: 'Clicks By Day',
              align: 'left',
            },
            grid: {
              row: {
                colors: ['transparent'], // takes an array which will be repeated on columns
                opacity: 0.5,
              },
            },
            xaxis: {
              categories: this.stats.clicksByDate.map((e) => e.date),
            },
          };

          this.loading = false;
        });
    }
  }

  private extractClickStats(data: Click[]): ClickStats {
    const clicks: Click[] = data;

    const browserCounts: Record<string, number> = {};
    const uniqueVisitors: Set<string> = new Set();
    const clicksByDate: Record<string, number> = {};

    for (const click of clicks) {
      const dateLabel = DateTime.fromISO(click.date).toISODate() as string;
      if (!clicksByDate[dateLabel]) {
        clicksByDate[dateLabel] = 0;
      }
      clicksByDate[dateLabel] += 1;

      const browser = this.extractBrowser(click.user_agent);
      if (browser) {
        if (!browserCounts[browser]) {
          browserCounts[browser] = 0;
        }
        browserCounts[browser] += 1;
      }

      uniqueVisitors.add(click.ip_address);
    }

    return {
      browserCounts,
      uniqueVisitors: uniqueVisitors.size,
      totalClicks: 0,
      clicksByDate: Object.entries(clicksByDate)
        .map(([date, count]) => ({
          date,
          count,
        }))
        .sort((a, b) => (a.date > b.date ? 1 : -1)),
    };
  }

  private extractBrowser(userAgent: string): string | undefined {
    const match = userAgent.match(/(chrome|firefox|safari|opera|edge)/i);
    if (match) {
      return match[1].toLowerCase();
    }
    return 'unknown';
  }
}
