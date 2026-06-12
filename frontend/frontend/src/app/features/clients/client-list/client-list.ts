import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

import { ApiService } from '../../../core/services/api';

@Component({
  selector: 'app-client-list',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './client-list.html',
  styleUrl: './client-list.css'
})
export class ClientList implements OnInit {
  clients: any[] = [];
  loading = true;
  errorMessage = '';
  searchTerm = '';
  statusFilter = '';
  sortBy = 'nameAsc';

  constructor(
    private apiService: ApiService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadClients();
  }

  loadClients(): void {
    this.loading = true;
    this.errorMessage = '';

    this.apiService.getClients().subscribe({
      next: (data: any) => {
        console.log('Clients API response:', data);

        if (Array.isArray(data)) {
          this.clients = data;
        } else if (Array.isArray(data?.clients)) {
          this.clients = data.clients;
        } else {
          this.clients = [];
        }

        this.loading = false;
      },
      error: (error: any) => {
        console.error('Clients loading error:', error);

        this.errorMessage =
          error?.error?.message ||
          'Could not load clients.';

        this.loading = false;
      }
    });
  }

  addClient(): void {
    this.router.navigate(['/clients/add']);
  }

  openClient(client: any): void {
    this.router.navigate(['/clients', client.id]);
  }

  get filteredClients(): any[] {
    const search = this.searchTerm.trim().toLowerCase();

    return this.clients
      .filter((client) => {
        const status = this.getClientStatus(client);

        if (this.statusFilter && status !== this.statusFilter) {
          return false;
        }

        if (!search) {
          return true;
        }

        return [
          client.full_name,
          client.email,
          client.phone,
          client.preferred_contact_method,
          client.application_type,
          client.case_type,
          status
        ]
          .filter(Boolean)
          .some((value) => String(value).toLowerCase().includes(search));
      })
      .sort((a, b) => this.compareClients(a, b));
  }

  get statusOptions(): string[] {
    return Array.from(
      new Set(
        this.clients
          .map((client) => this.getClientStatus(client))
          .filter(Boolean)
      )
    ).sort();
  }

  clearFilters(): void {
    this.searchTerm = '';
    this.statusFilter = '';
    this.sortBy = 'nameAsc';
  }

  getClientStatus(client: any): string {
    return client.case_status || client.status || '';
  }

  private compareClients(a: any, b: any): number {
    const nameA = String(a.full_name || '');
    const nameB = String(b.full_name || '');
    const deadlineA = String(a.main_deadline || '');
    const deadlineB = String(b.main_deadline || '');

    switch (this.sortBy) {
      case 'nameDesc':
        return nameB.localeCompare(nameA);
      case 'deadlineAsc':
        return deadlineA.localeCompare(deadlineB);
      case 'deadlineDesc':
        return deadlineB.localeCompare(deadlineA);
      case 'statusAsc':
        return this.getClientStatus(a).localeCompare(this.getClientStatus(b));
      default:
        return nameA.localeCompare(nameB);
    }
  }
}
