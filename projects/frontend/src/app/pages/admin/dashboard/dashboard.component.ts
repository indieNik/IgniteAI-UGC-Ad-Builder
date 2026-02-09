import { Component, OnInit, inject } from '@angular/core';
import { AdminService, AdminStats } from '../../../services/admin.service';
import { CommonModule } from '@angular/common';
import { LucideAngularModule } from 'lucide-angular';
import { LoaderComponent } from '../../../components/loader/loader.component';

@Component({
    selector: 'app-admin-dashboard',
    standalone: true,
    imports: [CommonModule, LucideAngularModule, LoaderComponent],
    template: `
        <div class="dashboard-container">
            <app-loader [isLoading]="!stats" message="Gathering platform intelligence..."></app-loader>

            <div class="stats-grid" *ngIf="stats">
                <!-- Card 1: Runs -->
                <div class="glass-panel card">
                    <h3 class="card-label">Total Runs</h3>
                    <div class="card-value">{{ stats.total_runs }}</div>
                    <div class="card-footer">
                        <lucide-icon name="sparkles" class="icon-xs text-indigo no-bg flex-center-icon" style="width: 14px; height: 14px;"></lucide-icon>
                        <span style="display: inline-block; vertical-align: middle;">All time executions</span>
                    </div>
                </div>

                <!-- Card 2: Cost -->
                <div class="glass-panel card">
                    <h3 class="card-label">Total AI Spend</h3>
                    <div class="card-value text-gradient-green">\${{ stats.total_cost_usd | number:'1.2-2' }}</div>
                     <div class="card-footer">
                        <lucide-icon name="zap" class="icon-xs text-green no-bg flex-center-icon" style="width: 14px; height: 14px;"></lucide-icon>
                        <span style="display: inline-block; vertical-align: middle;">Exact server-side calculation</span>
                    </div>
                </div>

                <!-- Card 3: User Activity -->
                <div class="glass-panel card">
                    <h3 class="card-label mb-large">User Activity</h3>
                    
                    <div class="activity-grid">
                        <!-- Online Now -->
                        <div class="activity-item">
                            <span class="activity-value white">{{ stats.active_users_now }}</span>
                            <span class="activity-label">Online</span>
                        </div>
                        
                         <!-- WAU -->
                        <div class="activity-item border-left">
                            <span class="activity-value blue">{{ stats.active_users_7d }}</span>
                            <span class="activity-label">7 Days</span>
                        </div>

                         <!-- MAU -->
                        <div class="activity-item border-left">
                            <span class="activity-value indigo">{{ stats.active_users_30d }}</span>
                            <span class="activity-label">30 Days</span>
                        </div>
                    </div>
                     <div class="live-indicator">
                        <span class="ping-container">
                          <span class="ping-sub" *ngIf="stats.active_users_now > 0"></span>
                          <span class="ping-dot" [class.active]="stats.active_users_now > 0"></span>
                        </span>
                        <span>Live App Usage</span>
                    </div>
                </div>
            </div>

            <!-- Financials Section -->
            <div class="section-container" *ngIf="margins">
                <h3 class="section-title">Financial Health</h3>
                <div class="stats-grid">
                    <div class="glass-panel card">
                        <h3 class="card-label">Revenue</h3>
                        <div class="card-value text-gradient-gold">\${{ margins.revenue | number:'1.2-2' }}</div>
                        <div class="card-footer">
                             {{ margins.credits_consumed }} credits
                        </div>
                    </div>

                    <div class="glass-panel card">
                        <h3 class="card-label">COGS</h3>
                        <div class="card-value">\${{ margins.cogs | number:'1.2-2' }}</div>
                    </div>

                    <div class="glass-panel card">
                        <h3 class="card-label">Net Margin</h3>
                        <div class="card-value" [class.negative]="margins.margin < 0" [class.positive]="margins.margin >= 0">
                            {{ margins.margin_percent }}%
                        </div>
                        <div class="card-footer">
                            \${{ margins.margin | number:'1.2-2' }} {{ margins.margin < 0 ? 'loss' : 'profit' }}
                        </div>
                    </div>
                </div>
            </div>

            <!-- Rate Limits Section -->
            <div class="section-container" *ngIf="rateLimits">
                <h3 class="section-title">API Rate Limits (Gemini/Veo)</h3>
                <div class="limits-grid">
                    <div class="glass-panel limit-card" *ngFor="let model of objectKeys(rateLimits)">
                        <div class="model-header">
                            <span class="model-name">{{ model }}</span>
                            <span class="status-indicator optimal"></span>
                        </div>
                        <div class="limit-stats">
                            <div class="stat-row">
                                <span class="stat-label">Requests Today</span>
                                <span class="stat-value">{{ rateLimits[model].daily_count }} <span class="stat-sub">/ 10</span></span>
                            </div>
                            <div class="stat-row">
                                <span class="stat-label">Last Reset</span>
                                <span class="stat-value small">{{ rateLimits[model].last_reset_date }}</span>
                            </div>
                        </div>
                        <!-- Progress Bar -->
                         <div class="progress-bar-bg">
                            <div class="progress-bar-fill" [style.width.%]="(rateLimits[model].daily_count / 10) * 100"></div>
                         </div>
                    </div>
                </div>
            </div>

            <div *ngIf="!stats" class="loading-state">Loading platform statistics...</div>
        </div>
    `,
    styles: [`
        .dashboard-container {
            width: 100%;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 24px;
            margin-bottom: 32px;
        }

        @media (max-width: 1024px) {
            .stats-grid {
                grid-template-columns: 1fr;
            }
        }

        .card {
            padding: 24px;
            position: relative;
            overflow: hidden;
            transition: all 0.3s ease;
        }

        .card:hover {
            border-color: rgba(99, 102, 241, 0.5);
        }

        .card-label {
            color: #9ca3af;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 8px;
            margin-top: 0;
        }

        .mb-large {
            margin-bottom: 16px;
        }

        .card-value {
            font-size: 2.25rem;
            font-weight: 800;
            color: white;
            margin-bottom: 8px;
            line-height: 1;
        }

        .text-gradient-green {
            background: linear-gradient(135deg, #4ade80 0%, #22c55e 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .text-gradient-gold {
            background: linear-gradient(135deg, #FFD700 0%, #FDB931 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .positive { color: #4ade80; }
        .negative { color: #ef4444; }

        .card-footer {
            font-size: 0.75rem;
            color: #6b7280;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
        }

        .dot.indigo { background-color: #6366f1; }
        .dot.green { background-color: #22c55e; }

        /* Activity Grid */
        .activity-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
            margin-bottom: 12px;
        }

        .activity-item {
            display: flex;
            flex-direction: column;
        }

        .border-left {
            border-left: 1px solid rgba(55, 65, 81, 0.5);
            padding-left: 16px;
        }

        .activity-value {
            font-size: 1.5rem;
            font-weight: 800;
            margin-bottom: 4px;
            line-height: 1;
        }

        .activity-value.white { color: white; }
        .activity-value.blue { color: #60a5fa; }
        .activity-value.indigo { color: #818cf8; }

        .activity-label {
            font-size: 0.65rem;
            color: #9ca3af;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 500;
        }

        .live-indicator {
            font-size: 0.75rem;
            color: #6b7280;
            display: flex;
            align-items: center;
            gap: 8px;
            padding-top: 8px;
            border-top: 1px solid rgba(75, 85, 99, 0.3);
        }

        .ping-container {
            position: relative;
            display: flex;
            height: 8px;
            width: 8px;
        }

        .ping-sub {
            position: absolute;
            display: inline-flex;
            height: 100%;
            width: 100%;
            border-radius: 50%;
            background-color: #4ade80;
            opacity: 0.75;
            animation: ping 1s cubic-bezier(0, 0, 0.2, 1) infinite;
        }

        @keyframes ping {
            75%, 100% {
                transform: scale(2);
                opacity: 0;
            }
        }

        .ping-dot {
            position: relative;
            display: inline-flex;
            border-radius: 50%;
            height: 8px;
            width: 8px;
            background-color: #4b5563;
        }

        .ping-dot.active {
            background-color: #22c55e;
        }

    /* Loading */
        .loading-state {
            color: #9ca3af;
            text-align: center;
            margin-top: 40px;
            animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: .5; }
        }

        /* Rate Limits */
        .section-container {
            margin-top: 40px;
        }

        .section-title {
            font-size: 1rem;
            color: #fff;
            margin-bottom: 16px;
            font-weight: 600;
        }

        .limits-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 24px;
        }

        .limit-card {
            padding: 20px;
        }

        .model-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }

        .model-name {
            font-size: 0.9rem;
            font-weight: 600;
            color: #e2e8f0;
        }

        .status-indicator {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #22c55e;
            box-shadow: 0 0 10px rgba(34, 197, 94, 0.4);
        }

        .stat-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 0.85rem;
        }

        .stat-label {
            color: #94a3b8;
        }

        .stat-value {
            color: #fff;
            font-weight: 600;
        }

        .stat-sub {
            color: #64748b;
            font-weight: 400;
            font-size: 0.8rem;
        }
        
        .stat-value.small {
             font-size: 0.8rem;
             color: #cbd5e1;
        }

        .progress-bar-bg {
            height: 4px;
            background: rgba(255,255,255,0.1);
            border-radius: 2px;
            margin-top: 16px;
            overflow: hidden;
        }

        .progress-bar-fill {
            height: 100%;
            background: #6366f1;
            border-radius: 2px;
            transition: width 0.3s ease;
        }

        @media (max-width: 768px) {
            .stats-grid {
                gap: 16px;
            }

            .card-label {
                font-size: 0.7rem;
            }

            .card-value {
                font-size: 1.75rem;
            }

            .activity-grid {
                gap: 8px;
            }
            
            .limits-grid {
                grid-template-columns: 1fr; /* Stack on mobile */
            }
        }
    `]
})
export class DashboardComponent implements OnInit {
    private adminService = inject(AdminService);
    stats: AdminStats | null = null;
    rateLimits: any = null;
    margins: any = null;
    objectKeys = Object.keys;

    async ngOnInit() {
        try {
            const [stats, limits, margins] = await Promise.all([
                this.adminService.getStats(),
                this.adminService.getRateLimits(),
                this.adminService.getMargins()
            ]);
            this.stats = stats;
            this.rateLimits = limits;
            this.margins = margins;
        } catch (e) {
            console.error('Failed to load stats', e);
        }
    }
}
