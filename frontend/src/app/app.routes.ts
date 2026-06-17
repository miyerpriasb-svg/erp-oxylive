import { Routes } from '@angular/router';
import { authGuard } from './core/auth/auth.guard';

export const routes: Routes = [
  {
    path: '',
    pathMatch: 'full',
    loadComponent: () => import('./features/login/login.component').then((m) => m.LoginComponent),
  },
  {
    path: 'migracion',
    canActivate: [authGuard],
    loadComponent: () => import('./features/migration/migration.component').then((m) => m.MigrationComponent),
  },
  { path: 'login', redirectTo: '', pathMatch: 'full' },
  { path: '**', redirectTo: '' },
];
