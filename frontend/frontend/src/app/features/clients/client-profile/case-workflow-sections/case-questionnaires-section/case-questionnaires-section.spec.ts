import { vi } from 'vitest';
import { of } from 'rxjs';

import { CaseQuestionnairesSection } from './case-questionnaires-section';

describe('CaseQuestionnairesSection', () => {
  let apiService: any;
  let authService: any;
  let component: CaseQuestionnairesSection;

  beforeEach(() => {
    apiService = {
      createQuestionnaire: vi.fn().mockReturnValue(of({})),
      updateQuestionnaire: vi.fn().mockReturnValue(of({})),
      deleteQuestionnaire: vi.fn().mockReturnValue(of({}))
    };

    authService = {
      hasAnyRole: vi.fn().mockReturnValue(true)
    };

    component = new CaseQuestionnairesSection(apiService, authService);
    component.caseId = 42;
    component.profile = { questionnaires: [] };
  });

  it('should create a questionnaire item when question is present', () => {
    const changed = vi.fn();
    component.profileChanged.subscribe(changed);
    component.questionnaireData.question = 'Confirm entry date?';

    component.saveQuestionnaire();

    expect(apiService.createQuestionnaire)
      .toHaveBeenCalledWith(42, component.questionnaireData);
    expect(changed).toHaveBeenCalled();
  });

  it('should update a questionnaire item when editing', () => {
    component.editingQuestionnaireId = 8;
    component.questionnaireData.question = 'Confirm address?';

    component.saveQuestionnaire();

    expect(apiService.updateQuestionnaire)
      .toHaveBeenCalledWith(8, component.questionnaireData);
    expect(apiService.createQuestionnaire).not.toHaveBeenCalled();
  });

  it('should require a question before saving', () => {
    component.questionnaireData.question = '';

    component.saveQuestionnaire();

    expect(component.questionnaireErrorMessage)
      .toBe('Question is required.');
    expect(apiService.createQuestionnaire).not.toHaveBeenCalled();
  });

  it('should populate edit form data from answer aliases', () => {
    component.editQuestionnaire({
      id: 8,
      question: 'Confirm travel history?',
      answer: 'Confirmed',
      status: 'Answered',
      follow_up_needed: true
    });

    expect(component.editingQuestionnaireId).toBe(8);
    expect(component.questionnaireData.client_answer).toBe('Confirmed');
    expect(component.questionnaireData.follow_up_needed).toBe(true);
    expect(component.questionnaireFormVisible).toBe(true);
  });

  it('should not delete questionnaire items for restricted roles', () => {
    authService.hasAnyRole.mockReturnValue(false);

    component.deleteQuestionnaire({ id: 1, question: 'Question?' });

    expect(component.questionnaireErrorMessage)
      .toBe('Only admins and solicitors can delete questionnaire items.');
    expect(apiService.deleteQuestionnaire).not.toHaveBeenCalled();
  });
});
