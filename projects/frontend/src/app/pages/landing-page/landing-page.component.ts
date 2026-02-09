import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, Router, ActivatedRoute } from '@angular/router';
import { LucideAngularModule } from 'lucide-angular';
import { AuthService } from '../../services/auth.service';
import { take } from 'rxjs/operators';
import { APP_VERSION } from '../../version';

@Component({
    selector: 'app-landing-page',
    standalone: true,
    imports: [CommonModule, RouterLink, LucideAngularModule],
    templateUrl: './landing-page.component.html',
    styleUrls: ['./landing-page.component.css', './landing-page-premium.css']
})
export class LandingPageComponent {
    private router = inject(Router);
    private authService = inject(AuthService);
    appVersion = APP_VERSION;

    pricingPlans = [
        {
            name: 'Starter Pack',
            price: '₹499',
            period: 'one-time',
            description: 'Try IgniteAI risk-free, no commitment.',
            cta: 'Try 15 Credits',
            currency: 'INR',
            features: [
                '<lucide-icon name="circle-dollar-sign" class="gold-icon" style="width: 14px; height: 14px;"></lucide-icon> 15 Credits',
                '<lucide-icon name="film" style="width: 14px; height: 14px;"></lucide-icon> Create Short-Form Videos',
                'Credits Never Expire',
                'No Subscription Required'
            ],
            isPopular: false,
            highlight: false,
            action: 'pricing',
            tier: 'starter'
        },
        {
            name: 'Builder Pack',
            price: '₹3,999',
            period: 'pay-once',
            description: 'Experiment, test hooks, iterate.',
            cta: 'Get 100 Credits',
            currency: 'INR',
            features: [
                '<lucide-icon name="circle-dollar-sign" class="gold-icon" style="width: 14px; height: 14px;"></lucide-icon> 100 Credits',
                '<lucide-icon name="film" style="width: 14px; height: 14px;"></lucide-icon> Optimized for Reels & Shorts',
                'HD Exports',
                'Credits Roll Over Forever'
            ],
            isPopular: true,
            highlight: true,
            action: 'pricing',
            tier: 'builder'
        },
        {
            name: 'Scale Pack',
            price: '₹11,999',
            period: 'pay-once',
            description: 'High-volume brands & agencies.',
            cta: 'Get 500 Credits',
            currency: 'INR',
            features: [
                '<lucide-icon name="circle-dollar-sign" class="gold-icon" style="width: 14px; height: 14px;"></lucide-icon> 500 Credits',
                '<lucide-icon name="film" style="width: 14px; height: 14px;"></lucide-icon> Priority Generation Speed',
                'Video Vibe Matching',
                'Priority Support'
            ],
            isPopular: false,
            highlight: false,
            action: 'pricing',
            tier: 'scale'
        }
    ];

    features = [
        {
            icon: 'zap',
            title: 'Launch in Seconds',
            desc: 'Generate multi-scene ad videos in minutes. Refine individual scenes without starting over.'
        },
        {
            icon: 'banknote',
            title: 'Cheaper than UGC Creators',
            desc: 'Run variation tests at the cost of a single creator. Generate multiple hooks, angles, and CTAs from one brief.'
        },
        {
            icon: 'trending-up',
            title: 'Performance Optimized',
            desc: 'Hooks designed for performance campaigns. Lower CPA through rapid creative testing.'
        }
    ];

    scrollToPricing() {
        const el = document.getElementById('pricing');
        if (el) el.scrollIntoView({ behavior: 'smooth' });
    }

    handleCta(action: string) {
        if (action === 'contact') {
            window.location.href = 'mailto:business@thejaggerypoint.com';
            return;
        }

        if (action === 'pricing') {
            // Navigate to the new pricing page
            this.router.navigate(['/pricing']);
            return;
        }

        if (action === 'payment' || action === 'build') {
            this.authService.user$.pipe(take(1)).subscribe(user => {
                let target = '/onboarding';
                let queryParams: any = {};

                if (action === 'payment') {
                    // Find the tier from the clicked plan
                    const clickedPlan = this.pricingPlans.find(p => p.action === 'payment' && (p as any).tier);
                    if (clickedPlan) {
                        queryParams.plan = (clickedPlan as any).tier;
                    }
                } else if (action === 'build') {
                    target = '/campaigns';
                }

                if (user) {
                    this.router.navigate([target], { queryParams });
                } else {
                    this.router.navigate(['/sign-in'], {
                        queryParams: {
                            returnUrl: target,
                            ...queryParams
                        }
                    });
                }
            });
        }
    }
}
