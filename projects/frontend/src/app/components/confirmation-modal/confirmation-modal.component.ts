import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ConfirmationService } from '../../services/confirmation.service';

@Component({
  selector: 'app-confirmation-modal',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="modal-overlay" *ngIf="confirmation$ | async as config" (click)="onCancel(config)">
      <div class="modal-content" (click)="$event.stopPropagation()">
        <h3>{{ config.title }}</h3>
        <p>{{ config.message }}</p>
        <div class="modal-actions">
          <button class="btn-cancel" *ngIf="config.cancelText" (click)="onCancel(config)">{{ config.cancelText }}</button>
          <button class="btn-confirm" (click)="onConfirm(config)">{{ config.confirmText }}</button>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .modal-overlay {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.8);
      backdrop-filter: blur(10px);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 10000;
      animation: fadeIn 0.2s ease;
    }

    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }

    .modal-content {
      background: linear-gradient(135deg, rgba(30, 30, 40, 0.98), rgba(20, 20, 30, 0.98));
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 16px;
      padding: 32px;
      max-width: 450px;
      width: 90%;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
      animation: slideUp 0.3s ease;
    }

    @keyframes slideUp {
      from {
        transform: translateY(20px);
        opacity: 0;
      }
      to {
        transform: translateY(0);
        opacity: 1;
      }
    }

    h3 {
      margin: 0 0 16px 0;
      font-size: 1.5rem;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }

    p {
      margin: 0 0 24px 0;
      color: rgba(255, 255, 255, 0.8);
      line-height: 1.6;
      font-size: 1rem;
      white-space: pre-line;
    }

    .modal-actions {
      display: flex;
      gap: 12px;
      justify-content: flex-end;
    }

    button {
      padding: 12px 24px;
      border-radius: 8px;
      font-weight: 600;
      font-size: 0.95rem;
      cursor: pointer;
      transition: all 0.2s ease;
      border: none;
    }

    .btn-cancel {
      background: rgba(255, 255, 255, 0.1);
      color: rgba(255, 255, 255, 0.8);
      border: 1px solid rgba(255, 255, 255, 0.2);
    }

    .btn-cancel:hover {
      background: rgba(255, 255, 255, 0.15);
      transform: translateY(-1px);
    }

    .btn-confirm {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }

    .btn-confirm:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 16px rgba(102, 126, 234, 0.5);
    }
  `]
})
export class ConfirmationModalComponent {
  private confirmationService = inject(ConfirmationService);
  confirmation$ = this.confirmationService.confirmation$;

  onConfirm(config: any) {
    config.onConfirm();
    this.confirmationService.close();
  }

  onCancel(config: any) {
    if (config.onCancel) {
      config.onCancel();
    }
    this.confirmationService.close();
  }
}
