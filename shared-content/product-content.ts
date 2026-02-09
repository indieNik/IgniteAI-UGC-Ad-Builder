/**
 * SINGLE SOURCE OF TRUTH for IgniteAI Content
 * 
 * This file is the canonical source for all product content, pricing, and promises.
 * Both the Next.js landing site and Angular app import from this.
 * 
 * DO NOT edit pricing or features in individual projects - update here instead.
 * 
 * ============================================================================
 * PRICING STRATEGY CONTEXT (January 2026)
 * ============================================================================
 * 
 * CURRENT MODEL: INR one-time credit purchases
 * - Starter: ₹499 (15 credits) = ~$6 USD
 * - Builder: ₹3,999 (100 credits) = ~$48 USD  
 * - Scale: ₹11,999 (500 credits) = ~$144 USD
 * 
 * KNOWN LIMITATIONS:
 * ⚠️ No duration-based pricing (negative margins on long videos possible)
 * ⚠️ No weighted credits (premium features can exceed COGS)
 * ⚠️ Non-expiring credits create deferred liability
 * ⚠️ INR-only signals "budget tool" to global market
 * 
 * STRATEGIC RECOMMENDATIONS (CFO Report Jan 23, 2026):
 * See: /docs/reports/pricing_strategy_2026.md
 * See: /.gemini/antigravity/brain/[conversation-id]/cfo_report_to_ceo.md
 * 
 * Recommended transition to USD subscription model:
 * - Starter: $49/month (40 credits, 1080p)
 * - Growth: $149/month (150 credits, 4K, 1 avatar clone)
 * - Agency: $497/month (600 credits, white-label, API)
 * 
 * Benefits: 85%+ margins (vs 30% current), recurring revenue, competitive alignment
 * 
 * STATUS: Pending CEO approval for USD subscription transition
 * ============================================================================
 */

export interface PricingPlan {
    name: string;
    price: string;
    priceNumeric: number;
    currency: 'USD' | 'INR';
    period: string;
    description: string;
    cta: string;
    credits: number;
    features: string[];
    highlight: boolean;
    tier: 'starter' | 'growth' | 'agency';
    badge?: string;
}

export interface Feature {
    icon: string;
    title: string;
    description: string;
}

export interface ProductContent {
    // Hero Section
    hero: {
        badge: string;
        headline: string;
        headlineHighlight: string;
        subheadline: string;
        ctaPrimary: string;
        ctaSecondary: string;
        supportingText: string;
        socialProof: string;
    };

    // Features
    features: Feature[];

    // Pricing
    pricing: {
        title: string;
        subtitle: string;
        plans: PricingPlan[];
        creditEstimate: string;
    };

    // Footer
    footer: {
        companyName: string;
        companyOwner: string;
        tagline: string;
        betaStatus: string;
    };
}

// ============================================================================
// CONTENT CONFIGURATION - EDIT HERE TO UPDATE EVERYWHERE
// ============================================================================

export const PRODUCT_CONTENT: ProductContent = {
    hero: {
        badge: 'New: Veo 2.0 Integration',
        headline: 'Stop Burning Cash on',
        headlineHighlight: 'Creative Fatigue',
        subheadline:
            'Generate short-form ad videos designed for iteration, testing, and scale. Create variations without shipping product or hiring actors.',
        ctaPrimary: 'Ignite My First Campaign',
        ctaSecondary: 'View Pricing',
        supportingText: 'Built for teams that iterate on creatives, not generate once.',
        socialProof: 'Trusted by 500+ D2C Founders',
    },

    features: [
        {
            icon: 'zap',
            title: 'Launch in Seconds',
            description:
                'Generate multi-scene ad videos in minutes. Refine individual scenes without starting over.',
        },
        {
            icon: 'banknote',
            title: 'Cheaper than UGC Creators',
            description:
                'Run variation tests at the cost of a single creator. Generate multiple hooks, angles, and CTAs from one brief.',
        },
        {
            icon: 'trending-up',
            title: 'Performance Optimized',
            description:
                'Hooks designed for performance campaigns. Lower CPA through rapid creative testing.',
        },
    ],

    pricing: {
        title: 'Simple, Transparent Pricing',
        subtitle: 'Scale your ads, not your overhead.',
        plans: [
            {
                name: 'Starter',
                price: '$49',
                priceNumeric: 49,
                currency: 'USD',
                period: 'per month',
                description: 'Perfect for pilots & testing.',
                cta: 'Start Free Trial',
                credits: 40,
                features: [
                    '40 Credits per Month',
                    'Refreshes Monthly',
                    'All Premium Features',
                    'Cancel Anytime',
                ],
                highlight: false,
                tier: 'starter',
                badge: 'Perfect to Start',
            },
            {
                name: 'Growth',
                price: '$149',
                priceNumeric: 149,
                currency: 'USD',
                period: 'per month',
                description: 'For growing brands.',
                cta: 'Start Growing',
                credits: 150,
                features: [
                    '150 Credits per Month',
                    'Refreshes Monthly',
                    '4K Resolution',
                    'Priority Support',
                ],
                highlight: true,
                tier: 'growth',
                badge: 'Most Popular',
            },
            {
                name: 'Agency',
                price: '$497',
                priceNumeric: 497,
                currency: 'USD',
                period: 'per month',
                description: 'High-volume agencies.',
                cta: 'Scale Your Agency',
                credits: 600,
                features: [
                    '600 Credits per Month',
                    'Refreshes Monthly',
                    'White-Label Mode',
                    'API Access',
                ],
                highlight: false,
                tier: 'agency',
                badge: 'Best Value',
            },
        ],
        creditEstimate: 'Estimate: 10-25 credits per video (varies by duration & features)',
    },

    footer: {
        companyName: 'IgniteAI',
        companyOwner: 'The Jaggery Point',
        tagline: 'Built on Google Cloud AI and scalable cloud infrastructure.',
        betaStatus: 'Currently in private beta',
    },
};

// Helper function to get pricing plan by tier
export function getPlanByTier(tier: 'starter' | 'growth' | 'agency'): PricingPlan | undefined {
    return PRODUCT_CONTENT.pricing.plans.find((p) => p.tier === tier);
}

// Helper to get all credit amounts
export function getAllCreditAmounts(): number[] {
    return PRODUCT_CONTENT.pricing.plans.map((p) => p.credits);
}
