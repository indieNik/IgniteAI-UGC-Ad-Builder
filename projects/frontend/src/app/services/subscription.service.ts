import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, from } from 'rxjs';
import { AuthService } from './auth.service';
import { environment } from '../../environments/environment';

export interface SubscriptionStatus {
    has_subscription: boolean;
    tier: string | null;
    status: string | null;
    period: string | null;
    current_period_end: string | null;
    cancel_at_period_end: boolean;
    monthly_credits: number;
}

export interface CreateSubscriptionResponse {
    subscription_id: string;
    short_url: string;
    tier: string;
    period: string;
    monthly_credits: number;
}

@Injectable({
    providedIn: 'root'
})
export class SubscriptionService {
    private apiUrl = environment.apiUrl;

    constructor(
        private http: HttpClient,
        private authService: AuthService
    ) { }

    /**
     * Create a new subscription.
     * Redirects user to Razorpay payment page.
     */
    async createSubscription(tier: string, period: 'monthly' | 'annual'): Promise<void> {
        try {
            const token = await this.authService.getIdToken();

            const headers = new HttpHeaders({
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            });

            const response = await this.http.post<CreateSubscriptionResponse>(
                `${this.apiUrl}/api/subscriptions/create`,
                { tier, period },
                { headers }
            ).toPromise();

            if (response && response.short_url) {
                // Redirect to Razorpay subscription payment page
                window.location.href = response.short_url;
            } else {
                throw new Error('No payment URL received');
            }
        } catch (error) {
            console.error('Error creating subscription:', error);
            throw error;
        }
    }

    /**
     * Get current user's subscription status.
     */
    getSubscriptionStatus(): Observable<SubscriptionStatus> {
        return from(this.getSubscriptionStatusAsync());
    }

    private async getSubscriptionStatusAsync(): Promise<SubscriptionStatus> {
        try {
            const token = await this.authService.getIdToken();

            const headers = new HttpHeaders({
                'Authorization': `Bearer ${token}`
            });

            return await this.http.get<SubscriptionStatus>(
                `${this.apiUrl}/api/subscriptions/status`,
                { headers }
            ).toPromise() as SubscriptionStatus;
        } catch (error) {
            console.error('Error getting subscription status:', error);
            throw error;
        }
    }

    /**
     * Cancel subscription (at end of billing period).
     */
    async cancelSubscription(): Promise<{ status: string; message: string }> {
        try {
            const token = await this.authService.getIdToken();

            const headers = new HttpHeaders({
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            });

            return await this.http.post<{ status: string; message: string }>(
                `${this.apiUrl}/api/subscriptions/cancel`,
                {},
                { headers }
            ).toPromise() as { status: string; message: string };
        } catch (error) {
            console.error('Error cancelling subscription:', error);
            throw error;
        }
    }

    /**
     * Update subscription tier (upgrade/downgrade).
     */
    async updateSubscription(newTier: string): Promise<any> {
        try {
            const token = await this.authService.getIdToken();

            const headers = new HttpHeaders({
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            });

            return await this.http.post(
                `${this.apiUrl}/api/subscriptions/update`,
                { new_tier: newTier },
                { headers }
            ).toPromise();
        } catch (error) {
            console.error('Error updating subscription:', error);
            throw error;
        }
    }
}
