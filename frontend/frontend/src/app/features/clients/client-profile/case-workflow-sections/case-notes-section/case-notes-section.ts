import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { ApiService } from '../../../../../core/services/api';

@Component({
  selector: 'app-case-notes-section',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './case-notes-section.html'
})
export class CaseNotesSection {
  @Input() profile: any = null;
  @Input() caseId = 0;
  @Output() profileChanged = new EventEmitter<void>();

  noteFormVisible = false;
  noteSaving = false;
  editingNoteId: number | null = null;
  noteErrorMessage = '';
  noteSuccessMessage = '';

  noteData = this.getEmptyNoteData();

  constructor(private apiService: ApiService) {}

  getEmptyNoteData() {
    return {
      note_text: ''
    };
  }

  showAddNoteForm(): void {
    this.noteData = this.getEmptyNoteData();
    this.editingNoteId = null;
    this.noteErrorMessage = '';
    this.noteSuccessMessage = '';
    this.noteFormVisible = true;
  }

  editNote(note: any): void {
    this.editingNoteId = note.id;
    this.noteData = {
      note_text: note.note_text || ''
    };
    this.noteFormVisible = true;
  }

  saveNote(): void {
    this.noteErrorMessage = '';

    if (!this.noteData.note_text.trim()) {
      this.noteErrorMessage = 'Note text is required.';
      return;
    }

    this.noteSaving = true;
    const request = this.editingNoteId
      ? this.apiService.updateNote(this.editingNoteId, this.noteData)
      : this.apiService.createNote(this.caseId, this.noteData);

    request.subscribe({
      next: () => {
        this.noteSaving = false;
        this.noteSuccessMessage = this.editingNoteId
          ? 'Note updated successfully.'
          : 'Note added successfully.';
        this.profileChanged.emit();
        setTimeout(() => this.closeNoteForm(), 700);
      },
      error: (error: any) => {
        console.error('Save note error:', error);
        this.noteSaving = false;
        this.noteErrorMessage =
          error?.error?.message || 'Could not save the note.';
      }
    });
  }

  deleteNote(note: any): void {
    const confirmed = window.confirm('Delete this note?');

    if (!confirmed) {
      return;
    }

    this.noteErrorMessage = '';
    this.noteSuccessMessage = '';

    this.apiService.deleteNote(note.id).subscribe({
      next: () => {
        this.noteSuccessMessage = 'Note deleted successfully.';
        this.profileChanged.emit();
      },
      error: (error: any) => {
        console.error('Delete note error:', error);
        this.noteErrorMessage =
          error?.error?.message || 'Could not delete the note.';
      }
    });
  }

  closeNoteForm(): void {
    this.noteFormVisible = false;
    this.editingNoteId = null;
    this.noteData = this.getEmptyNoteData();
    this.noteErrorMessage = '';
    this.noteSuccessMessage = '';
  }
}
