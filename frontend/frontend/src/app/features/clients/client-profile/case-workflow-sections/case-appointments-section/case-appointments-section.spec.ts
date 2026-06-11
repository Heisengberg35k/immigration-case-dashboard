import { vi } from 'vitest';
import { of } from 'rxjs';

import { CaseAppointmentsSection } from './case-appointments-section';

describe('CaseAppointmentsSection', () => {
  let apiService: any;
  let component: CaseAppointmentsSection;

  beforeEach(() => {
    apiService = {
      createAppointment: vi.fn().mockReturnValue(of({})),
      updateAppointment: vi.fn().mockReturnValue(of({})),
      deleteAppointment: vi.fn().mockReturnValue(of({}))
    };

    component = new CaseAppointmentsSection(apiService);
    component.caseId = 42;
    component.profile = { appointments: [] };
  });

  it('should create an appointment when a date is present', () => {
    const changed = vi.fn();
    component.profileChanged.subscribe(changed);
    component.appointmentData.appointment_date = '2026-07-01';

    component.saveAppointment();

    expect(apiService.createAppointment)
      .toHaveBeenCalledWith(42, component.appointmentData);
    expect(changed).toHaveBeenCalled();
  });

  it('should update an appointment when editing', () => {
    component.editingAppointmentId = 9;
    component.appointmentData.appointment_date = '2026-07-02';

    component.saveAppointment();

    expect(apiService.updateAppointment)
      .toHaveBeenCalledWith(9, component.appointmentData);
    expect(apiService.createAppointment).not.toHaveBeenCalled();
  });

  it('should require an appointment date before saving', () => {
    component.appointmentData.appointment_date = '';

    component.saveAppointment();

    expect(component.appointmentErrorMessage)
      .toBe('Appointment date is required.');
    expect(apiService.createAppointment).not.toHaveBeenCalled();
  });

  it('should populate edit form data from appointment aliases', () => {
    component.editAppointment({
      id: 9,
      title: 'Biometrics',
      appointment_date: '2026-07-03',
      location: 'TLS Centre',
      status: 'Booked'
    });

    expect(component.editingAppointmentId).toBe(9);
    expect(component.appointmentData.appointment_type).toBe('Biometrics');
    expect(component.appointmentData.appointment_location).toBe('TLS Centre');
    expect(component.appointmentFormVisible).toBe(true);
  });
});
