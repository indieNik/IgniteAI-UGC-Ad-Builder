import { Component } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { CommonModule } from '@angular/common';
import { LucideAngularModule } from 'lucide-angular';

@Component({
    selector: 'app-admin-layout',
    standalone: true,
    imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive, LucideAngularModule],
    template: `
        <div class="admin-layout">
            <!-- Sidebar is handled by app-root, we just provide the main content area structure -->
             <main class="main-content" style="background: linear-gradient(135deg, #13141b 0%, #1a1b23 100%);">
                <header class="top-bar glass-panel" style="margin-bottom: 24px; border-radius: 12px; padding: 16px 24px;">
                    <div class="header-container">
                        <div class="project-title-group">
                             <h1 class="project-name text-gradient">Admin Center</h1>
                        </div>
                        <nav class="admin-nav">
                            <a routerLink="dashboard" routerLinkActive="active-link" class="nav-tab">Overview</a>
                            <a routerLink="runs" routerLinkActive="active-link" class="nav-tab">Execution Logs</a>
                        </nav>
                    </div>
                    <div class="header-actions">
                        <a routerLink="/campaigns" class="btn-secondary small" style="display: flex; align-items:center; gap: 8px;">
                            Exit to Editor <lucide-icon name="arrow-right" style="width: 14px; height: 14px;"></lucide-icon>
                        </a>
                    </div>
                </header>

                <div class="admin-content-container" style="padding: 0 4px;">
                    <router-outlet></router-outlet>
                </div>
            </main>
        </div>
    `,
    styles: [`
        .admin-layout {
            display: grid;
            grid-template-columns: 1fr;
            height: 100%;
            width: 100%;
            overflow: hidden;
        }

        .main-content {
            background: linear-gradient(135deg, #13141b 0%, #1a1b23 100%);
            height: 100%;
            overflow-y: auto;
            position: relative;
            display: flex;
            flex-direction: column;
            padding: 32px 40px;
        }

        .header-container {
            display: flex;
            align-items: center;
            gap: 16px;
        }

        .admin-nav {
            display: flex;
            gap: 32px;
            margin-left: 40px;
        }

        .nav-tab {
            color: #9ca3af;
            text-decoration: none;
            padding: 4px 8px;
            font-weight: 500;
            transition: color 0.2s;
            font-size: 0.95rem;
        }

        .nav-tab:hover {
            color: white;
        }

        .active-link {
            color: #fff;
            border-bottom: 2px solid var(--accent-primary);
        }

        .btn-secondary.small {
            font-size: 0.85rem;
            padding: 6px 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 6px;
            color: #ccc;
            text-decoration: none;
            transition: all 0.2s;
        }

        .btn-secondary.small:hover {
            background: rgba(255, 255, 255, 0.05);
            color: white;
            border-color: white;
        }

        @media (max-width: 768px) {
            .main-content {
                padding: 16px;
            }

            .header-container {
                flex-direction: column;
                align-items: flex-start;
                gap: 12px;
            }

            .admin-nav {
                margin-left: 0;
                width: 100%;
                gap: 24px;
                border-bottom: 1px solid rgba(255,255,255,0.1);
                padding-bottom: 8px;
            }

            .header-actions {
                position: absolute;
                top: 16px;
                right: 16px;
            }
        }
    `]
})
export class AdminComponent { }
