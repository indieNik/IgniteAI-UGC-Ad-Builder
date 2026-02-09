import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { LucideAngularModule } from 'lucide-angular';

@Component({
  selector: 'app-credit-badge',
  standalone: true,
  imports: [CommonModule, RouterModule, LucideAngularModule],
  template: `
    <div class="credit-badge" routerLink="/credits" 
         [title]="'Available Credits: ' + credits + ' (Click to manage)'"
         [class.zero-credits]="credits === 0">
      <lucide-icon name="circle-dollar-sign" class="icon"></lucide-icon>
      <span class="count">{{ credits }}</span>
    </div>
  `,
  styles: [`
    .credit-badge {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 6px 12px;
      background: rgba(99, 102, 241, 0.1);
      border: 1px solid rgba(99, 102, 241, 0.2);
      border-radius: 100px;
      cursor: pointer;
      transition: all 0.2s ease;
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--accent-primary);
      line-height: 1;
    }

    .credit-badge:hover {
      background: rgba(99, 102, 241, 0.15);
      border-color: var(--accent-primary);
      transform: scale(1.05);
    }

    .credit-badge.zero-credits {
      background: rgba(239, 68, 68, 0.1);
      border-color: rgba(239, 68, 68, 0.2);
      color: #ef4444;
    }

    .credit-badge.zero-credits:hover {
      background: rgba(239, 68, 68, 0.15);
      border-color: #ef4444;
    }

    .icon {
      width: 16px;
      height: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }

    .count {
      font-variant-numeric: tabular-nums;
      min-width: 16px;
      text-align: center;
      line-height: 1;
      display: flex;
      align-items: center;
    }

    @media (max-width: 1024px) {
      .credit-badge {
        padding: 4px 10px;
        font-size: 0.8rem;
      }
      .icon {
        width: 14px;
        height: 14px;
      }
    }
  `]
})
export class CreditBadgeComponent {
  @Input() credits: number = 0;
}
