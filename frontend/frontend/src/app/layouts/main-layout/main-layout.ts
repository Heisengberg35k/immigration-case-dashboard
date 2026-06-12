import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, RouterOutlet } from '@angular/router';

import { AuthService } from '../../core/services/auth';

@Component({
  selector: 'app-main-layout',
  imports: [CommonModule, RouterOutlet, RouterLink],
  templateUrl: './main-layout.html',
  styleUrl: './main-layout.css'
})
export class MainLayoutComponent {
  user: any;
  sidebarCollapsed = false;

  constructor(private authService: AuthService) {
    this.user = this.authService.getUser();
  }

  logout(): void {
    this.authService.logout();
  }

  toggleSidebar(): void {
    this.sidebarCollapsed = !this.sidebarCollapsed;
  }

  canViewAuditLog(): boolean {
    return this.authService.hasAnyRole(['admin', 'solicitor']);
  }

  canManageUsers(): boolean {
    return this.authService.hasAnyRole(['admin']);
  }
}
