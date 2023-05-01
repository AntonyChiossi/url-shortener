/**
 * @file url.service.ts
 * @author Antony Chiossi
 */

import { Injectable } from '@angular/core';
import {
  HttpClient,
  HttpErrorResponse,
  HttpHeaders,
} from '@angular/common/http';
import { BehaviorSubject, Observable, Subject, throwError } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';
import { Url, UrlStats, UserUrls } from '../models/common';
import { DateTime } from 'luxon';
import { ToastrService } from 'ngx-toastr';
import { environment } from '../../environments/environment';

export interface CreateUrlResponse {
  short_id: string;
}

@Injectable({
  providedIn: 'root',
})
export class UrlService {
  private readonly BASE_URL = environment.apiserver;
  private urlCreation$: BehaviorSubject<CreateUrlResponse | null> =
    new BehaviorSubject<CreateUrlResponse | null>(null);
  private userUrls: BehaviorSubject<UserUrls> = new BehaviorSubject<UserUrls>({
    urls: [],
  });
  private urlStats: Record<string, BehaviorSubject<UrlStats | null>> = {};

  constructor(private http: HttpClient, private toastService: ToastrService) {}

  private fullUrl(shortId: string) {
    return `${this.BASE_URL}/${shortId}`;
  }

  getUrlCreationSubject() {
    return this.urlCreation$;
  }

  createUrl(longUrl: string, expireDate?: Date): Observable<CreateUrlResponse> {
    const headers = this.getAuthHeaders();
    const body: any = { long_url: longUrl };
    if (expireDate) {
      body.expires_at = DateTime.fromJSDate(expireDate).toUTC().toISO();
    }

    console.log({ body });

    if (headers) {
      return this.http
        .post<CreateUrlResponse>(`${this.BASE_URL}/api/url`, body, { headers })
        .pipe(catchError(this.handleError.bind(this)))
        .pipe(
          tap((res: CreateUrlResponse) => {
            console.log({ creation: res });
            res.short_id = this.fullUrl(res.short_id);
            this.urlCreation$.next(res);
          })
        );
    }
    return this.http
      .post<CreateUrlResponse>(`${this.BASE_URL}/api/url`, body)
      .pipe(catchError(this.handleError.bind(this)))
      .pipe(
        tap((res: CreateUrlResponse) => {
          console.log({ creation: res });
          res.short_id = this.fullUrl(res.short_id);
          this.urlCreation$.next(res);
        })
      );
  }

  getUserUrls(): Observable<UserUrls> {
    const headers = this.getAuthHeaders();

    return this.http
      .get<UserUrls>(`${this.BASE_URL}/api/url`, headers ? { headers } : {})
      .pipe(
        map((res: UserUrls) => {
          console.log({ url: res });
          return {
            ...res,
            urls: res.urls.map((u) => ({
              ...u,
              short_url: `${this.BASE_URL}/${u.short_id}`,
            })),
          };
        })
      )
      .pipe(
        tap((res: UserUrls) => {
          console.log({ url: res });
          this.userUrls.next({
            ...res,
            urls: res.urls.map((u) => ({
              ...u,
              short_url: `${this.BASE_URL}/${u.short_id}`,
            })),
          });
        })
      );
  }

  getUrlStats(shortId: string): Observable<UrlStats> {
    const headers = this.getAuthHeaders();
    if (!this.urlStats['shortId']) {
      this.urlStats['shortId'] = new BehaviorSubject<UrlStats | null>(null);
    }
    return this.http
      .get<UrlStats>(`${this.BASE_URL}/${shortId}+`, headers ? { headers } : {})
      .pipe(
        tap((res: UrlStats) => {
          console.log({ urlStats: res });
          this.urlStats['shortId'].next(res);
        })
      );
  }

  private getAuthHeaders(): HttpHeaders | null {
    const accessToken = localStorage.getItem('accessToken');
    if (!accessToken) {
      return null;
    }
    return new HttpHeaders({ Authorization: `Bearer ${accessToken}` });
  }

  private handleError(error: HttpErrorResponse) {
    if (error.status === 0) {
      // A client-side or network error occurred. Handle it accordingly.
      console.error('An error occurred:', error.error);
    } else {
      // The backend returned an unsuccessful response code.
      // The response body may contain clues as to what went wrong.
      console.error(
        `Backend returned code ${error.status}, body was: `,
        error.error
      );
      let errMessage = JSON.stringify(error.error);
      if (Array.isArray(error.error.non_field_errors)) {
        errMessage = error.error.non_field_errors.join('; ');
      }
      this.toastService.error(errMessage, 'Error', { timeOut: 10000 });
    }
    // Return an observable with a user-facing error message.
    return throwError(
      () => new Error('Something bad happened; please try again later.')
    );
  }
}
