import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { ApiService } from '../../../../../core/services/api';
import { AuthService } from '../../../../../core/services/auth';

@Component({
  selector: 'app-case-payments-section',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './case-payments-section.html'
})
export class CasePaymentsSection {
  @Input() profile: any = null;
  @Input() caseId = 0;
  @Output() profileChanged = new EventEmitter<void>();

  paymentFormVisible = false;
  paymentSaving = false;
  editingPaymentId: number | null = null;
  paymentErrorMessage = '';
  paymentSuccessMessage = '';

  paymentData = this.getEmptyPaymentData();

  constructor(
    private apiService: ApiService,
    private authService: AuthService
  ) {}

  getEmptyPaymentData() {
    return {
      total_fee: 0,
      amount_paid: 0,
      payment_status: '',
      next_payment_due: '',
      notes: ''
    };
  }

  showAddPaymentForm(): void {
    this.paymentData = this.getEmptyPaymentData();
    this.editingPaymentId = null;
    this.paymentErrorMessage = '';
    this.paymentSuccessMessage = '';
    this.paymentFormVisible = true;
  }

  editPayment(payment: any): void {
    this.editingPaymentId = payment.id;
    this.paymentData = {
      total_fee: payment.total_fee || 0,
      amount_paid: payment.amount_paid || 0,
      payment_status: payment.payment_status || payment.status || '',
      next_payment_due:
        payment.next_payment_due || payment.next_payment_date || '',
      notes: payment.notes || ''
    };
    this.paymentFormVisible = true;
  }

  savePayment(): void {
    this.paymentErrorMessage = '';
    this.paymentSaving = true;

    const request = this.editingPaymentId
      ? this.apiService.updatePayment(
          this.editingPaymentId,
          this.paymentData
        )
      : this.apiService.createPayment(this.caseId, this.paymentData);

    request.subscribe({
      next: () => {
        this.paymentSaving = false;
        this.paymentSuccessMessage = this.editingPaymentId
          ? 'Payment updated successfully.'
          : 'Payment added successfully.';
        this.profileChanged.emit();
        setTimeout(() => this.closePaymentForm(), 700);
      },
      error: (error: any) => {
        console.error('Save payment error:', error);
        this.paymentSaving = false;
        this.paymentErrorMessage =
          error?.error?.message || 'Could not save the payment.';
      }
    });
  }

  deletePayment(payment: any): void {
    if (!this.canDeleteRecords()) {
      this.paymentErrorMessage =
        'Only admins and solicitors can delete payment records.';
      return;
    }

    const confirmed = window.confirm('Delete this payment record?');

    if (!confirmed) {
      return;
    }

    this.paymentErrorMessage = '';
    this.paymentSuccessMessage = '';

    this.apiService.deletePayment(payment.id).subscribe({
      next: () => {
        this.paymentSuccessMessage = 'Payment deleted successfully.';
        this.profileChanged.emit();
      },
      error: (error: any) => {
        console.error('Delete payment error:', error);
        this.paymentErrorMessage =
          error?.error?.message || 'Could not delete the payment.';
      }
    });
  }

  closePaymentForm(): void {
    this.paymentFormVisible = false;
    this.editingPaymentId = null;
    this.paymentData = this.getEmptyPaymentData();
    this.paymentErrorMessage = '';
    this.paymentSuccessMessage = '';
  }

  canDeleteRecords(): boolean {
    return this.authService.hasAnyRole([
      'admin',
      'solicitor'
    ]);
  }
}
