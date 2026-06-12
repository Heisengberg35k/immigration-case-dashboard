import { Routes } from '@angular/router';

import { LoginComponent } from './features/auth/login/login';
import { Dashboard } from './features/dashboard/dashboard/dashboard';
import { ClientList } from './features/clients/client-list/client-list';
import { ClientCreate } from './features/clients/client-create/client-create';
import { ClientEdit } from './features/clients/client-edit/client-edit';
import { ClientProfile } from './features/clients/client-profile/client-profile';
import { Reports } from './features/reports/reports';
import { AuditLog } from './features/admin/audit-log/audit-log';
import { Users } from './features/admin/users/users';
import { FirmSettings } from './features/admin/firm-settings/firm-settings';
import { MainLayoutComponent } from './layouts/main-layout/main-layout';
import { authGuard } from './core/guards/auth-guard';

export const routes: Routes = [
  {
    path: 'login',
    component: LoginComponent
  },
  {
    path: '',
    component: MainLayoutComponent,
    canActivate: [authGuard],
    children: [
      {
        path: 'dashboard',
        component: Dashboard
      },
      {
        path: 'clients',
        component: ClientList
      },
      {
        path: 'clients/add',
        component: ClientCreate
      },
      {
        path: 'clients/:id/edit',
        component: ClientEdit
      },
      {
        path: 'clients/:id',
        component: ClientProfile
      },
      {
        path: 'reports',
        component: Reports
      },
      {
        path: 'audit-log',
        component: AuditLog,
        canActivate: [authGuard],
        data: {
          roles: ['admin', 'solicitor']
        }
      },
      {
        path: 'users',
        component: Users,
        canActivate: [authGuard],
        data: {
          roles: ['admin']
        }
      },
      {
        path: 'firm-settings',
        component: FirmSettings,
        canActivate: [authGuard],
        data: {
          roles: ['admin', 'solicitor', 'staff']
        }
      },
      {
        path: '',
        redirectTo: 'dashboard',
        pathMatch: 'full'
      }
    ]
  },
  {
    path: '**',
    redirectTo: 'login'
  }
];
