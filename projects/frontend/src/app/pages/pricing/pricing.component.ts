import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, ActivatedRoute } from '@angular/router';
import { LucideAngularModule } from 'lucide-angular';
import { PaymentService } from '../../services/payment.service';
import { AuthService } from '../../services/auth.service';
import { SubscriptionService } from '../../services/subscription.service';
import { PRODUCT_CONTENT, PricingPlan } from '../../shared/product-content';
import { ConfirmationService } from '../../services/confirmation.service';

interface PricingTier {
    id: string;
    name: string;
    monthlyPrice: number;
    annualPrice: number;
    monthlyCredits: number;
    badge?: string;
    badgeColor: 'purple' | 'blue';
    ctaText: string;
    ctaColor: 'purple' | 'blue';
    features: string[];
    subtitle?: string;
    isFeatured: boolean;
    coinImage?: string;
}

@Component({
    selector: 'app-pricing',
    standalone: true,
    imports: [CommonModule, LucideAngularModule],
    templateUrl: './pricing.component.html',
    styleUrls: ['./pricing.component.css']
})
export class PricingComponent implements OnInit {
    isProcessingPayment = false;
    userCredits = 0;
    userName = '';
    billingPeriod: 'monthly' | 'annual' = 'monthly';
    private confirmationService = inject(ConfirmationService);

    // Map imported pricing from product-content.ts to PricingTier interface
    pricingTiers: PricingTier[] = PRODUCT_CONTENT.pricing.plans.map((plan: PricingPlan, index: number) => ({
        id: plan.tier,
        name: plan.name,
        monthlyPrice: plan.priceNumeric,
        annualPrice: Math.floor(plan.priceNumeric * 12 * 0.8), // 20% annual discount
        monthlyCredits: plan.credits,
        badge: plan.badge,
        badgeColor: plan.highlight ? 'blue' : 'purple',
        subtitle: plan.description,
        ctaText: plan.cta,
        ctaColor: plan.highlight ? 'blue' : 'purple',
        features: plan.features,
        isFeatured: plan.highlight
    }));

    constructor(
        private paymentService: PaymentService,
        public authService: AuthService,
        private router: Router,
        private route: ActivatedRoute,
        private subscriptionService: SubscriptionService
    ) { }

    ngOnInit() {
        this.loadUserData();
        this.loadCredits();

        // Handle query parameter from landing page (e.g., ?plan=builder)
        this.route.queryParams.subscribe(params => {
            const planId = params['plan'];
            if (planId) {
                const selectedTier = this.pricingTiers.find(t => t.id === planId);
                if (selectedTier) {
                    // Auto-scroll to pricing section if user came from landing page
                    setTimeout(() => {
                        const pricingSection = document.querySelector('.pricing-grid');
                        pricingSection?.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }, 500);
                }
            }
        });
    }

    loadUserData() {
        this.authService.user$.subscribe(user => {
            if (user) {
                this.userName = user.displayName || 'there';
            }
        });
    }

    loadCredits() {
        this.paymentService.getCredits().subscribe({
            next: (res) => {
                this.userCredits = res.credits || 0;
            },
            error: (err) => console.error('Failed to load credits', err)
        });
    }

    async purchasePlan(tier: PricingTier) {
        if (this.isProcessingPayment) return;

        // Check if user is authenticated
        const user = this.authService.currentUser();
        if (!user) {
            // Redirect to sign-in with return URL including the plan
            this.router.navigate(['/sign-in'], {
                queryParams: {
                    returnUrl: `/pricing?plan=${tier.id}`,
                    action: 'purchase'
                }
            });
            return;
        }

        this.isProcessingPayment = true;

        try {
            // Create Razorpay order with tier name
            const order = await this.paymentService.createOrder(tier.id).toPromise();

            // Get user details
            const userDetails = {
                name: user?.displayName || this.userName || 'Valued Customer',
                email: user?.email || '',
                contact: ''
            };

            // Initiate Razorpay payment (pass order and userDetails separately)
            await this.paymentService.initiatePayment(order, userDetails);

            // Success - reload credits and show modal
            this.confirmationService.confirm({
                title: 'Payment Successful!',
                message: `${tier.monthlyCredits} credits have been added to your account.`,
                confirmText: 'OK',
                onConfirm: () => { }
            });

            this.loadCredits();

            // Redirect to projects after purchase
            setTimeout(() => {
                this.router.navigate(['/projects']);
            }, 2000);

        } catch (err: any) {
            console.error('Payment failed:', err);
            this.confirmationService.confirm({
                title: 'Payment Failed',
                message: err?.error?.detail || 'Payment failed. Please try again.',
                confirmText: 'OK',
                onConfirm: () => { }
            });
        } finally {
            this.isProcessingPayment = false;
        }
    }

    getPrice(tier: PricingTier): number {
        return this.billingPeriod === 'annual' ? tier.annualPrice : tier.monthlyPrice;
    }

    getPriceLabel(tier: PricingTier): string {
        // Always show base monthly price for clarity
        // Annual savings shown separately in "Billed $X annually" text
        return `$${tier.monthlyPrice}`;
    }

    async purchaseSubscription(tier: PricingTier) {
        if (this.isProcessingPayment) return;

        const user = this.authService.currentUser();
        if (!user) {
            this.router.navigate(['/sign-in'], {
                queryParams: {
                    returnUrl: `/pricing?plan=${tier.id}`,
                    action: 'subscribe'
                }
            });
            return;
        }

        this.isProcessingPayment = true;

        try {
            await this.subscriptionService.createSubscription(tier.id, this.billingPeriod);
        } catch (err: any) {
            console.error('Subscription creation failed:', err);
            this.confirmationService.confirm({
                title: 'Subscription Failed',
                message: 'Failed to create subscription. Please try again.',
                confirmText: 'OK',
                onConfirm: () => { }
            });
            this.isProcessingPayment = false;
        }
    }
}
