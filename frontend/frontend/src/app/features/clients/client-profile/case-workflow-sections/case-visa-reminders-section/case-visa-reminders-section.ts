import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { ApiService } from '../../../../../core/services/api';

@Component({
  selector: 'app-case-visa-reminders-section',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './case-visa-reminders-section.html'
})
export class CaseVisaRemindersSection {
  @Input() profile: any = null;
  @Input() caseId = 0;
  @Output() profileChanged = new EventEmitter<void>();

  visaReminderFormVisible = false;
  visaReminderSaving = false;
  editingVisaReminderId: number | null = null;
  visaReminderErrorMessage = '';
  visaReminderSuccessMessage = '';

  visaReminderData = this.getEmptyVisaReminderData();

  constructor(private apiService: ApiService) {}

  getEmptyVisaReminderData() {
    return {
      visa_granted_date: '',
      visa_expiry_date: '',
      reminder_date: '',
      client_contacted: false,
      notes: ''
    };
  }

  showAddVisaReminderForm(): void {
    this.visaReminderData = this.getEmptyVisaReminderData();
    this.editingVisaReminderId = null;
    this.visaReminderErrorMessage = '';
    this.visaReminderSuccessMessage = '';
    this.visaReminderFormVisible = true;
  }

  editVisaReminder(reminder: any): void {
    this.editingVisaReminderId = reminder.id;
    this.visaReminderData = {
      visa_granted_date: reminder.visa_granted_date || '',
      visa_expiry_date: reminder.visa_expiry_date || '',
      reminder_date: reminder.reminder_date || '',
      client_contacted: reminder.client_contacted ?? false,
      notes: reminder.notes || ''
    };
    this.visaReminderFormVisible = true;
  }

  saveVisaReminder(): void {
    this.visaReminderErrorMessage = '';

    if (!this.visaReminderData.visa_expiry_date) {
      this.visaReminderErrorMessage = 'Visa expiry date is required.';
      return;
    }

    if (!this.visaReminderData.reminder_date) {
      this.visaReminderErrorMessage = 'Reminder date is required.';
      return;
    }

    this.visaReminderSaving = true;
    const request = this.editingVisaReminderId
      ? this.apiService.updateVisaReminder(
          this.editingVisaReminderId,
          this.visaReminderData
        )
      : this.apiService.createVisaReminder(
          this.caseId,
          this.visaReminderData
        );

    request.subscribe({
      next: () => {
        this.visaReminderSaving = false;
        this.visaReminderSuccessMessage = this.editingVisaReminderId
          ? 'Visa reminder updated successfully.'
          : 'Visa reminder added successfully.';
        this.profileChanged.emit();
        setTimeout(() => this.closeVisaReminderForm(), 700);
      },
      error: (error: any) => {
        console.error('Save visa reminder error:', error);
        this.visaReminderSaving = false;
        this.visaReminderErrorMessage =
          error?.error?.message || 'Could not save the visa reminder.';
      }
    });
  }

  deleteVisaReminder(reminder: any): void {
    const confirmed = window.confirm('Delete this visa reminder?');

    if (!confirmed) {
      return;
    }

    this.visaReminderErrorMessage = '';
    this.visaReminderSuccessMessage = '';

    this.apiService.deleteVisaReminder(reminder.id).subscribe({
      next: () => {
        this.visaReminderSuccessMessage =
          'Visa reminder deleted successfully.';
        this.profileChanged.emit();
      },
      error: (error: any) => {
        console.error('Delete visa reminder error:', error);
        this.visaReminderErrorMessage =
          error?.error?.message || 'Could not delete the visa reminder.';
      }
    });
  }

  closeVisaReminderForm(): void {
    this.visaReminderFormVisible = false;
    this.editingVisaReminderId = null;
    this.visaReminderData = this.getEmptyVisaReminderData();
    this.visaReminderErrorMessage = '';
    this.visaReminderSuccessMessage = '';
  }
}
