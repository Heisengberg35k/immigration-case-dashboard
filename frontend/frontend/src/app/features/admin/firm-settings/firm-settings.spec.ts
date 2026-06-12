import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { vi } from 'vitest';

import { ApiService } from '../../../core/services/api';
import { AuthService } from '../../../core/services/auth';
import { FirmSettings } from './firm-settings';

describe('FirmSettings', () => {
  let component: FirmSettings;
  let fixture: ComponentFixture<FirmSettings>;

  const apiService = {
    getFirm: vi.fn().mockReturnValue(of({
      firm: {
        id: 1,
        name: 'Demo Firm',
        created_at: '2026-06-12T10:00:00'
      }
    })),
    updateFirm: vi.fn().mockReturnValue(of({
      firm: {
        id: 1,
        name: 'Updated Firm',
        created_at: '2026-06-12T10:00:00'
      }
    }))
  };

  const authService = {
    hasAnyRole: vi.fn().mockReturnValue(true)
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FirmSettings],
      providers: [
        { provide: ApiService, useValue: apiService },
        { provide: AuthService, useValue: authService }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(FirmSettings);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should load firm settings', () => {
    expect(component.firmName).toBe('Demo Firm');
    expect(apiService.getFirm).toHaveBeenCalled();
  });

  it('should allow admins to save firm settings', () => {
    component.firmName = 'Updated Firm';

    component.saveFirm();

    expect(apiService.updateFirm).toHaveBeenCalledWith({
      name: 'Updated Firm'
    });
    expect(component.successMessage).toBe(
      'Firm settings updated successfully.'
    );
  });
});
