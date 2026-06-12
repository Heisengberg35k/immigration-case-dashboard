import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';

import { CaseAppointmentsSection } from './case-appointments-section/case-appointments-section';
import { CaseDeadlinesSection } from './case-deadlines-section/case-deadlines-section';
import { CaseDocumentsSection } from './case-documents-section/case-documents-section';
import { CaseNotesSection } from './case-notes-section/case-notes-section';
import { CasePaymentsSection } from './case-payments-section/case-payments-section';
import { CaseQuestionnairesSection } from './case-questionnaires-section/case-questionnaires-section';
import { CaseVisaRemindersSection } from './case-visa-reminders-section/case-visa-reminders-section';

@Component({
  selector: 'app-case-workflow-sections',
  standalone: true,
  imports: [
    CommonModule,
    CaseAppointmentsSection,
    CaseDeadlinesSection,
    CaseDocumentsSection,
    CaseNotesSection,
    CasePaymentsSection,
    CaseQuestionnairesSection,
    CaseVisaRemindersSection
  ],
  templateUrl: './case-workflow-sections.html',
  styleUrl: './case-workflow-sections.css'
})
export class CaseWorkflowSections {
  @Input() profile: any = null;
  @Input() caseId = 0;
  @Output() profileChanged = new EventEmitter<void>();

  activeSection = 'documents';

  sections = [
    { id: 'documents', label: 'Documents', mark: 'I' },
    { id: 'questionnaires', label: 'Questionnaires', mark: 'II' },
    { id: 'deadlines', label: 'Deadlines', mark: 'III' },
    { id: 'appointments', label: 'Appointments', mark: 'IV' },
    { id: 'payments', label: 'Payments', mark: 'V' },
    { id: 'visaReminders', label: 'Visa Reminders', mark: 'VI' },
    { id: 'notes', label: 'Notes', mark: 'VII' }
  ];

  selectSection(sectionId: string): void {
    this.activeSection = sectionId;
  }
}
