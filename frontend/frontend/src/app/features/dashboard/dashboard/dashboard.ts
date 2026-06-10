import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { ApiService } from '../../../core/services/api';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css'
})
export class Dashboard implements OnInit {
  loading = true;
  errorMessage = '';

  summary = {
    active_cases: 0,
    waiting_documents: 0,
    waiting_client_answers: 0,
    solicitor_review_pending: 0,
    upload_deadlines_this_week: 0,
    due_deadlines_today: 0,
    overdue_deadlines: 0,
    deadline_alerts: [] as any[],
    appointments_this_week: 0,
    payments_overdue: 0,
    visa_renewals_due_soon: 0
  };

  constructor(
    private apiService: ApiService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadDashboardSummary();
  }

  loadDashboardSummary(): void {
    this.loading = true;
    this.errorMessage = '';

    this.apiService.getDashboardSummary().subscribe({
      next: (data) => {
        this.summary = data;
        this.loading = false;
      },
      error: (error) => {
        console.error('Dashboard summary error:', error);
        this.errorMessage = 'Could not load dashboard summary.';
        this.loading = false;
      }
    });
  }

  hasDeadlineAlerts(): boolean {
    return Array.isArray(this.summary.deadline_alerts)
      && this.summary.deadline_alerts.length > 0;
  }

  openDeadlineAlert(alert: any): void {
    if (!alert.client_id) {
      return;
    }

    this.router.navigate(['/clients', alert.client_id]);
  }
}
