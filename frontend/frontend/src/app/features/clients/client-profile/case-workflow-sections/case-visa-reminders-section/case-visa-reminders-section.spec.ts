import { vi } from 'vitest';
import { of } from 'rxjs';

import { CaseVisaRemindersSection } from './case-visa-reminders-section';

describe('CaseVisaRemindersSection', () => {
  let apiService: any;
  let component: CaseVisaRemindersSection;

  beforeEach(() => {
    apiService = {
      createVisaReminder: vi.fn().mockReturnValue(of({})),
      updateVisaReminder: vi.fn().mockReturnValue(of({})),
      deleteVisaReminder: vi.fn().mockReturnValue(of({}))
    };

    component = new CaseVisaRemindersSection(apiService);
    component.caseId = 42;
    component.profile = { visa_reminders: [] };
  });

  it('should create a visa reminder when required dates are present', () => {
    const changed = vi.fn();
    component.profileChanged.subscribe(changed);
    component.visaReminderData.visa_expiry_date = '2026-12-01';
    component.visaReminderData.reminder_date = '2026-11-01';

    component.saveVisaReminder();

    expect(apiService.createVisaReminder)
      .toHaveBeenCalledWith(42, component.visaReminderData);
    expect(changed).toHaveBeenCalled();
  });

  it('should update a visa reminder when editing', () => {
    component.editingVisaReminderId = 12;
    component.visaReminderData.visa_expiry_date = '2026-12-01';
    component.visaReminderData.reminder_date = '2026-11-01';

    component.saveVisaReminder();

    expect(apiService.updateVisaReminder)
      .toHaveBeenCalledWith(12, component.visaReminderData);
    expect(apiService.createVisaReminder).not.toHaveBeenCalled();
  });

  it('should require a visa expiry date before saving', () => {
    component.visaReminderData.visa_expiry_date = '';
    component.visaReminderData.reminder_date = '2026-11-01';

    component.saveVisaReminder();

    expect(component.visaReminderErrorMessage)
      .toBe('Visa expiry date is required.');
    expect(apiService.createVisaReminder).not.toHaveBeenCalled();
  });

  it('should require a reminder date before saving', () => {
    component.visaReminderData.visa_expiry_date = '2026-12-01';
    component.visaReminderData.reminder_date = '';

    component.saveVisaReminder();

    expect(component.visaReminderErrorMessage)
      .toBe('Reminder date is required.');
    expect(apiService.createVisaReminder).not.toHaveBeenCalled();
  });
});
