import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { AuthService } from './auth.service';
import { environment } from '../../environments/environment';
import { firstValueFrom } from 'rxjs';

export interface AdminStats {
    total_runs: number;
    total_cost_usd: number;
    active_users_now: number;
    active_users_7d: number;
    active_users_30d: number;
    sample_size: number | string;
}

export interface RunRecord {
    run_id: string;
    user_id: string;
    status: string;
    cost_usd?: number; // Root level cost (new standard)
    result?: {
        video_url?: string;
        cost_usd?: number; // Legacy nested cost
        log_url?: string;
    };
    created_at?: number;
    updated_at: number;
}

@Injectable({
    providedIn: 'root'
})
export class AdminService {
    private http = inject(HttpClient);
    private auth = inject(AuthService);
    private apiUrl = `${environment.apiUrl}/api/admin`;

    private cachedIsAdmin: boolean | null = null;

    private async getHeaders() {
        const token = await this.auth.getIdToken();
        return new HttpHeaders().set('Authorization', `Bearer ${token}`);
    }

    async checkAdmin(): Promise<boolean> {
        if (this.cachedIsAdmin !== null) return this.cachedIsAdmin;
        try {
            await this.getStats();
            this.cachedIsAdmin = true;
            return true;
        } catch {
            this.cachedIsAdmin = false;
            return false;
        }
    }

    async getStats(): Promise<AdminStats> {
        const headers = await this.getHeaders();
        const stats = await firstValueFrom(this.http.get<AdminStats>(`${this.apiUrl}/stats`, { headers }));
        this.cachedIsAdmin = true;
        return stats;
    }

    async getAllRuns(limit = 20, startAfter?: any): Promise<RunRecord[]> {
        const headers = await this.getHeaders();
        let url = `${this.apiUrl}/runs?limit=${limit}`;
        // Pagination logic could be added here if needed
        return firstValueFrom(this.http.get<RunRecord[]>(url, { headers }));
    }

    async getRateLimits(): Promise<any> {
        const headers = await this.getHeaders();
        return firstValueFrom(this.http.get(`${this.apiUrl}/rate-limits`, { headers }));
    }

    async getMargins(): Promise<any> {
        const headers = await this.getHeaders();
        return firstValueFrom(this.http.get(`${this.apiUrl}/margins`, { headers }));
    }

    async getLogContent(runId: string): Promise<string> {
        // Logs are stored in storage, but we might want to fetch via backend proxy or direct URL
        // Backend admin runs list returns 'log_url'
        // If we want to view it, we can fetch the text from that URL directly
        return "";
    }
}
