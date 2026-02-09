import { Routes } from '@angular/router';
import { AdminComponent } from './admin.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { RunsComponent } from './runs/runs.component';

export const ADMIN_ROUTES: Routes = [
    {
        path: '',
        component: AdminComponent,
        children: [
            { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
            { path: 'dashboard', component: DashboardComponent },
            { path: 'runs', component: RunsComponent }
        ]
    }
];
