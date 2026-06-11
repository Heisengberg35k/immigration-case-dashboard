import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { ApiService } from '../../../../../core/services/api';

@Component({
  selector: 'app-case-deadlines-section',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './case-deadlines-section.html'
})
export class CaseDeadlinesSection {
  @Input() profile: any = null;
  @Input() caseId = 0;
  @Output() profileChanged = new EventEmitter<void>();

  deadlineFormVisible = false;
  deadlineSaving = false;
  editingDeadlineId: number | null = null;
  deadlineErrorMessage = '';
  deadlineSuccessMessage = '';

  deadlineData = this.getEmptyDeadlineData();

  constructor(private apiService: ApiService) {}

  getEmptyDeadlineData() {
    return {
      deadline_type: '',
      deadline_date: '',
      status: 'Upcoming',
      notes: ''
    };
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
