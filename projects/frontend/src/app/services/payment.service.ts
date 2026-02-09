import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

declare var Razorpay: any;

@Injectable({
    providedIn: 'root'
})
export class PaymentService {
    private apiUrl = `${environment.apiUrl}/api/payments`;

    constructor(private http: HttpClient) { }

    createOrder(tier: string): Observable<any> {
        return this.http.post(`${this.apiUrl}/create-order`, { tier });
    }

    getCredits(): Observable<any> {
        return this.http.get(`${this.apiUrl}/credits`);
    }

    verifyPayment(paymentDetails: any, amount: number): Observable<any> {
        return this.http.post(`${this.apiUrl}/verify`, { ...paymentDetails, amount });
    }

    initiatePayment(order: any, userDetails: { name: string, email: string, contact: string }): Promise<any> {
        return new Promise((resolve, reject) => {
            const options = {
                key: environment.razorpayKeyId,
                amount: order.amount,
                currency: order.currency,
                name: 'IgniteAI',
                description: 'Buying Ad Credits',
                order_id: order.id,
                handler: (response: any) => {
                    this.verifyPayment(response, order.amount / 100).subscribe({
                        next: (res) => resolve(res),
                        error: (err) => reject(err)
                    });
                },
                prefill: {
                    name: userDetails.name,
                    email: userDetails.email,
                    contact: userDetails.contact
                },
                theme: {
                    color: '#00F2FF'
                }
            };

            const rzp = new Razorpay(options);
            rzp.on('payment.failed', (response: any) => {
                reject(response.error);
            });
            rzp.open();
        });
    }
}
