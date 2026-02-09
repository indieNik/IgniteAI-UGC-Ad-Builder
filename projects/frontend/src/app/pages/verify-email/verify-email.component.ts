import { Component, OnInit, inject } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { environment } from '../../../environments/environment';
import { ConfirmationService } from '../../services/confirmation.service';

@Component({
  selector: 'app-verify-email',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="verify-container">
      <div class="verify-card">
        <div *ngIf="loading" class="loading-state">
          <div class="spinner"></div>
          <h2>Verifying your email...</h2>
          <p>Please wait while we confirm your email address.</p>
        </div>

        <div *ngIf="!loading && success" class="success-state">
          <div class="success-icon">✓</div>
          <h2>Email Verified!</h2>
          <p>Your email has been successfully verified.</p>
          <p class="redirect-message">Redirecting to dashboard in {{ countdown }} seconds...</p>
          <button class="btn-primary" (click)="goToDashboard()">Go to Dashboard Now</button>
        </div>

        <div *ngIf="!loading && !success" class="error-state">
          <div class="error-icon">✕</div>
          <h2>Verification Failed</h2>
          <p class="error-message">{{ errorMessage }}</p>
          <div class="error-actions">
            <button class="btn-secondary" (click)="resendVerification()">Resend Verification Email</button>
            <button class="btn-primary" (click)="goToHome()">Go to Home</button>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .verify-container {
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%);
      padding: 20px;
    }

    .verify-card {
      background: white;
      border-radius: 16px;
      padding: 48px;
      max-width: 500px;
      width: 100%;
      text-align: center;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    }

    .spinner {
      width: 60px;
      height: 60px;
      border: 4px solid #f3f4f6;
      border-top: 4px solid #8B5CF6;
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin: 0 auto 24px;
    }

    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }

    .success-icon, .error-icon {
      width: 80px;
      height: 80px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 48px;
      margin: 0 auto 24px;
      font-weight: bold;
    }

    .success-icon {
      background: #10B981;
      color: white;
    }

    .error-icon {
      background: #EF4444;
      color: white;
    }

    h2 {
      font-size: 28px;
      font-weight: 700;
      color: #1f2937;
      margin: 0 0 16px 0;
    }

    p {
      font-size: 16px;
      color: #6b7280;
      margin: 0 0 12px 0;
    }

    .redirect-message {
      color: #8B5CF6;
      font-weight: 600;
      margin: 24px 0;
    }

    .error-message {
      color: #EF4444;
      margin: 16px 0 24px 0;
    }

    .error-actions {
      display: flex;
      gap: 12px;
      justify-content: center;
      flex-wrap: wrap;
    }

    button {
      padding: 12px 24px;
      border-radius: 8px;
      font-weight: 600;
      font-size: 16px;
      cursor: pointer;
      border: none;
      transition: all 0.2s;
    }

    .btn-primary {
      background: linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%);
      color: white;
    }

    .btn-primary:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
    }

    .btn-secondary {
      background: white;
      color: #8B5CF6;
      border: 2px solid #8B5CF6;
    }

    .btn-secondary:hover {
      background: #f9fafb;
    }

    @media (max-width: 600px) {
      .verify-card {
        padding: 32px 24px;
      }

      .error-actions {
        flex-direction: column;
      }

      button {
        width: 100%;
      }
    }
  `]
})
export class VerifyEmailComponent implements OnInit {
  loading = true;
  success = false;
  errorMessage = '';
  countdown = 3;
  private countdownInterval: any;
  private confirmationService = inject(ConfirmationService);

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private http: HttpClient
  ) { }

  ngOnInit() {
    const token = this.route.snapshot.queryParams['token'];

    if (!token) {
      this.loading = false;
      this.errorMessage = 'No verification token provided. Please check your email link.';
      return;
    }

    this.verifyEmail(token);
  }

  verifyEmail(token: string) {
    this.http.post(`${environment.apiUrl}/api/auth/verify-email`, { token })
      .subscribe({
        next: () => {
          this.loading = false;
          this.success = true;
          this.startCountdown();
        },
        error: (error) => {
          this.loading = false;
          this.success = false;
          this.errorMessage = error.error?.detail || 'Verification failed. The link may be invalid or expired.';
        }
      });
  }

  startCountdown() {
    this.countdownInterval = setInterval(() => {
      this.countdown--;
      if (this.countdown === 0) {
        clearInterval(this.countdownInterval);
        this.goToDashboard();
      }
    }, 1000);
  }

  goToDashboard() {
    if (this.countdownInterval) {
      clearInterval(this.countdownInterval);
    }
    this.router.navigate(['/projects']);
  }

  goToHome() {
    this.router.navigate(['/']);
  }

  resendVerification() {
    // This would call the resend verification endpoint
    this.confirmationService.confirm({
      title: 'Coming Soon',
      message: 'Resend verification functionality will be implemented soon.',
      confirmText: 'OK',
      onConfirm: () => { }
    });
  }

  ngOnDestroy() {
    if (this.countdownInterval) {
      clearInterval(this.countdownInterval);
    }
  }
}
