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
      .mockReturnValue(of({
        clients: [
          {
            id: 1,
            full_name: 'Zara Client',
            email: 'zara@example.com',
            case_status: 'Open',
            application_type: 'Spouse Visa',
            main_deadline: '2026-07-01'
          },
          {
            id: 2,
            full_name: 'Adam Client',
            email: 'adam@example.com',
            case_status: 'Closed',
            application_type: 'ILR',
            main_deadline: '2026-06-01'
          }
        ]
      }))
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

  it('should search clients by case details', () => {
    component.searchTerm = 'spouse';

    expect(component.filteredClients.length).toBe(1);
    expect(component.filteredClients[0].full_name).toBe('Zara Client');
  });

  it('should filter clients by status', () => {
    component.statusFilter = 'Closed';

    expect(component.filteredClients.length).toBe(1);
    expect(component.filteredClients[0].full_name).toBe('Adam Client');
  });

  it('should sort clients by earliest deadline', () => {
    component.sortBy = 'deadlineAsc';

    expect(component.filteredClients[0].full_name).toBe('Adam Client');
  });

  it('should clear filters', () => {
    component.searchTerm = 'spouse';
    component.statusFilter = 'Open';
    component.sortBy = 'deadlineDesc';

    component.clearFilters();

    expect(component.searchTerm).toBe('');
    expect(component.statusFilter).toBe('');
    expect(component.sortBy).toBe('nameAsc');
  });
});
