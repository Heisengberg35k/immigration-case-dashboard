import { vi } from 'vitest';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { of } from 'rxjs';

import { ApiService } from '../../../core/services/api';
import { Dashboard } from './dashboard';

describe('Dashboard', () => {
  let component: Dashboard;
  let fixture: ComponentFixture<Dashboard>;

  const apiService = {
    getDashboardSummary: vi.fn()
      .mockReturnValue(of({
        active_cases: 0,
        waiting_documents: 0,
        waiting_client_answers: 0,
        solicitor_review_pending: 0,
        upload_deadlines_this_week: 0,
        due_deadlines_today: 0,
        overdue_deadlines: 0,
        deadline_alerts: [],
        appointments_this_week: 0,
        payments_overdue: 0,
        visa_renewals_due_soon: 0
      }))
  };

  const router = {
    navigate: vi.fn()
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Dashboard],
      providers: [
        { provide: ApiService, useValue: apiService },
        { provide: Router, useValue: router }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(Dashboard);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
