import { Component, OnInit, inject } from '@angular/core';
import { AdminService, RunRecord } from '../../../services/admin.service';
import { CommonModule, DatePipe } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { LucideAngularModule } from 'lucide-angular';

@Component({
    selector: 'app-admin-runs',
    standalone: true,
    imports: [CommonModule, DatePipe, LucideAngularModule],
    template: `
        <div class="runs-container">
            <h2 class="page-title">Execution History (God Mode)</h2>
            
            <div class="glass-panel table-wrapper">
                <table class="runs-table">
                    <thead>
                        <tr>
                            <th>Run ID / User</th>
                            <th>Generated</th>
                            <th>Status</th>
                            <th>Cost</th>
                            <th class="text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr *ngFor="let run of runs" class="run-row">
                            <td>
                                <div class="user-info">
                                    <span class="run-id">{{ run.run_id }}</span>
                                    <span class="user-id">{{ run.user_id | slice:0:12 }}...</span>
                                </div>
                            </td>
                            <td class="timestamp">
                                {{ run.updated_at * 1000 | date:'MMM d, h:mm a' }}
                            </td>
                            <td>
                                <span class="status-badge" [ngClass]="run.status">
                                    {{ run.status }}
                                </span>
                            </td>
                            <td class="cost-cell">
                                <span *ngIf="run.cost_usd || run.result?.cost_usd; else noCost" class="cost-val">
                                    \${{ (run.cost_usd || run.result?.cost_usd) | number:'1.2-4' }}
                                </span>
                                <ng-template #noCost><span class="no-cost">-</span></ng-template>
                            </td>
                            <td class="actions-cell">
                                <a *ngIf="run.result?.video_url" [href]="run.result?.video_url" target="_blank" class="action-btn link">
                                    Watch Video
                                </a>
                                <button *ngIf="run.result?.log_url" (click)="viewLog(run.result!.log_url!)" class="action-btn">
                                    Log
                                </button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Log Modal -->
            <div *ngIf="selectedLogContent" class="modal-overlay" (click)="closeLog()">
                <div class="modal-window" (click)="$event.stopPropagation()">
                    <div class="modal-header">
                        <h3>Run Log Output</h3>
                        <button (click)="closeLog()" class="close-btn">
                            <lucide-icon name="x"></lucide-icon>
                        </button>
                    </div>
                    <div class="modal-body">
                        <pre>{{ selectedLogContent }}</pre>
                    </div>
                </div>
            </div>
        </div>
    `,
    styles: [`
        .runs-container {
            padding: 24px;
            padding-top: 0;
            width: 100%;
        }

        .page-title {
            font-size: 1.25rem;
            font-weight: 700;
            color: white;
            margin-bottom: 16px;
        }

        .table-wrapper {
            overflow-x: auto;
            border-radius: 12px;
        }

        .runs-table {
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 0.875rem;
            color: #9ca3af;
        }

        .runs-table th {
            padding: 16px 24px;
            background: rgba(0, 0, 0, 0.3);
            color: #e5e7eb;
            text-transform: uppercase;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            border-bottom: 1px solid rgba(55, 65, 81, 0.5);
        }

        .runs-table td {
            padding: 16px 24px;
            border-bottom: 1px solid rgba(55, 65, 81, 0.3);
        }

        .run-row:hover {
            background: rgba(255, 255, 255, 0.05);
        }

        .user-info {
            display: flex;
            flex-direction: column;
        }

        .run-id {
            font-family: monospace;
            color: white;
            font-size: 0.75rem;
        }

        .user-id {
            color: #4b5563;
            font-size: 0.65rem;
        }

        .timestamp {
            font-size: 0.75rem;
        }

        /* Status Badges */
        .status-badge {
            padding: 2px 8px;
            border-radius: 9999px;
            font-size: 0.65rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border: 1px solid transparent;
        }

        .status-badge.completed {
            background: rgba(34, 197, 94, 0.1);
            color: #4ade80;
            border-color: rgba(34, 197, 94, 0.2);
        }

        .status-badge.failed {
            background: rgba(239, 68, 68, 0.1);
            color: #f87171;
            border-color: rgba(239, 68, 68, 0.2);
        }

        .status-badge.running,
        .status-badge.queued {
            background: rgba(59, 130, 246, 0.1);
            color: #60a5fa;
            border-color: rgba(59, 130, 246, 0.2);
        }

        .cost-cell {
            font-family: monospace;
            font-size: 0.75rem;
        }

        .cost-val { color: #4ade80; }
        .no-cost { color: #4b5563; }

        .actions-cell {
            display: flex;
            gap: 12px;
            justify-content: flex-end;
            align-items: center;
        }

        .text-right { text-align: right; }

        .action-btn {
            font-size: 0.75rem;
            padding: 4px 8px;
            border-radius: 4px;
            border: 1px solid #374151;
            color: #9ca3af;
            background: transparent;
            cursor: pointer;
            text-decoration: none;
            transition: all 0.2s;
        }

        .action-btn:hover {
            color: white;
            border-color: #6b7280;
        }

        .action-btn.link {
            border-color: rgba(59, 130, 246, 0.3);
            color: #60a5fa;
        }

        .action-btn.link:hover {
            background: rgba(59, 130, 246, 0.1);
            color: white;
        }

        /* Modal */
        .modal-overlay {
            position: fixed;
            inset: 0;
            background: rgba(0, 0, 0, 0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 50;
            padding: 16px;
        }

        .modal-window {
            background: #111827;
            width: 100%;
            max-width: 800px;
            height: 80vh;
            border-radius: 12px;
            border: 1px solid #374151;
            display: flex;
            flex-direction: column;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px;
            border-bottom: 1px solid #374151;
        }

        .modal-header h3 {
            margin: 0;
            color: white;
            font-family: monospace;
            font-size: 1rem;
        }

        .close-btn {
            background: none;
            border: none;
            color: #9ca3af;
            font-size: 1.5rem;
            cursor: pointer;
        }

        .close-btn:hover { color: white; }

        .modal-body {
            flex: 1;
            overflow: auto;
            padding: 16px;
            background: black;
        }

        .modal-body pre {
            color: #4ade80;
            font-family: monospace;
            font-size: 0.75rem;
            white-space: pre-wrap;
            margin: 0;
        }

        @media (max-width: 768px) {
            .runs-container {
                padding: 16px;
                padding-top: 0;
            }
            
            .page-title {
                font-size: 1.1rem;
            }

            /* Hide less critical columns on small mobile if needed, 
               but scrolling is usually preferred for data tables. 
               We'll stick to reducing padding/fonts. */
            
            .runs-table th, .runs-table td {
                padding: 12px 16px;
            }
        }
    `]
})
export class RunsComponent implements OnInit {
    private adminService = inject(AdminService);
    private http = inject(HttpClient);
    runs: RunRecord[] = [];
    selectedLogContent: string | null = null;

    async ngOnInit() {
        this.runs = await this.adminService.getAllRuns(50);
    }

    async viewLog(url: string) {
        try {
            this.selectedLogContent = "Loading log...";
            // Fetch the text content from the public URL
            this.selectedLogContent = await firstValueFrom(this.http.get(url, { responseType: 'text' }));
        } catch (e) {
            this.selectedLogContent = `Failed to load log: ${e}`;
        }
    }

    closeLog() {
        this.selectedLogContent = null;
    }
}
