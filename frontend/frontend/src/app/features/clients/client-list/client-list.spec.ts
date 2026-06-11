import { vi } from 'vitest';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { of } from 'rxjs';

import { ApiService } from '../../../core/services/api';
import { ClientList } from './client-list';

describe('ClientList', () => {
  let component: ClientList;
  let fixture: ComponentFixture<ClientList>;

  const apiService = {
    getClients: vi.fn()
      .mockReturnValue(of({ clients: [] }))
  };

  const router = {
    navigate: vi.fn()
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ClientList],
      providers: [
        { provide: ApiService, useValue: apiService },
        { provide: Router, useValue: router }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(ClientList);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
