import { vi } from 'vitest';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';

import { AuthService } from '../../core/services/auth';
import { MainLayoutComponent } from './main-layout';

describe('MainLayoutComponent', () => {
  let component: MainLayoutComponent;
  let fixture: ComponentFixture<MainLayoutComponent>;

  const authService = {
    getUser: vi.fn().mockReturnValue({
      email: 'admin@firm.com',
      role: 'admin'
    }),
    logout: vi.fn(),
    hasAnyRole: vi.fn().mockReturnValue(true)
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MainLayoutComponent],
      providers: [
        { provide: AuthService, useValue: authService },
        provideRouter([])
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(MainLayoutComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
