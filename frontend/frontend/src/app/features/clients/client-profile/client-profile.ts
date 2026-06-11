import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';

import { CaseWorkflowSections } from './case-workflow-sections/case-workflow-sections';
import { ApiService } from '../../../core/services/api';
import { AuthService } from '../../../core/services/auth';

@Component({
  selector: 'app-client-profile',
  standalone: true,
  imports: [
    CommonModule,
    CaseWorkflowSections
  ],
  templateUrl: './client-profile.html',
  styleUrl: './client-profile.css'
})
export class ClientProfile implements OnInit {
  clientId = 0;
  caseId = 0;

  profile: any = null;

  loading = true;
  deleting = false;

  errorMessage = '';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private apiService: ApiService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.clientId = Number(
      this.route.snapshot.paramMap.get('id')
    );

    if (!this.clientId) {
      this.errorMessage = 'No client ID found.';
      this.loading = false;
      return;
    }

    this.loadClient();
  }

  loadClient(): void {
    this.loading = true;
    this.errorMessage = '';

    this.apiService.getClient(this.clientId).subscribe({
      next: (data: any) => {
        const client = data.client ? data.client : data;

        const caseId =
          client.case_id ||
          client.latest_case_id ||
          client.case?.id ||
          client.cases?.[0]?.id;

        if (!caseId) {
          this.errorMessage =
            'Client loaded, but no linked case ID was found.';

          this.loading = false;
          return;
        }

        this.caseId = Number(caseId);
        this.loadProfile();
      },
      error: (error: any) => {
        console.error(
          'Single client loading error:',
          error
        );

        this.errorMessage =
          error?.error?.message ||
          'Could not load client details.';

        this.loading = false;
      }
    });
  }

  loadProfile(): void {
    this.apiService
      .getCaseFullProfile(this.caseId)
      .subscribe({
        next: (data: any) => {
          this.profile = data;
          this.loading = false;
        },
        error: (error: any) => {
          console.error(
            'Client profile loading error:',
            error
          );

          this.errorMessage =
            error?.error?.message ||
            'Could not load client profile.';

          this.loading = false;
        }
      });
  }
  editClient(): void {
    this.router.navigate([
      '/clients',
      this.clientId,
      'edit'
    ]);
  }

  deleteClient(): void {
    if (!this.canDeleteClient()) {
      this.errorMessage =
        'Only admins and solicitors can delete clients.';
      return;
    }

    const clientName =
      this.profile?.client?.full_name ||
      'this client';

    const confirmed = window.confirm(
      `Delete ${clientName}? This will also delete the linked case and related records.`
    );

    if (!confirmed) {
      return;
    }

    this.deleting = true;
    this.errorMessage = '';

    this.apiService
      .deleteClient(this.clientId)
      .subscribe({
        next: () => {
          this.router.navigate(['/clients']);
        },
        error: (error: any) => {
          console.error(
            'Delete client error:',
            error
          );

          this.errorMessage =
            error?.error?.message ||
            'Could not delete the client.';

          this.deleting = false;
        }
      });
  }

  goBack(): void {
    this.router.navigate(['/clients']);
  }

  canDeleteClient(): boolean {
    return this.authService.hasAnyRole([
      'admin',
      'solicitor'
    ]);
  }
}
