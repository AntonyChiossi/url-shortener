/**
 * @file auth.service.ts
 * @author Antony Chiossi
 */

import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { catchError, map } from 'rxjs/operators';
import { Observable, BehaviorSubject, throwError } from 'rxjs';
import { ToastrService } from 'ngx-toastr';
import { tap } from 'rxjs/operators';
import { environment } from '../../environments/environment';

interface LoginResponse {
  access: string;
  refresh: string;
}

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private accessToken$ = new BehaviorSubject<string | null>('');
  private authenticatedSubjec$ = new BehaviorSubject<boolean>(false);
  private baseUrl = environment.apiserver;
  private accessToken: string | null = '';
  constructor(private http: HttpClient, private toastService: ToastrService) {
    const cached = this.getAccessToken();
    console.log({ cached });
    this.accessToken$.next(cached as string);
    this.authenticatedSubjec$.next(!!cached);
  }

  register(email: string, password: string): Observable<any> {
    const body = { email: email, password: password };
    return this.http
      .post<any>(`${this.baseUrl}/api/register`, body)
      .pipe(catchError(this.handleError.bind(this)));
  }

  login(email: string, password: string): Observable<LoginResponse> {
    return this.http
      .post<LoginResponse>(`${this.baseUrl}/api/login`, { email, password })
      .pipe(catchError(this.handleError.bind(this)))
      .pipe(tap((response) => this.saveToken(response.access)));
  }

  logout() {
    this.accessToken = null;
    this.saveToken(null);
  }

  refreshToken(): void {
    const refresh = localStorage.getItem('refreshToken');
    this.http
      .post<LoginResponse>('/api/token/refresh/', { refresh })
      .pipe(catchError(this.handleError.bind(this)))
      .pipe(tap((response) => this.saveToken(response.access)));
  }

  private saveToken(token: string | null): void {
    this.accessToken = token;
    // Not best place i know :)
    if (!token) {
      localStorage.removeItem('accessToken');
    } else {
      localStorage.setItem('accessToken', token as string);
    }
    this.accessToken$.next(token);
    this.authenticatedSubjec$.next(!!token);
  }

  getAccessToken(): string | null {
    return this.accessToken || localStorage.getItem('accessToken');
  }

  isLoggedIn(): boolean {
    const token = this.getAccessToken();
    return token !== null;
  }

  getTokenSubject(): BehaviorSubject<string | null> {
    return this.accessToken$;
  }

  isAuthenticatedSubject(): BehaviorSubject<boolean> {
    return this.authenticatedSubjec$;
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
