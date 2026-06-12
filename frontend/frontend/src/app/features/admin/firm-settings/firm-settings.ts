import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { ApiService } from '../../../core/services/api';
import { AuthService } from '../../../core/services/auth';

@Component({
  selector: 'app-firm-settings',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './firm-settings.html',
  styleUrl: './firm-settings.css'
})
export class FirmSettings implements OnInit {
  loading = true;
  saving = false;
  errorMessage = '';
  successMessage = '';
  firm: any = null;
  firmName = '';

  constructor(
    private apiService: ApiService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.loadFirm();
  }

  loadFirm(): void {
    this.loading = true;
    this.errorMessage = '';
    this.successMessage = '';

    this.apiService.getFirm().subscribe({
      next: (data: any) => {
        this.firm = data?.firm || null;
        this.firmName = this.firm?.name || '';
        this.loading = false;
      },
      error: (error: any) => {
        console.error('Firm loading error:', error);
        this.errorMessage =
          error?.error?.message ||
          'Could not load firm settings.';
        this.loading = false;
      }
    });
  }

  saveFirm(): void {
    if (!this.canManageFirm()) {
      return;
    }

    this.errorMessage = '';
    this.successMessage = '';
    this.saving = true;

    this.apiService.updateFirm({
      name: this.firmName
    }).subscribe({
      next: (data: any) => {
        this.firm = data?.firm || this.firm;
        this.firmName = this.firm?.name || this.firmName;
        this.successMessage = 'Firm settings updated successfully.';
        this.saving = false;
      },
      error: (error: any) => {
        console.error('Firm update error:', error);
        this.errorMessage =
          error?.error?.message ||
          'Could not update firm settings.';
        this.saving = false;
      }
    });
  }

  canManageFirm(): boolean {
    return this.authService.hasAnyRole(['admin']);
  }
}
