import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { environment } from '../../../environments/environment';

@Component({
    selector: 'app-email-preferences',
    standalone: true,
    imports: [CommonModule, FormsModule],
    template: `
    <div class="preferences-container">
      <div class="preferences-card">
        <h1>Email Preferences</h1>
        <p class="subtitle">Manage how we communicate with you</p>

        <div *ngIf="loading" class="loading">
          <div class="spinner"></div>
          <p>Loading preferences...</p>
        </div>

        <div *ngIf="!loading" class="preferences-form">
          <div class="preference-item disabled">
            <div class="preference-header">
              <div>
                <h3>Transactional Emails</h3>
                <p>Account security, password resets, and receipts</p>
              </div>
              <label class="toggle disabled">
                <input type="checkbox" checked disabled>
                <span class="slider"></span>
              </label>
            </div>
            <p class="note">Required for account security</p>
          </div>

          <div class="preference-item">
            <div class="preference-header">
              <div>
                <h3>Operational Emails</h3>
                <p>Video generation updates, low credits warnings, and important notifications</p>
              </div>
              <label class="toggle">
                <input type="checkbox" [(ngModel)]="preferences.operational">
                <span class="slider"></span>
              </label>
            </div>
          </div>

          <div class="preference-item">
            <div class="preference-header">
              <div>
                <h3>Marketing Emails</h3>
                <p>Tips, product updates, and promotional offers</p>
              </div>
              <label class="toggle">
                <input type="checkbox" [(ngModel)]="preferences.marketing">
                <span class="slider"></span>
              </label>
            </div>
          </div>

          <div class="actions">
            <button class="btn-primary" (click)="savePreferences()" [disabled]="saving">
              {{ saving ? 'Saving...' : 'Save Preferences' }}
            </button>
          </div>

          <div *ngIf="successMessage" class="success-message">
            {{ successMessage }}
          </div>
          <div *ngIf="errorMessage" class="error-message">
            {{ errorMessage }}
          </div>
        </div>
      </div>
    </div>
  `,
    styles: [`
    .preferences-container {
      min-height: 100vh;
      background: #f3f4f6;
      padding: 40px 20px;
    }

    .preferences-card {
      max-width: 700px;
      margin: 0 auto;
      background: white;
      border-radius: 16px;
      padding: 40px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    h1 {
      font-size: 32px;
      font-weight: 700;
      color: #1f2937;
      margin: 0 0 8px 0;
    }

    .subtitle {
      font-size: 16px;
      color: #6b7280;
      margin: 0 0 32px 0;
    }

    .loading {
      text-align: center;
      padding: 40px 0;
    }

    .spinner {
      width: 40px;
      height: 40px;
      border: 3px solid #f3f4f6;
      border-top: 3px solid #8B5CF6;
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin: 0 auto 16px;
    }

    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }

    .preference-item {
      border: 1px solid #e5e7eb;
      border-radius: 12px;
      padding: 24px;
      margin-bottom: 16px;
      transition: all 0.2s;
    }

    .preference-item:hover:not(.disabled) {
      border-color: #8B5CF6;
      box-shadow: 0 2px 8px rgba(139, 92, 246, 0.1);
    }

    .preference-item.disabled {
      background: #f9fafb;
      opacity: 0.7;
    }

    .preference-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 20px;
    }

    .preference-header h3 {
      font-size: 18px;
      font-weight: 600;
      color: #1f2937;
      margin: 0 0 4px 0;
    }

    .preference-header p {
      font-size: 14px;
      color: #6b7280;
      margin: 0;
    }

    .note {
      font-size: 12px;
      color: #9ca3af;
      margin: 12px 0 0 0;
      font-style: italic;
    }

    .toggle {
      position: relative;
      display: inline-block;
      width: 52px;
      height: 28px;
      flex-shrink: 0;
    }

    .toggle input {
      opacity: 0;
      width: 0;
      height: 0;
    }

    .slider {
      position: absolute;
      cursor: pointer;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background-color: #d1d5db;
      transition: 0.3s;
      border-radius: 28px;
    }

    .slider:before {
      position: absolute;
      content: "";
      height: 20px;
      width: 20px;
      left: 4px;
      bottom: 4px;
      background-color: white;
      transition: 0.3s;
      border-radius: 50%;
    }

    input:checked + .slider {
      background: linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%);
    }

    input:checked + .slider:before {
      transform: translateX(24px);
    }

    .toggle.disabled .slider {
      cursor: not-allowed;
      background-color: #9ca3af;
    }

    .actions {
      margin-top: 32px;
      display: flex;
      justify-content: flex-end;
    }

    .btn-primary {
      padding: 12px 32px;
      background: linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%);
      color: white;
      border: none;
      border-radius: 8px;
      font-weight: 600;
      font-size: 16px;
      cursor: pointer;
      transition: all 0.2s;
    }

    .btn-primary:hover:not(:disabled) {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
    }

    .btn-primary:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }

    .success-message, .error-message {
      margin-top: 16px;
      padding: 12px 16px;
      border-radius: 8px;
      font-size: 14px;
      text-align: center;
    }

    .success-message {
      background: #d1fae5;
      color: #065f46;
      border: 1px solid #10b981;
    }

    .error-message {
      background: #fee2e2;
      color: #991b1b;
      border: 1px solid #ef4444;
    }

    @media (max-width: 600px) {
      .preferences-card {
        padding: 24px 20px;
      }

      .preference-header {
        flex-direction: column;
        gap: 16px;
      }

      .toggle {
        align-self: flex-start;
      }
    }
  `]
})
export class EmailPreferencesComponent implements OnInit {
    loading = true;
    saving = false;
    successMessage = '';
    errorMessage = '';

    preferences = {
        operational: true,
        marketing: true
    };

    constructor(private http: HttpClient) { }

    ngOnInit() {
        this.loadPreferences();
    }

    loadPreferences() {
        this.http.get<any>(`${environment.apiUrl}/api/auth/email-preferences`)
            .subscribe({
                next: (data) => {
                    this.preferences = data;
                    this.loading = false;
                },
                error: (error) => {
                    console.error('Error loading preferences:', error);
                    this.loading = false;
                    this.errorMessage = 'Failed to load preferences';
                }
            });
    }

    savePreferences() {
        this.saving = true;
        this.successMessage = '';
        this.errorMessage = '';

        this.http.put(`${environment.apiUrl}/api/auth/email-preferences`, this.preferences)
            .subscribe({
                next: () => {
                    this.saving = false;
                    this.successMessage = 'Preferences saved successfully!';
                    setTimeout(() => this.successMessage = '', 3000);
                },
                error: (error) => {
                    this.saving = false;
                    this.errorMessage = 'Failed to save preferences. Please try again.';
                    console.error('Error saving preferences:', error);
                }
            });
    }
}
