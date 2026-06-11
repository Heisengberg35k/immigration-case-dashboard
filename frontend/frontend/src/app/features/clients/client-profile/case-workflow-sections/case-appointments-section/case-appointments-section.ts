import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { ApiService } from '../../../../../core/services/api';
import { AuthService } from '../../../../../core/services/auth';

@Component({
  selector: 'app-case-appointments-section',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './case-appointments-section.html'
})
export class CaseAppointmentsSection {
  @Input() profile: any = null;
  @Input() caseId = 0;
  @Output() profileChanged = new EventEmitter<void>();

  appointmentFormVisible = false;
  appointmentSaving = false;
  editingAppointmentId: number | null = null;
  appointmentErrorMessage = '';
  appointmentSuccessMessage = '';

  appointmentData = this.getEmptyAppointmentData();

  constructor(
    private apiService: ApiService,
    private authService: AuthService
  ) {}

  getEmptyAppointmentData() {
    return {
      appointment_type: '',
      appointment_date: '',
      appointment_time: '',
      appointment_location: '',
      status: 'Booked',
      notes: ''
    };
  }

  showAddAppointmentForm(): void {
    this.appointmentData = this.getEmptyAppointmentData();
    this.editingAppointmentId = null;
    this.appointmentErrorMessage = '';
    this.appointmentSuccessMessage = '';
    this.appointmentFormVisible = true;
  }

  editAppointment(appointment: any): void {
    this.editingAppointmentId = appointment.id;
    this.appointmentData = {
      appointment_type: appointment.appointment_type || appointment.title || '',
      appointment_date: appointment.appointment_date || '',
      appointment_time: appointment.appointment_time || '',
      appointment_location:
        appointment.appointment_location || appointment.location || '',
      status: appointment.status || 'Booked',
      notes: appointment.notes || ''
    };
    this.appointmentFormVisible = true;
  }

  saveAppointment(): void {
    this.appointmentErrorMessage = '';

    if (!this.appointmentData.appointment_date) {
      this.appointmentErrorMessage = 'Appointment date is required.';
      return;
    }

    this.appointmentSaving = true;
    const request = this.editingAppointmentId
      ? this.apiService.updateAppointment(
          this.editingAppointmentId,
          this.appointmentData
        )
      : this.apiService.createAppointment(
          this.caseId,
          this.appointmentData
        );

    request.subscribe({
      next: () => {
        this.appointmentSaving = false;
        this.appointmentSuccessMessage = this.editingAppointmentId
          ? 'Appointment updated successfully.'
          : 'Appointment added successfully.';
        this.profileChanged.emit();
        setTimeout(() => this.closeAppointmentForm(), 700);
      },
      error: (error: any) => {
        console.error('Save appointment error:', error);
        this.appointmentSaving = false;
        this.appointmentErrorMessage =
          error?.error?.message || 'Could not save the appointment.';
      }
    });
  }

  deleteAppointment(appointment: any): void {
    if (!this.canDeleteRecords()) {
      this.appointmentErrorMessage =
        'Only admins and solicitors can delete appointments.';
      return;
    }

    const confirmed = window.confirm('Delete this appointment?');

    if (!confirmed) {
      return;
    }

    this.appointmentErrorMessage = '';
    this.appointmentSuccessMessage = '';

    this.apiService.deleteAppointment(appointment.id).subscribe({
      next: () => {
        this.appointmentSuccessMessage = 'Appointment deleted successfully.';
        this.profileChanged.emit();
      },
      error: (error: any) => {
        console.error('Delete appointment error:', error);
        this.appointmentErrorMessage =
          error?.error?.message || 'Could not delete the appointment.';
      }
    });
  }

  closeAppointmentForm(): void {
    this.appointmentFormVisible = false;
    this.editingAppointmentId = null;
    this.appointmentData = this.getEmptyAppointmentData();
    this.appointmentErrorMessage = '';
    this.appointmentSuccessMessage = '';
  }

  canDeleteRecords(): boolean {
    return this.authService.hasAnyRole([
      'admin',
      'solicitor'
    ]);
  }
}
