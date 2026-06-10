import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

import { ApiService } from '../../../core/services/api';

@Component({
  selector: 'app-client-create',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule
  ],
  templateUrl: './client-create.html',
  styleUrl: './client-create.css'
})
export class ClientCreate {
  loading = false;
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
    case_status: 'New Consultation',
    assigned_lawyer: '',
    assigned_staff: '',
    home_office_reference: '',
    main_deadline: '',
    priority: 'Normal',
    file_location: '',
    solicitor_review_status: 'Not Reviewed'
  };

  constructor(
    private apiService: ApiService,
    private router: Router
  ) {}

  createClient(): void {
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

    this.loading = true;

    this.apiService.createClient(this.clientData).subscribe({
      next: (response: any) => {
        console.log('Client created:', response);

        this.loading = false;
        this.successMessage = 'Client and case created successfully.';

        setTimeout(() => {
          this.router.navigate(['/clients']);
        }, 800);
      },
      error: (error: any) => {
        console.error('Create client error:', error);

        this.loading = false;

        this.errorMessage =
          error?.error?.message ||
          'Could not create the client. Please try again.';
      }
    });
  }

  cancel(): void {
    this.router.navigate(['/clients']);
  }
}