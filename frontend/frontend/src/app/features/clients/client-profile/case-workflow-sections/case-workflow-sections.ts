import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { CaseAppointmentsSection } from './case-appointments-section/case-appointments-section';
import { CaseNotesSection } from './case-notes-section/case-notes-section';
import { CasePaymentsSection } from './case-payments-section/case-payments-section';
import { CaseVisaRemindersSection } from './case-visa-reminders-section/case-visa-reminders-section';
import { ApiService } from '../../../../core/services/api';

@Component({
  selector: 'app-case-workflow-sections',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    CaseAppointmentsSection,
    CaseNotesSection,
    CasePaymentsSection,
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
  questionnaireFormVisible = false;
  questionnaireSaving = false;
  editingQuestionnaireId: number | null = null;
  questionnaireErrorMessage = '';
  questionnaireSuccessMessage = '';
  deadlineFormVisible = false;
  deadlineSaving = false;
  editingDeadlineId: number | null = null;
  deadlineErrorMessage = '';
  deadlineSuccessMessage = '';
  documentData = this.getEmptyDocumentData();
  questionnaireData = this.getEmptyQuestionnaireData();
  deadlineData = this.getEmptyDeadlineData();

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

  getEmptyQuestionnaireData() {
    return {
      question: '',
      client_answer: '',
      status: 'Not Asked',
      asked_date: '',
      answered_date: '',
      follow_up_needed: false,
      notes: ''
    };
  }

  getEmptyDeadlineData() {
    return {
      deadline_type: '',
      deadline_date: '',
      status: 'Upcoming',
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

  showAddQuestionnaireForm(): void {
    this.questionnaireData = this.getEmptyQuestionnaireData();
    this.editingQuestionnaireId = null;
    this.questionnaireErrorMessage = '';
    this.questionnaireSuccessMessage = '';
    this.questionnaireFormVisible = true;
  }

  editQuestionnaire(questionnaireItem: any): void {
    this.editingQuestionnaireId = questionnaireItem.id;

    this.questionnaireData = {
      question: questionnaireItem.question || '',
      client_answer:
        questionnaireItem.client_answer ||
        questionnaireItem.answer ||
        '',
      status: questionnaireItem.status || 'Not Asked',
      asked_date: questionnaireItem.asked_date || '',
      answered_date: questionnaireItem.answered_date || '',
      follow_up_needed:
        questionnaireItem.follow_up_needed ?? false,
      notes: questionnaireItem.notes || ''
    };

    this.questionnaireErrorMessage = '';
    this.questionnaireSuccessMessage = '';
    this.questionnaireFormVisible = true;

    setTimeout(() => {
      window.document
        .getElementById('questionnaire-form')
        ?.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
    });
  }

  saveQuestionnaire(): void {
    this.questionnaireErrorMessage = '';
    this.questionnaireSuccessMessage = '';

    if (!this.questionnaireData.question.trim()) {
      this.questionnaireErrorMessage =
        'Question is required.';
      return;
    }

    if (!this.caseId) {
      this.questionnaireErrorMessage =
        'No linked case was found.';
      return;
    }

    this.questionnaireSaving = true;

    if (this.editingQuestionnaireId) {
      this.apiService
        .updateQuestionnaire(
          this.editingQuestionnaireId,
          this.questionnaireData
        )
        .subscribe({
          next: () => {
            this.questionnaireSaving = false;
            this.questionnaireSuccessMessage =
              'Questionnaire item updated successfully.';

            this.profileChanged.emit();

            setTimeout(() => {
              this.closeQuestionnaireForm();
            }, 700);
          },
          error: (error: any) => {
            console.error(
              'Update questionnaire error:',
              error
            );

            this.questionnaireSaving = false;

            this.questionnaireErrorMessage =
              error?.error?.message ||
              'Could not update the questionnaire item.';
          }
        });

      return;
    }

    this.apiService
      .createQuestionnaire(
        this.caseId,
        this.questionnaireData
      )
      .subscribe({
        next: () => {
          this.questionnaireSaving = false;
          this.questionnaireSuccessMessage =
            'Questionnaire item added successfully.';

          this.profileChanged.emit();

          setTimeout(() => {
            this.closeQuestionnaireForm();
          }, 700);
        },
        error: (error: any) => {
          console.error(
            'Create questionnaire error:',
            error
          );

          this.questionnaireSaving = false;

          this.questionnaireErrorMessage =
            error?.error?.message ||
            'Could not add the questionnaire item.';
        }
      });
  }

  deleteQuestionnaire(questionnaireItem: any): void {
    const question =
      questionnaireItem.question ||
      'this questionnaire item';

    const confirmed = window.confirm(
      `Delete "${question}"?`
    );

    if (!confirmed) {
      return;
    }

    this.questionnaireErrorMessage = '';
    this.questionnaireSuccessMessage = '';

    this.apiService
      .deleteQuestionnaire(questionnaireItem.id)
      .subscribe({
        next: () => {
          this.questionnaireSuccessMessage =
            'Questionnaire item deleted successfully.';

          this.profileChanged.emit();
        },
        error: (error: any) => {
          console.error(
            'Delete questionnaire error:',
            error
          );

          this.questionnaireErrorMessage =
            error?.error?.message ||
            'Could not delete the questionnaire item.';
        }
      });
  }

  closeQuestionnaireForm(): void {
    this.questionnaireFormVisible = false;
    this.editingQuestionnaireId = null;
    this.questionnaireData = this.getEmptyQuestionnaireData();
    this.questionnaireErrorMessage = '';
    this.questionnaireSuccessMessage = '';
  }

  showAddDeadlineForm(): void {
    this.deadlineData = this.getEmptyDeadlineData();
    this.editingDeadlineId = null;
    this.deadlineErrorMessage = '';
    this.deadlineSuccessMessage = '';
    this.deadlineFormVisible = true;
  }

  editDeadline(deadlineItem: any): void {
    this.editingDeadlineId = deadlineItem.id;

    this.deadlineData = {
      deadline_type:
        deadlineItem.deadline_type ||
        deadlineItem.title ||
        '',
      deadline_date:
        deadlineItem.deadline_date ||
        deadlineItem.due_date ||
        '',
      status: deadlineItem.status || 'Upcoming',
      notes: deadlineItem.notes || ''
    };

    this.deadlineErrorMessage = '';
    this.deadlineSuccessMessage = '';
    this.deadlineFormVisible = true;

    setTimeout(() => {
      window.document
        .getElementById('deadline-form')
        ?.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
    });
  }

  saveDeadline(): void {
    this.deadlineErrorMessage = '';
    this.deadlineSuccessMessage = '';

    if (!this.deadlineData.deadline_type.trim()) {
      this.deadlineErrorMessage =
        'Deadline type is required.';
      return;
    }

    if (!this.deadlineData.deadline_date) {
      this.deadlineErrorMessage =
        'Deadline date is required.';
      return;
    }

    if (!this.caseId) {
      this.deadlineErrorMessage =
        'No linked case was found.';
      return;
    }

    this.deadlineSaving = true;

    if (this.editingDeadlineId) {
      this.apiService
        .updateDeadline(
          this.editingDeadlineId,
          this.deadlineData
        )
        .subscribe({
          next: () => {
            this.deadlineSaving = false;
            this.deadlineSuccessMessage =
              'Deadline updated successfully.';

            this.profileChanged.emit();

            setTimeout(() => {
              this.closeDeadlineForm();
            }, 700);
          },
          error: (error: any) => {
            console.error(
              'Update deadline error:',
              error
            );

            this.deadlineSaving = false;

            this.deadlineErrorMessage =
              error?.error?.message ||
              'Could not update the deadline.';
          }
        });

      return;
    }

    this.apiService
      .createDeadline(
        this.caseId,
        this.deadlineData
      )
      .subscribe({
        next: () => {
          this.deadlineSaving = false;
          this.deadlineSuccessMessage =
            'Deadline added successfully.';

          this.profileChanged.emit();

          setTimeout(() => {
            this.closeDeadlineForm();
          }, 700);
        },
        error: (error: any) => {
          console.error(
            'Create deadline error:',
            error
          );

          this.deadlineSaving = false;

          this.deadlineErrorMessage =
            error?.error?.message ||
            'Could not add the deadline.';
        }
      });
  }

  deleteDeadline(deadlineItem: any): void {
    const deadlineName =
      deadlineItem.deadline_type ||
      deadlineItem.title ||
      'this deadline';

    const confirmed = window.confirm(
      `Delete "${deadlineName}"?`
    );

    if (!confirmed) {
      return;
    }

    this.deadlineErrorMessage = '';
    this.deadlineSuccessMessage = '';

    this.apiService
      .deleteDeadline(deadlineItem.id)
      .subscribe({
        next: () => {
          this.deadlineSuccessMessage =
            'Deadline deleted successfully.';

          this.profileChanged.emit();
        },
        error: (error: any) => {
          console.error(
            'Delete deadline error:',
            error
          );

          this.deadlineErrorMessage =
            error?.error?.message ||
            'Could not delete the deadline.';
        }
      });
  }

  closeDeadlineForm(): void {
    this.deadlineFormVisible = false;
    this.editingDeadlineId = null;
    this.deadlineData = this.getEmptyDeadlineData();
    this.deadlineErrorMessage = '';
    this.deadlineSuccessMessage = '';
  }

}
