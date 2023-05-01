import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { UrlStatsComponent } from './url-stats/url-stats.component';

const routes: Routes = [{ path: 'stats', component: UrlStatsComponent }];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
