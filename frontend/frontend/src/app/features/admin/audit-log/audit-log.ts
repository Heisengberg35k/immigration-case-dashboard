import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';

import { ApiService } from '../../../core/services/api';

@Component({
  selector: 'app-audit-log',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './audit-log.html',
  styleUrl: './audit-log.css'
})
export class AuditLog implements OnInit {
  loading = true;
  errorMessage = '';
  logs: any[] = [];

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    this.loadAuditLogs();
  }

  loadAuditLogs(): void {
    this.loading = true;
    this.errorMessage = '';

    this.apiService.getAuditLogs().subscribe({
      next: (data: any) => {
        this.logs = Array.isArray(data?.audit_logs)
          ? data.audit_logs
          : [];
        this.loading = false;
      },
      error: (error: any) => {
        console.error('Audit log loading error:', error);
        this.errorMessage =
          error?.error?.message ||
          'Could not load audit log.';
        this.loading = false;
      }
    });
  }
}
