import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { ApiService } from '../../../../../core/services/api';
import { AuthService } from '../../../../../core/services/auth';

@Component({
  selector: 'app-case-questionnaires-section',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './case-questionnaires-section.html'
})
export class CaseQuestionnairesSection {
  @Input() profile: any = null;
  @Input() caseId = 0;
  @Output() profileChanged = new EventEmitter<void>();

  questionnaireFormVisible = false;
  questionnaireSaving = false;
  editingQuestionnaireId: number | null = null;
  questionnaireErrorMessage = '';
  questionnaireSuccessMessage = '';

  questionnaireData = this.getEmptyQuestionnaireData();

  constructor(
    private apiService: ApiService,
    private authService: AuthService
  ) {}

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
    if (!this.canDeleteRecords()) {
      this.questionnaireErrorMessage =
        'Only admins and solicitors can delete questionnaire items.';
      return;
    }

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

  canDeleteRecords(): boolean {
    return this.authService.hasAnyRole([
      'admin',
      'solicitor'
    ]);
  }
}
