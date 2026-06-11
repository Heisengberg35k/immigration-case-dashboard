import { vi } from 'vitest';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute, Router } from '@angular/router';
import { of } from 'rxjs';

import { ApiService } from '../../../core/services/api';
import { AuthService } from '../../../core/services/auth';
import { ClientProfile } from './client-profile';

describe('ClientProfile', () => {
  let component: ClientProfile;
  let fixture: ComponentFixture<ClientProfile>;

  const apiService = {
    getClient: vi.fn()
      .mockReturnValue(of({ id: 1, case_id: 10 })),
    getCaseFullProfile: vi.fn()
      .mockReturnValue(of({
        client: { full_name: 'Test Client' },
        case: { case_status: 'Open' }
      })),
    deleteClient: vi.fn()
      .mockReturnValue(of({}))
  };

  const router = {
    navigate: vi.fn()
  };

  const authService = {
    hasAnyRole: vi.fn().mockReturnValue(true)
  };

  const route = {
    snapshot: {
      paramMap: {
        get: vi.fn().mockReturnValue('1')
      }
    }
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ClientProfile],
      providers: [
        { provide: ApiService, useValue: apiService },
        { provide: AuthService, useValue: authService },
        { provide: Router, useValue: router },
        { provide: ActivatedRoute, useValue: route }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(ClientProfile);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create and load the linked case profile', () => {
    expect(component).toBeTruthy();
    expect(component.caseId).toBe(10);
    expect(apiService.getCaseFullProfile).toHaveBeenCalledWith(10);
  });

  it('should only allow admins and solicitors to delete clients', () => {
    authService.hasAnyRole.mockReturnValue(false);

    expect(component.canDeleteClient()).toBe(false);
  });
});
