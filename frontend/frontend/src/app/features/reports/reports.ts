import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';

import { ApiService } from '../../core/services/api';

@Component({
  selector: 'app-reports',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './reports.html',
  styleUrl: './reports.css'
})
export class Reports implements OnInit {
  loading = true;
  errorMessage = '';
  report: any = null;

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    this.loadReports();
  }

  loadReports(): void {
    this.loading = true;
    this.errorMessage = '';

    this.apiService.getReportsOverview().subscribe({
      next: (data: any) => {
        this.report = data;
        this.loading = false;
      },
      error: (error: any) => {
        console.error('Reports loading error:', error);
        this.errorMessage =
          error?.error?.message ||
          'Could not load reports.';
        this.loading = false;
      }
    });
  }
}
