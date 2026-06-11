import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { CaseAppointmentsSection } from './case-appointments-section/case-appointments-section';
import { CaseDeadlinesSection } from './case-deadlines-section/case-deadlines-section';
import { CaseNotesSection } from './case-notes-section/case-notes-section';
import { CasePaymentsSection } from './case-payments-section/case-payments-section';
import { CaseQuestionnairesSection } from './case-questionnaires-section/case-questionnaires-section';
import { CaseVisaRemindersSection } from './case-visa-reminders-section/case-visa-reminders-section';
import { ApiService } from '../../../../core/services/api';

@Component({
  selector: 'app-case-workflow-sections',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    CaseAppointmentsSection,
    CaseDeadlinesSection,
    CaseNotesSection,
    CasePaymentsSection,
    CaseQuestionnairesSection,
    CaseVisaRemindersSection
  ],
  templateUrl: './case-workflow-sections.html'
})
export class CaseWorkflowSections {
  @Input() profile: any = null;
  @Input() caseId = 0;
  @Output() profileChanged = new EventEmitter<void>();

  documentFormVisible = false;
  documentSaving = false;
  documentDownloadingId: number | null = null;
  editingDocumentId: number | null = null;
  selectedDocumentFile: File | null = null;

  errorMessage = '';
  documentErrorMessage = '';
  documentSuccessMessage = '';
  documentData = this.getEmptyDocumentData();

  constructor(private apiService: ApiService) {}

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

  showAddDocumentForm(): void {
    this.documentData = this.getEmptyDocumentData();
    this.editingDocumentId = null;
    this.selectedDocumentFile = null;
    this.documentErrorMessage = '';
    this.documentSuccessMessage = '';
    this.documentFormVisible = true;
  }

  editDocument(documentItem: any): void {
    this.editingDocumentId = documentItem.id;
    this.selectedDocumentFile = null;

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

  onDocumentFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0] || null;

    this.selectedDocumentFile = file;
  }

  buildDocumentUploadFormData(): FormData {
    const formData = new FormData();

    formData.append('file', this.selectedDocumentFile as File);

    Object.entries(this.documentData).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        formData.append(key, String(value));
      }
    });

    return formData;
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

            this.profileChanged.emit();

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

    if (this.selectedDocumentFile) {
      this.apiService
        .uploadDocument(
          this.caseId,
          this.buildDocumentUploadFormData()
        )
        .subscribe({
          next: () => {
            this.documentSaving = false;
            this.documentSuccessMessage =
              'Document uploaded successfully.';

            this.profileChanged.emit();

            setTimeout(() => {
              this.closeDocumentForm();
            }, 700);
          },
          error: (error: any) => {
            console.error(
              'Upload document error:',
              error
            );

            this.documentSaving = false;

            this.documentErrorMessage =
              error?.error?.message ||
              'Could not upload the document.';
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

          this.profileChanged.emit();

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

  viewDocument(documentItem: any): void {
    this.openDocumentBlob(documentItem, true);
  }

  downloadDocument(documentItem: any): void {
    this.openDocumentBlob(documentItem, false);
  }

  openDocumentBlob(
    documentItem: any,
    inline: boolean
  ): void {
    this.documentErrorMessage = '';
    this.documentDownloadingId = documentItem.id;

    const openedWindow = inline
      ? window.open('', '_blank')
      : null;

    this.apiService
      .downloadDocument(documentItem.id, inline)
      .subscribe({
        next: (blob: Blob) => {
          const blobUrl = window.URL.createObjectURL(blob);

          if (inline) {
            if (openedWindow) {
              openedWindow.location.href = blobUrl;
            } else {
              window.open(blobUrl, '_blank');
            }
          } else {
            const link = window.document.createElement('a');

            link.href = blobUrl;
            link.download =
              documentItem.file_name ||
              `${documentItem.document_name || 'document'}`;
            link.click();
          }

          setTimeout(() => {
            window.URL.revokeObjectURL(blobUrl);
          }, 30000);

          this.documentDownloadingId = null;
        },
        error: (error: any) => {
          console.error(
            'Download document error:',
            error
          );

          if (openedWindow) {
            openedWindow.close();
          }

          this.documentDownloadingId = null;
          this.documentErrorMessage =
            error?.error?.message ||
            'Could not open the uploaded file.';
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

          this.profileChanged.emit();
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
    this.selectedDocumentFile = null;
    this.documentData = this.getEmptyDocumentData();
    this.documentErrorMessage = '';
    this.documentSuccessMessage = '';
  }

}
