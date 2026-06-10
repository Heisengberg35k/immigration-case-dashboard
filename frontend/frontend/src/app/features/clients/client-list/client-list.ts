import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

import { ApiService } from '../../../core/services/api';

@Component({
  selector: 'app-client-list',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './client-list.html',
  styleUrl: './client-list.css'
})
export class ClientList implements OnInit {
  clients: any[] = [];
  loading = true;
  errorMessage = '';

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
}