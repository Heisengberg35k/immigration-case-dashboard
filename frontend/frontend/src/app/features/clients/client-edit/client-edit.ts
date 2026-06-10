import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';

import { ApiService } from '../../../core/services/api';

@Component({
  selector: 'app-client-edit',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule
  ],
  templateUrl: './client-edit.html',
  styleUrl: './client-edit.css'
})
export class ClientEdit implements OnInit {
  clientId = 0;

  pageLoading = true;
  saving = false;

  errorMessage = '';
  successMessage = '';

  clientData = {
    full_name: '',
    date_of_birth: '',
    phone: '',
    email: '',
    address: '',
    preferred_contact_method: '',
    whatsapp_number: '',

    application_type: '',
    case_status: '',
    assigned_lawyer: '',
    assigned_staff: '',
    home_office_reference: '',
    main_deadline: '',
    priority: '',
    file_location: '',
    solicitor_review_status: ''
  };

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private apiService: ApiService
  ) {}

  ngOnInit(): void {
    this.clientId = Number(
      this.route.snapshot.paramMap.get('id')
    );

    if (!this.clientId) {
      this.errorMessage = 'Invalid client ID.';
      this.pageLoading = false;
      return;
    }

    this.loadClient();
  }

  loadClient(): void {
    this.pageLoading = true;
    this.errorMessage = '';

    this.apiService.getClient(this.clientId).subscribe({
      next: (data: any) => {
        console.log('Edit client response:', data);

        const client = data.client ? data.client : data;

        this.clientData = {
          full_name: client.full_name || '',
          date_of_birth: client.date_of_birth || '',
          phone: client.phone || '',
          email: client.email || '',
          address: client.address || '',
          preferred_contact_method:
            client.preferred_contact_method || '',
          whatsapp_number:
            client.whatsapp_number || '',

          application_type:
            client.application_type ||
            client.case_type ||
            '',

          case_status:
            client.case_status ||
            client.status ||
            'New Consultation',

          assigned_lawyer:
            client.assigned_lawyer || '',

          assigned_staff:
            client.assigned_staff || '',

          home_office_reference:
            client.home_office_reference || '',

          main_deadline:
            client.main_deadline || '',

          priority:
            client.priority || 'Normal',

          file_location:
            client.file_location || '',

          solicitor_review_status:
            client.solicitor_review_status ||
            'Not Reviewed'
        };

        this.pageLoading = false;
      },
      error: (error: any) => {
        console.error('Load client error:', error);

        this.errorMessage =
          error?.error?.message ||
          'Could not load client details.';

        this.pageLoading = false;
      }
    });
  }

  saveClient(): void {
    this.errorMessage = '';
    this.successMessage = '';

    if (!this.clientData.full_name.trim()) {
      this.errorMessage = 'Client full name is required.';
      return;
    }

    if (!this.clientData.application_type.trim()) {
      this.errorMessage = 'Application type is required.';
      return;
    }

    this.saving = true;

    this.apiService
      .updateClient(this.clientId, this.clientData)
      .subscribe({
        next: (response: any) => {
          console.log('Client updated:', response);

          this.saving = false;
          this.successMessage =
            'Client and case updated successfully.';

          setTimeout(() => {
            this.router.navigate([
              '/clients',
              this.clientId
            ]);
          }, 800);
        },
        error: (error: any) => {
          console.error('Update client error:', error);

          this.saving = false;

          this.errorMessage =
            error?.error?.message ||
            'Could not update the client.';
        }
      });
  }

  cancel(): void {
    this.router.navigate([
      '/clients',
      this.clientId
    ]);
  }
}