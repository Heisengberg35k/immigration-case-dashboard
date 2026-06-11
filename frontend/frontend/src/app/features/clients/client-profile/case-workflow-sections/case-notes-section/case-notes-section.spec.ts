import { vi } from 'vitest';
import { of } from 'rxjs';

import { CaseNotesSection } from './case-notes-section';

describe('CaseNotesSection', () => {
  let apiService: any;
  let authService: any;
  let component: CaseNotesSection;

  beforeEach(() => {
    apiService = {
      createNote: vi.fn().mockReturnValue(of({})),
      updateNote: vi.fn().mockReturnValue(of({})),
      deleteNote: vi.fn().mockReturnValue(of({}))
    };

    authService = {
      hasAnyRole: vi.fn().mockReturnValue(true)
    };

    component = new CaseNotesSection(apiService, authService);
    component.caseId = 42;
    component.profile = { notes: [] };
  });

  it('should create a note when text is present', () => {
    const changed = vi.fn();
    component.profileChanged.subscribe(changed);
    component.noteData.note_text = 'Client called with update.';

    component.saveNote();

    expect(apiService.createNote)
      .toHaveBeenCalledWith(42, component.noteData);
    expect(changed).toHaveBeenCalled();
  });

  it('should update a note when editing', () => {
    component.editingNoteId = 15;
    component.noteData.note_text = 'Updated note.';

    component.saveNote();

    expect(apiService.updateNote)
      .toHaveBeenCalledWith(15, component.noteData);
    expect(apiService.createNote).not.toHaveBeenCalled();
  });

  it('should require note text before saving', () => {
    component.noteData.note_text = '';

    component.saveNote();

    expect(component.noteErrorMessage)
      .toBe('Note text is required.');
    expect(apiService.createNote).not.toHaveBeenCalled();
  });

  it('should populate edit form data', () => {
    component.editNote({
      id: 15,
      note_text: 'Existing note.'
    });

    expect(component.editingNoteId).toBe(15);
    expect(component.noteData.note_text).toBe('Existing note.');
    expect(component.noteFormVisible).toBe(true);
  });

  it('should not delete notes for restricted roles', () => {
    authService.hasAnyRole.mockReturnValue(false);

    component.deleteNote({ id: 1 });

    expect(component.noteErrorMessage)
      .toBe('Only admins and solicitors can delete notes.');
    expect(apiService.deleteNote).not.toHaveBeenCalled();
  });
});
