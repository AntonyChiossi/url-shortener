import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { LoginComponent } from './login/login.component';
import {
  NgbDatepickerModule,
  NgbModalModule,
  NgbModule,
} from '@ng-bootstrap/ng-bootstrap';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { AuthService } from './services/auth.service';
import { HttpClientModule } from '@angular/common/http';
import { ToastrModule } from 'ngx-toastr';
import { NgApexchartsModule } from 'ng-apexcharts';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { UrlService } from './services/url.service';
import { UrlStatsComponent } from './url-stats/url-stats.component';
import { RegistrationComponent } from './registration/registration.component';

const IMPORTS = [
  BrowserModule,
  HttpClientModule,
  AppRoutingModule,
  FormsModule,
  ReactiveFormsModule,
  BrowserAnimationsModule,
  NgbModalModule,
  NgbDatepickerModule,
  NgbModule,
  ToastrModule.forRoot({
    positionClass: 'toast-bottom-right',
  }),
  NgApexchartsModule,
];

@NgModule({
  declarations: [AppComponent, LoginComponent, UrlStatsComponent, RegistrationComponent],
  imports: [...IMPORTS],
  providers: [AuthService, UrlService],
  bootstrap: [AppComponent],
})
export class AppModule {}
