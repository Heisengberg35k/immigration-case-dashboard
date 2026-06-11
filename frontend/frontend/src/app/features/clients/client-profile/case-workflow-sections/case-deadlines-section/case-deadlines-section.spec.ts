import { vi } from 'vitest';
import { of } from 'rxjs';

import { CaseDeadlinesSection } from './case-deadlines-section';

describe('CaseDeadlinesSection', () => {
  let apiService: any;
  let component: CaseDeadlinesSection;

  beforeEach(() => {
    apiService = {
      createDeadline: vi.fn().mockReturnValue(of({})),
      updateDeadline: vi.fn().mockReturnValue(of({})),
      deleteDeadline: vi.fn().mockReturnValue(of({}))
    };

    component = new CaseDeadlinesSection(apiService);
    component.caseId = 42;
    component.profile = { deadlines: [] };
  });

  it('should create a deadline when required fields are present', () => {
    const changed = vi.fn();
    component.profileChanged.subscribe(changed);
    component.deadlineData.deadline_type = 'Upload Deadline';
    component.deadlineData.deadline_date = '2026-07-01';

    component.saveDeadline();

    expect(apiService.createDeadline)
      .toHaveBeenCalledWith(42, component.deadlineData);
    expect(changed).toHaveBeenCalled();
  });

  it('should update a deadline when editing', () => {
    component.editingDeadlineId = 7;
    component.deadlineData.deadline_type = 'Review Deadline';
    component.deadlineData.deadline_date = '2026-07-02';

    component.saveDeadline();

    expect(apiService.updateDeadline)
      .toHaveBeenCalledWith(7, component.deadlineData);
    expect(apiService.createDeadline).not.toHaveBeenCalled();
  });

  it('should require a deadline type before saving', () => {
    component.deadlineData.deadline_type = '';
    component.deadlineData.deadline_date = '2026-07-01';

    component.saveDeadline();

    expect(component.deadlineErrorMessage)
      .toBe('Deadline type is required.');
    expect(apiService.createDeadline).not.toHaveBeenCalled();
  });

  it('should require a deadline date before saving', () => {
    component.deadlineData.deadline_type = 'Upload Deadline';
    component.deadlineData.deadline_date = '';

    component.saveDeadline();

    expect(component.deadlineErrorMessage)
      .toBe('Deadline date is required.');
    expect(apiService.createDeadline).not.toHaveBeenCalled();
  });
});
