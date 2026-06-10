import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { ApiService } from '../../../core/services/api';

@Component({
  selector: 'app-users',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './users.html',
  styleUrl: './users.css'
})
export class Users implements OnInit {
  loading = true;
  savingUserId: number | null = null;
  errorMessage = '';
  successMessage = '';
  users: any[] = [];

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    this.loadUsers();
  }

  loadUsers(): void {
    this.loading = true;
    this.errorMessage = '';

    this.apiService.getUsers().subscribe({
      next: (data: any) => {
        this.users = Array.isArray(data?.users)
          ? data.users
          : [];
        this.loading = false;
      },
      error: (error: any) => {
        console.error('Users loading error:', error);
        this.errorMessage =
          error?.error?.message ||
          'Could not load users.';
        this.loading = false;
      }
    });
  }

  updateRole(user: any, role: string): void {
    this.errorMessage = '';
    this.successMessage = '';
    this.savingUserId = user.id;

    this.apiService.updateUserRole(user.id, role).subscribe({
      next: (data: any) => {
        user.role = data?.user?.role || role;
        this.successMessage = 'User role updated successfully.';
        this.savingUserId = null;
      },
      error: (error: any) => {
        console.error('User role update error:', error);
        this.errorMessage =
          error?.error?.message ||
          'Could not update user role.';
        this.savingUserId = null;
      }
    });
  }
}
