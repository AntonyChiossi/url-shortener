import { Component, OnDestroy, OnInit } from '@angular/core';
import { UrlService } from './services/url.service';
import { Subscription, interval } from 'rxjs';
import { Clipboard } from '@angular/cdk/clipboard';
import { AuthService } from './services/auth.service';
import { Url, UrlInUserUrls, UserUrls } from './models/common';
import {
  NgbDateStruct,
  NgbTimeStruct,
  NgbTimepickerConfig,
} from '@ng-bootstrap/ng-bootstrap';
import { DateTime } from 'luxon';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
  providers: [NgbTimepickerConfig],
})
export class AppComponent implements OnInit, OnDestroy {
  public title = 'shortener';
  public longUrl: string | null = null;
  public shortId: string | null = null;
  public copyDisabled = false;
  public authenticated = false;
  public expire: NgbDateStruct;
  public expireTime: NgbTimeStruct;
  public userUrls: UrlInUserUrls[] = [];
  public collapsed: Record<string, boolean> = {};
  private subs: Subscription[] = [];

  public constructor(
    private authService: AuthService,
    private urlService: UrlService,
    private clipboard: Clipboard,
    private config: NgbTimepickerConfig
  ) {
    config.seconds = false;
    config.spinners = false;
    this.expireTime = {
      hour: DateTime.now().get('hour'),
      minute: DateTime.now().get('minute') + 1,
      second: 0,
    };
  }

  ngOnInit(): void {
    this.subs.push(
      this.authService
        .isAuthenticatedSubject()
        .subscribe((authenticated: boolean) => {
          this.authenticated = authenticated;
          this.refreshUserUrls();
        }),
      this.urlService.getUrlCreationSubject().subscribe((created) => {
        console.log({ created });
        if (!created) {
          return;
        }
        this.shortId = created.short_id;
        this.refreshUserUrls();
      })
    );
  }

  private refreshUserUrls() {
    if (!this.authenticated) {
      return;
    }
    this.urlService.getUserUrls().subscribe((data: UserUrls) => {
      this.userUrls = data.urls || [];
    });
  }

  public logout() {
    this.authService.logout();
  }

  public createUrl() {
    let expire;
    if (this.expire) {
      expire = DateTime.fromObject({
        day: this.expire.day,
        month: this.expire.month,
        year: this.expire.year,
        hour: this.expireTime.hour || 0,
        minute: this.expireTime.minute || 0,
        second: 0,
      }).toJSDate();
    }
    this.urlService.createUrl(this.longUrl as string, expire).subscribe();
  }

  public copy() {
    this.copyDisabled = true;
    this.clipboard.copy(this.shortId as string);
    this.subs.push(
      interval(3 * 1000).subscribe(() => {
        this.copyDisabled = false;
      })
    );
  }

  public ngOnDestroy(): void {
    this.subs.forEach((e) => e.unsubscribe());
  }
}
