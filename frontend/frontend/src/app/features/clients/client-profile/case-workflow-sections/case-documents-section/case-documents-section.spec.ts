import { vi } from 'vitest';
import { of } from 'rxjs';

import { CaseDocumentsSection } from './case-documents-section';

describe('CaseDocumentsSection', () => {
  let apiService: any;
  let authService: any;
  let component: CaseDocumentsSection;

  beforeEach(() => {
    apiService = {
      createDocument: vi.fn()
        .mockReturnValue(of({})),
      uploadDocument: vi.fn()
        .mockReturnValue(of({})),
      updateDocument: vi.fn()
        .mockReturnValue(of({})),
      deleteDocument: vi.fn()
        .mockReturnValue(of({})),
      downloadDocument: vi.fn()
        .mockReturnValue(of(new Blob(['test'], { type: 'text/plain' })))
    };

    authService = {
      hasAnyRole: vi.fn().mockReturnValue(true)
    };

    component = new CaseDocumentsSection(apiService, authService);
    component.caseId = 42;
    component.profile = { documents: [] };
  });

  it('should create a document record when no file is selected', () => {
    const changed = vi.fn();
    component.profileChanged.subscribe(changed);
    component.documentData.document_name = 'Passport';

    component.saveDocument();

    expect(apiService.createDocument)
      .toHaveBeenCalledWith(42, component.documentData);
    expect(changed).toHaveBeenCalled();
  });

  it('should upload a document when a file is selected', () => {
    component.documentData.document_name = 'Passport';
    component.selectedDocumentFile = new File(
      ['content'],
      'passport.pdf',
      { type: 'application/pdf' }
    );

    component.saveDocument();

    expect(apiService.uploadDocument).toHaveBeenCalled();
    expect(apiService.createDocument).not.toHaveBeenCalled();
  });

  it('should require a document name before saving', () => {
    component.documentData.document_name = '';

    component.saveDocument();

    expect(component.documentErrorMessage)
      .toBe('Document name is required.');
    expect(apiService.createDocument).not.toHaveBeenCalled();
    expect(apiService.uploadDocument).not.toHaveBeenCalled();
  });

  it('should not delete documents for restricted roles', () => {
    authService.hasAnyRole.mockReturnValue(false);

    component.deleteDocument({ id: 1, document_name: 'Passport' });

    expect(component.documentErrorMessage)
      .toBe('Only admins and solicitors can delete documents.');
    expect(apiService.deleteDocument).not.toHaveBeenCalled();
  });
});
