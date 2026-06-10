import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';

import { ApiService } from '../../../core/services/api';

@Component({
  selector: 'app-client-profile',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule
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

  documentFormVisible = false;
  documentSaving = false;
  editingDocumentId: number | null = null;

  errorMessage = '';
  documentErrorMessage = '';
  documentSuccessMessage = '';

  documentData = this.getEmptyDocumentData();

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
      this.errorMessage = 'No client ID found.';
      this.loading = false;
      return;
    }

    this.loadClient();
  }

  getEmptyDocumentData() {
    return {
      document_name: '',
      required: true,
      status: 'Requested',
      source: '',
      file_name: '',
      file_location: '',
      received_date: '',
      checked_by: '',
      notes: ''
    };
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
          console.log(
            'Client full profile response:',
            data
          );

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

  showAddDocumentForm(): void {
    this.documentData = this.getEmptyDocumentData();
    this.editingDocumentId = null;
    this.documentErrorMessage = '';
    this.documentSuccessMessage = '';
    this.documentFormVisible = true;
  }

  editDocument(documentItem: any): void {
    this.editingDocumentId = documentItem.id;

    this.documentData = {
      document_name: documentItem.document_name || '',
      required: documentItem.required ?? true,
      status: documentItem.status || 'Requested',
      source: documentItem.source || '',
      file_name: documentItem.file_name || '',
      file_location: documentItem.file_location || '',
      received_date: documentItem.received_date || '',
      checked_by: documentItem.checked_by || '',
      notes: documentItem.notes || ''
    };

    this.documentErrorMessage = '';
    this.documentSuccessMessage = '';
    this.documentFormVisible = true;

    setTimeout(() => {
      window.document
        .getElementById('document-form')
        ?.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
    });
  }

  saveDocument(): void {
    this.documentErrorMessage = '';
    this.documentSuccessMessage = '';

    if (!this.documentData.document_name.trim()) {
      this.documentErrorMessage =
        'Document name is required.';
      return;
    }

    if (!this.caseId) {
      this.documentErrorMessage =
        'No linked case was found.';
      return;
    }

    this.documentSaving = true;

    if (this.editingDocumentId) {
      this.apiService
        .updateDocument(
          this.editingDocumentId,
          this.documentData
        )
        .subscribe({
          next: () => {
            this.documentSaving = false;
            this.documentSuccessMessage =
              'Document updated successfully.';

            this.loadProfile();

            setTimeout(() => {
              this.closeDocumentForm();
            }, 700);
          },
          error: (error: any) => {
            console.error(
              'Update document error:',
              error
            );

            this.documentSaving = false;

            this.documentErrorMessage =
              error?.error?.message ||
              'Could not update the document.';
          }
        });

      return;
    }

    this.apiService
      .createDocument(
        this.caseId,
        this.documentData
      )
      .subscribe({
        next: () => {
          this.documentSaving = false;
          this.documentSuccessMessage =
            'Document added successfully.';

          this.loadProfile();

          setTimeout(() => {
            this.closeDocumentForm();
          }, 700);
        },
        error: (error: any) => {
          console.error(
            'Create document error:',
            error
          );

          this.documentSaving = false;

          this.documentErrorMessage =
            error?.error?.message ||
            'Could not add the document.';
        }
      });
  }

  deleteDocument(documentItem: any): void {
    const documentName =
      documentItem.document_name ||
      'this document';

    const confirmed = window.confirm(
      `Delete "${documentName}"?`
    );

    if (!confirmed) {
      return;
    }

    this.documentErrorMessage = '';
    this.documentSuccessMessage = '';

    this.apiService
      .deleteDocument(documentItem.id)
      .subscribe({
        next: () => {
          this.documentSuccessMessage =
            'Document deleted successfully.';

          this.loadProfile();
        },
        error: (error: any) => {
          console.error(
            'Delete document error:',
            error
          );

          this.documentErrorMessage =
            error?.error?.message ||
            'Could not delete the document.';
        }
      });
  }

  closeDocumentForm(): void {
    this.documentFormVisible = false;
    this.editingDocumentId = null;
    this.documentData = this.getEmptyDocumentData();
    this.documentErrorMessage = '';
    this.documentSuccessMessage = '';
  }

  editClient(): void {
    this.router.navigate([
      '/clients',
      this.clientId,
      'edit'
    ]);
  }

  deleteClient(): void {
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
}