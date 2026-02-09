import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-icon',
  standalone: true,
  imports: [CommonModule],
  template: `
    <svg [attr.width]="size" [attr.height]="size" [attr.viewBox]="viewBox" fill="none" xmlns="http://www.w3.org/2000/svg">
      <ng-container [ngSwitch]="name">
        <!-- Download Icon -->
        <g *ngSwitchCase="'download'">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </g>
        
        <!-- Share Icon -->
        <g *ngSwitchCase="'share'">
          <circle cx="18" cy="5" r="3" stroke="currentColor" stroke-width="2"/>
          <circle cx="6" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
          <circle cx="18" cy="19" r="3" stroke="currentColor" stroke-width="2"/>
          <path d="m8.59 13.51 6.83 3.98M15.41 6.51l-6.82 3.98" stroke="currentColor" stroke-width="2"/>
        </g>
        
        <!-- User/Circle User Icon -->
        <g *ngSwitchCase="'user'">
          <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
          <circle cx="12" cy="10" r="3" stroke="currentColor" stroke-width="2"/>
          <path d="M7 18.5c1-2.5 2.5-4 5-4s4 1.5 5 4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </g>
        
        <!-- Arrow Left Icon -->
        <g *ngSwitchCase="'arrow-left'">
          <path d="M19 12H5M12 19l-7-7 7-7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </g>
        
        <!-- Arrow Right Icon -->
        <g *ngSwitchCase="'arrow-right'">
          <path d="M5 12h14M12 5l7 7-7 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </g>
        
        <!-- Chevron Down Icon -->
        <g *ngSwitchCase="'chevron-down'">
          <path d="m6 9 6 6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </g>
        
        <!-- Chevron Right Icon -->
        <g *ngSwitchCase="'chevron-right'">
          <path d="m9 18 6-6-6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </g>
        
        <!-- Play Icon -->
        <g *ngSwitchCase="'play'">
          <path d="M5 3l14 9-14 9V3z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </g>
        
        <!-- X/Close Icon -->
        <g *ngSwitchCase="'x'">
          <path d="M18 6 6 18M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </g>
        
        <!-- Menu Icon -->
        <g *ngSwitchCase="'menu'">
          <path d="M3 12h18M3 6h18M3 18h18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </g>
        
        <!-- Folder Icon -->
        <g *ngSwitchCase="'folder'">
          <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </g>
        
        <!-- Image Icon -->
        <g *ngSwitchCase="'image'">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2" stroke="currentColor" stroke-width="2"/>
          <circle cx="8.5" cy="8.5" r="1.5" fill="currentColor"/>
          <path d="m21 15-5-5L5 21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </g>
        
        <!-- Sparkles Icon -->
        <g *ngSwitchCase="'sparkles'">
          <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3ZM5 3v4M3 5h4M19 17v4M17 19h4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </g>
        
        <!-- Shield Icon -->
        <g *ngSwitchCase="'shield'">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </g>
        
        <!-- Globe/Community Icon -->
        <g *ngSwitchCase="'globe'">
          <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
          <path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" stroke="currentColor" stroke-width="2"/>
        </g>
        
        <!-- Settings Icon -->
        <g *ngSwitchCase="'settings'">
          <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
          <path d="M12 1v6m0 6v6M4.22 4.22l4.24 4.24m5.08 5.08 4.24 4.24M1 12h6m6 0h6M4.22 19.78l4.24-4.24m5.08-5.08 4.24-4.24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </g>
      </ng-container>
    </svg>
  `,
  styles: [`
    :host {
      display: inline-flex;
      align-items: center;
      justify-content: center;
    }
    svg {
      display: block;
    }
  `]
})
export class IconComponent {
  @Input() name: string = '';
  @Input() size: string = '24';

  get viewBox(): string {
    return '0 0 24 24';
  }
}
