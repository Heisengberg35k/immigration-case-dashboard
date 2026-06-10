import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private readonly apiUrl = 'http://127.0.0.1:5000/api';

  constructor(private http: HttpClient) {}

  getDashboardSummary(): Observable<any> {
    return this.http.get<any>(
      `${this.apiUrl}/dashboard/summary`
    );
  }

  getReportsOverview(): Observable<any> {
    return this.http.get<any>(
      `${this.apiUrl}/reports/overview`
    );
  }

  getAuditLogs(): Observable<any> {
    return this.http.get<any>(
      `${this.apiUrl}/audit-logs`
    );
  }

  getUsers(): Observable<any> {
    return this.http.get<any>(
      `${this.apiUrl}/users`
    );
  }

  updateUserRole(userId: number, role: string): Observable<any> {
    return this.http.put<any>(
      `${this.apiUrl}/users/${userId}/role`,
      { role }
    );
  }

  getClients(): Observable<any> {
    return this.http.get<any>(
      `${this.apiUrl}/clients`
    );
  }

  getClient(id: number): Observable<any> {
    return this.http.get<any>(
      `${this.apiUrl}/clients/${id}`
    );
  }

  createClient(clientData: any): Observable<any> {
    return this.http.post<any>(
      `${this.apiUrl}/clients`,
      clientData
    );
  }

  updateClient(
    id: number,
    clientData: any
  ): Observable<any> {
    return this.http.put<any>(
      `${this.apiUrl}/clients/${id}`,
      clientData
    );
  }

  deleteClient(id: number): Observable<any> {
    return this.http.delete<any>(
      `${this.apiUrl}/clients/${id}`
    );
  }

  getCaseFullProfile(caseId: number): Observable<any> {
    return this.http.get<any>(
      `${this.apiUrl}/cases/${caseId}/full-profile`
    );
  }

  getCaseDocuments(caseId: number): Observable<any> {
    return this.http.get<any>(
      `${this.apiUrl}/cases/${caseId}/documents`
    );
  }

  createDocument(
    caseId: number,
    documentData: any
  ): Observable<any> {
    return this.http.post<any>(
      `${this.apiUrl}/cases/${caseId}/documents`,
      documentData
    );
  }

  uploadDocument(
    caseId: number,
    documentData: FormData
  ): Observable<any> {
    return this.http.post<any>(
      `${this.apiUrl}/cases/${caseId}/documents/upload`,
      documentData
    );
  }

  getDocument(documentId: number): Observable<any> {
    return this.http.get<any>(
      `${this.apiUrl}/documents/${documentId}`
    );
  }

  updateDocument(
    documentId: number,
    documentData: any
  ): Observable<any> {
    return this.http.put<any>(
      `${this.apiUrl}/documents/${documentId}`,
      documentData
    );
  }

  deleteDocument(documentId: number): Observable<any> {
    return this.http.delete<any>(
      `${this.apiUrl}/documents/${documentId}`
    );
  }

  downloadDocument(
    documentId: number,
    inline = false
  ): Observable<Blob> {
    const disposition = inline ? 'inline' : 'attachment';

    return this.http.get(
      `${this.apiUrl}/documents/${documentId}/download?disposition=${disposition}`,
      {
        responseType: 'blob'
      }
    );
  }

  getCaseQuestionnaires(caseId: number): Observable<any> {
    return this.http.get<any>(
      `${this.apiUrl}/cases/${caseId}/questionnaires`
    );
  }

  createQuestionnaire(
    caseId: number,
    questionnaireData: any
  ): Observable<any> {
    return this.http.post<any>(
      `${this.apiUrl}/cases/${caseId}/questionnaires`,
      questionnaireData
    );
  }

  updateQuestionnaire(
    questionnaireId: number,
    questionnaireData: any
  ): Observable<any> {
    return this.http.put<any>(
      `${this.apiUrl}/questionnaires/${questionnaireId}`,
      questionnaireData
    );
  }

  deleteQuestionnaire(
    questionnaireId: number
  ): Observable<any> {
    return this.http.delete<any>(
      `${this.apiUrl}/questionnaires/${questionnaireId}`
    );
  }

  getCaseDeadlines(caseId: number): Observable<any> {
    return this.http.get<any>(
      `${this.apiUrl}/cases/${caseId}/deadlines`
    );
  }

  createDeadline(
    caseId: number,
    deadlineData: any
  ): Observable<any> {
    return this.http.post<any>(
      `${this.apiUrl}/cases/${caseId}/deadlines`,
      deadlineData
    );
  }

  updateDeadline(
    deadlineId: number,
    deadlineData: any
  ): Observable<any> {
    return this.http.put<any>(
      `${this.apiUrl}/deadlines/${deadlineId}`,
      deadlineData
    );
  }

  deleteDeadline(deadlineId: number): Observable<any> {
    return this.http.delete<any>(
      `${this.apiUrl}/deadlines/${deadlineId}`
    );
  }

  createAppointment(
    caseId: number,
    appointmentData: any
  ): Observable<any> {
    return this.http.post<any>(
      `${this.apiUrl}/cases/${caseId}/appointments`,
      appointmentData
    );
  }

  updateAppointment(
    appointmentId: number,
    appointmentData: any
  ): Observable<any> {
    return this.http.put<any>(
      `${this.apiUrl}/appointments/${appointmentId}`,
      appointmentData
    );
  }

  deleteAppointment(appointmentId: number): Observable<any> {
    return this.http.delete<any>(
      `${this.apiUrl}/appointments/${appointmentId}`
    );
  }

  createPayment(
    caseId: number,
    paymentData: any
  ): Observable<any> {
    return this.http.post<any>(
      `${this.apiUrl}/cases/${caseId}/payments`,
      paymentData
    );
  }

  updatePayment(
    paymentId: number,
    paymentData: any
  ): Observable<any> {
    return this.http.put<any>(
      `${this.apiUrl}/payments/${paymentId}`,
      paymentData
    );
  }

  deletePayment(paymentId: number): Observable<any> {
    return this.http.delete<any>(
      `${this.apiUrl}/payments/${paymentId}`
    );
  }

  createVisaReminder(
    caseId: number,
    reminderData: any
  ): Observable<any> {
    return this.http.post<any>(
      `${this.apiUrl}/cases/${caseId}/visa-reminders`,
      reminderData
    );
  }

  updateVisaReminder(
    reminderId: number,
    reminderData: any
  ): Observable<any> {
    return this.http.put<any>(
      `${this.apiUrl}/visa-reminders/${reminderId}`,
      reminderData
    );
  }

  deleteVisaReminder(reminderId: number): Observable<any> {
    return this.http.delete<any>(
      `${this.apiUrl}/visa-reminders/${reminderId}`
    );
  }

  createNote(caseId: number, noteData: any): Observable<any> {
    return this.http.post<any>(
      `${this.apiUrl}/cases/${caseId}/notes`,
      noteData
    );
  }

  updateNote(noteId: number, noteData: any): Observable<any> {
    return this.http.put<any>(
      `${this.apiUrl}/notes/${noteId}`,
      noteData
    );
  }

  deleteNote(noteId: number): Observable<any> {
    return this.http.delete<any>(
      `${this.apiUrl}/notes/${noteId}`
    );
  }
}
