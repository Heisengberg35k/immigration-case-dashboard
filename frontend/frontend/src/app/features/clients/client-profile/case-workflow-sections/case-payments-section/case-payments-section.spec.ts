import { vi } from 'vitest';
import { of } from 'rxjs';

import { CasePaymentsSection } from './case-payments-section';

describe('CasePaymentsSection', () => {
  let apiService: any;
  let authService: any;
  let component: CasePaymentsSection;

  beforeEach(() => {
    apiService = {
      createPayment: vi.fn().mockReturnValue(of({})),
      updatePayment: vi.fn().mockReturnValue(of({})),
      deletePayment: vi.fn().mockReturnValue(of({}))
    };

    authService = {
      hasAnyRole: vi.fn().mockReturnValue(true)
    };

    component = new CasePaymentsSection(apiService, authService);
    component.caseId = 42;
    component.profile = { payments: [] };
  });

  it('should create a payment record', () => {
    const changed = vi.fn();
    component.profileChanged.subscribe(changed);
    component.paymentData.total_fee = 1200;
    component.paymentData.amount_paid = 300;

    component.savePayment();

    expect(apiService.createPayment)
      .toHaveBeenCalledWith(42, component.paymentData);
    expect(changed).toHaveBeenCalled();
  });

  it('should update a payment record when editing', () => {
    component.editingPaymentId = 5;
    component.paymentData.total_fee = 1200;
    component.paymentData.amount_paid = 600;

    component.savePayment();

    expect(apiService.updatePayment)
      .toHaveBeenCalledWith(5, component.paymentData);
    expect(apiService.createPayment).not.toHaveBeenCalled();
  });

  it('should populate edit form data from existing payment aliases', () => {
    component.editPayment({
      id: 5,
      total_fee: 1000,
      amount_paid: 250,
      status: 'Part Paid',
      next_payment_date: '2026-07-10',
      notes: 'Installments'
    });

    expect(component.editingPaymentId).toBe(5);
    expect(component.paymentData.payment_status).toBe('Part Paid');
    expect(component.paymentData.next_payment_due).toBe('2026-07-10');
    expect(component.paymentFormVisible).toBe(true);
  });

  it('should not delete payments for restricted roles', () => {
    authService.hasAnyRole.mockReturnValue(false);

    component.deletePayment({ id: 1 });

    expect(component.paymentErrorMessage)
      .toBe('Only admins and solicitors can delete payment records.');
    expect(apiService.deletePayment).not.toHaveBeenCalled();
  });
});
