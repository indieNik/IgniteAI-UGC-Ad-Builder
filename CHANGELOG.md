# Changelog

## v2.2.0 - Community Reels & Model Updates (2026-02-09)

### 🎬 Community Reels Viewer
- **Full-Screen Experience**:
  - Implemented `ReelsViewerComponent` for TikTok/Reels-style video browsing
  - Auto-play on scroll using `IntersectionObserver` for seamless viewing
  - **Interactions**: Like, Share (Navigator API / Clipboard fallback), and View counts
  - **UI**: Glassmorphic controls, mobile-optimized gestures, and keyboard navigation (Arrow keys)

### 🤖 Generative Model Updates
- **Visual Intelligence**:
  - Added support for **Gemini 2.5 Flash** and **Gemini 3 Pro** in the Editor
  - Updated image generation options to use latest highly-capable models

### 🧹 Housekeeping
- **Repository Cleanup**:
  - Removed legacy `PRODUCT_DEMO` framework and assets to maintain a lean repository structure
  - Prepared workspace for next-generation demo generation framework

---

## v2.1.0 - Invoice System & PDF Integration (2026-01-24)

### 🧾 Invoice Generation
- **Automated PDFs**:
  - Implemented `xhtml2pdf` integration to generate professional PDF invoices on-the-fly
  - Invoices are automatically attached to "Payment Successful" emails
  - **Design**: Professional layout with IgniteAI branding (Indigo colors), clean typography, and robust "Classic Boxed" structure
- **Templates**:
  - `invoice.html`: Optimized strictly for PDF compatibility (table-based, no flexbox)
  - `invoice_body.html`: Modern email body with "Go to Dashboard" CTA

### 🛠️ Technical Improvements
- **Robust PDF Layout**:
  - Solved `xhtml2pdf` rendering engine bugs including nested table crashes and alignment shifting
  - Implemented non-collapsing spacer cells for pixel-perfect right alignment
- **Tooling**:
  - Added `scripts/utils/render_invoice.py` for HTML template previewing
  - Added `tests/manual/test_invoice_email.py` for end-to-end verification

### 🐛 Bug Fixes
- **PDF Alignment**: Fixed critical issue where "Total" columns would float left due to spacer collapse
- **Deployment**: Added missing dependencies (`xhtml2pdf`)

---

## v2.0.2 - Editor UI Refactoring & Mobile Polish (2026-01-24)

### 🎨 Editor Experience Overhaul
- **Action Button Interaction**:
  - Implemented 3-state design (Default/Hover/Active) for scene menu buttons
  - Fixed layout shift issues by wrapping actions in `.action-container`
  - Added conditional visibility: Action menu only appears when scene is finished (video ready)
- **Menu Improvements**:
  - Refactored hover-based actions to a persistent click-triggered dropdown
  - Improved positioning to prevent "garbled" overlap issues
  - Added global "click outside" listener to auto-close menus
- **Input & Scroling**:
  - Replaced single-line prompt input with resizeable `textarea` for better UX
  - Fixed horizontal scrolling on desktop storyboard to prevent card clipping
- **Terminology**: Changed empty scene status from "Ready" to "Draft" for clarity

### 📱 Projects & Layout Updates
- **Mobile Responsiveness**:
  - Moved mobile header to `absolute` positioning inside content area (fixes fixed-header overlap)
  - Adjusted top bar padding (80px) to accommodate hamburger menu
- **Project Dashboard**:
  - Removed redundant "Refresh" button (users can pull-to-refresh or reload)
  - Renamed sidebar navigation: "Projects" → "My Campaigns", "Campaigns" → "History"

### 🐛 Bug Fixes
- **Duplicate Headers**: Fixed an issue where `card-header` was duplicated in the DOM
- **CSS Glitch**: Fixed button layout jumping to the left when menu opened
- **Linting**: Resolved missing `socket`/`isConnected` types and CSS compatibility warnings

---

## v2.0.1 - Content Sync Validation & Fixes (2026-01-23)

### 🔍 Critical Issue Discovered & Fixed

**Problem**: Content sync system was functional but **unused**
- `tools/sync-content.js` successfully copied files
- Neither Next.js landing nor Angular app imported the synced files
- Both projects had **hardcoded** pricing/features arrays
- **Result**: Pricing drift (source had ₹499 INR, landing showed $49 USD)

### ✅ Fixes Applied

1. **Established True Single Source of Truth**
   - Updated `shared-content/product-content.ts` to USD monthly pricing ($49/$149/$497)
   - Changed tier names: `builder` → `growth`, `scale` → `agency`
   - Added `badge: 'Most Popular'` to Growth tier

2. **Refactored Landing Page** ([`projects/landing/app/page.tsx`](file:///Users/publicissapient/Projects/AI-Projects/AI%20UGC%20Ad%20Video%20Builder/projects/landing/app/page.tsx))
   - Removed ~60 lines of hardcoded pricing
   - Now imports `PRODUCT_CONTENT` from synced file
   - Features & pricing dynamically rendered from source
   - Removed legacy free tier conditional (TypeScript error fix)

3. **Refactored Angular Pricing** ([`projects/frontend/.../pricing.component.ts`](file:///Users/publicissapient/Projects/AI-Projects/AI%20UGC%20Ad%20Video%20Builder/projects/frontend/src/app/pages/pricing/pricing.component.ts))
   - Removed ~40 lines of hardcoded pricing tiers
   - Maps `PRODUCT_CONTENT.pricing.plans` to `PricingTier` interface
   - Calculates annual pricing (20% discount) dynamically
   - Removed broken coin image references

### 🎨 Design Improvements

- **Added**: "Most Popular" badge to Growth tier (matches landing page)
- **Fixed**: Broken coin images showing "🔥Credits" fallback text
- **Improved**: Visual hierarchy consistency between landing and app
- **Result**: Professional polish, clear user guidance to recommended tier

### 📊 Code Quality

**Before**:
- 258 lines of duplicated pricing code across 2 projects
- Source of truth file ignored
- Pricing drift risk on every manual update

**After**:
- 168 lines of DRY imports and mappings
- Net reduction: -90 lines (-35%)
- True single source of truth enforced
- Update once, sync everywhere

### 🐛 Bug Fixes

- **TypeScript Error**: Removed legacy `plan.tier === 'free'` check causing build failure
- **Missing Badge**: Growth tier now shows "Most Popular" badge in Angular app
- **Broken Images**: Removed `coinImage` references to non-existent SVG files
- **Dev Server Caching**: Created `fix-cache.sh` to clear `.next` and `.angular/cache`

### 📁 Files Modified

1. `shared-content/product-content.ts` - Updated pricing, added badge
2. `projects/landing/lib/product-content.ts` - Synced from source
3. `projects/landing/app/page.tsx` - Refactored to use imports
4. `projects/frontend/src/app/shared/product-content.ts` - Synced from source
5. `projects/frontend/.../pricing.component.ts` - Refactored to use imports

### 📚 Documentation Created

- **Content Sync Analysis** (`content_sync_analysis.md`) - Root cause investigation
- **Fix Walkthrough** (`content_sync_fix_walkthrough.md`) - Step-by-step changes
- **Design Review** (`final_design_review.md`) - Product designer perspective  
- **Testing Guide** (`testing_guide.md`) - Local verification steps
- **Deployment Summary** (`deployment_summary.md`) - Git details, next steps

### 🚀 Deployment

**Commit**: `7bd4be9`
**Message**: "fix: Establish true content sync single source of truth"
**Branch**: `main`
**Status**: ✅ Pushed to GitHub

### ⚠️ Breaking Changes

**Tier Names**:
- `builder` → `growth`
- `scale` → `agency`

**Impact**: Frontend query params (`?plan=builder`) still work (backward compatible mapping)

### 🎯 Impact

**User Experience**:
- Clear "Most Popular" badge guides users to Growth tier
- Visual consistency between landing and app builds trust
- No broken images improves perceived quality

**Developer Experience**:
- Edit pricing in ONE file (`shared-content/product-content.ts`)
- Sync script auto-copies to both projects
- TypeScript enforces consistency
- No more manual updates in 2+ places

**Business**:
- Reduced pricing update risk (single source)
- Improved conversion (clear tier recommendation)
- Professional polish (no broken elements)

### ✅ Verification

**Local Testing**: Dev servers refreshed with new content
**Visual Parity**: Landing and app pricing pages match perfectly
**TypeScript**: Build passes without errors
**Git**: Changes committed and pushed successfully

---

## v2.0.0 - Phase 2: Subscription Model Implementation (2026-01-23)

### 🎉 Major Release - Monthly Subscriptions Live

**Complete transition from one-time credits to monthly subscription model with scene-based pricing.**

### 💳 Subscription Infrastructure
- **Razorpay Integration**: Full subscription lifecycle management
  - Created `subscriptions.py` router with 5 endpoints
  - Monthly/annual billing support
  - Webhook handlers for automatic credit reset
  - Subscription status tracking and management
  
- **Subscription Plans**:
  - **Starter**: $49/month (40 credits/mo) | $470/year
  - **Growth**: $149/month (150 credits/mo) | $1,430/year
  - **Agency**: $497/month (600 credits/mo) | $4,770/year

### 🎬 Scene-Based Credit Model
- **Formula**: 2 credits per scene (Source of Truth)
- **Rationale**: Aligns perfectly with Veo's 6-second per scene constraint
- **Examples**:
  - 3 scenes (~15s video) = 6 credits
  - 6 scenes (~30s video) = 12 credits
  - Scene regeneration = 2 credits each
- **Weighted Features**:
  - Generative Background: +2 credits
  - Premium TTS: +1 credit
  - 4K Resolution: +1 credit

### 🏗️ Backend Updates
- **Database Layer**: Added subscription management methods to `db_service.py`
  - `create_subscription()`, `get_user_subscription()`
  - `get_subscription_by_razorpay_id()`, `update_subscription()`
  - `set_credits()` for monthly credit resets
  
- **Credit Calculation**: Complete rewrite
  - Removed duration-based tiers (10/13/18/25 credits)
  - Implemented scene-based formula (2 credits × num_scenes)
  - Updated `calculate_credit_cost()` and `calculate_estimated_cogs()`

- **Environment Configuration**:
  - Added 6 Razorpay plan IDs to `.config/cloud-run-env.yaml`
  - Webhook secret configuration
  - Cloud Run deployment script integration

### �� Frontend Implementation
- **Pricing Component Overhaul**:
  - Billing period toggle (Monthly/Annual) with "Save 20%" badge
  - Dynamic price display based on selected period
  - Updated tier interface: `monthlyPrice`, `annualPrice`, `monthlyCredits`
  - New `SubscriptionService` for API integration
  
- **UI/UX Updates**:
  - Subscription-focused copy ("per month" vs "pay-once")
  - Monthly credit refresh messaging
  - Cancel anytime functionality
  - Clean billing toggle design with glassmorphic styling

- **Editor Updates**:
  - Added `numScenes` property (default: 3 scenes)
  - Updated `getCreditCost()` to accept scene count
  - Fixed template compilation errors

### 🏷️ Tier Renaming
- **Builder → Growth**: Mid-tier for growing brands
- **Scale → Agency**: High-volume agency tier
- **Consistency**: Updated across backend, frontend, landing page, and docs

### 📊 Strategic Alignment
- **Margins**: Maintained healthy ~58% gross margins
- **Competitive Position**: Aligned with market ($49-$497/month)
- **Predictability**: Monthly recurring revenue model
- **Documentation**: Comprehensive guides created

### 📚 Documentation Created
- **Razorpay Setup Guide**: Step-by-step plan creation in dashboard
- **Cloud Run Deployment Checklist**: Critical env var configuration steps
- **Scene-Based Pricing**: Source of truth for credit calculations
- **Implementation Plan**: Updated with subscription roadmap

### 🔄 Breaking Changes
- **Credit Calculation**: Now requires `num_scenes` instead of `target_duration`
- **Tier Names**: `builder` → `growth`, `scale` → `agency`
- **Purchase Flow**: Redirects to Razorpay subscription checkout
- **Environment Variables**: 6 new `RAZORPAY_PLAN_*` vars required for Cloud Run

### ⚙️ Configuration
New environment variables required:
```bash
RAZORPAY_PLAN_STARTER_MONTHLY=plan_xxxxx
RAZORPAY_PLAN_STARTER_ANNUAL=plan_xxxxx
RAZORPAY_PLAN_GROWTH_MONTHLY=plan_xxxxx
RAZORPAY_PLAN_GROWTH_ANNUAL=plan_xxxxx  
RAZORPAY_PLAN_AGENCY_MONTHLY=plan_xxxxx
RAZORPAY_PLAN_AGENCY_ANNUAL=plan_xxxxx
RAZORPAY_WEBHOOK_SECRET=whsec_xxxxx
```

### 📄 Files Changed
**Backend** (8 files):
- `routers/subscriptions.py` (NEW)
- `routers/generation.py` - Scene-based credits
- `routers/payments.py` - Tier renaming
- `services/db_service.py` - Subscription methods
- `main.py` - Router registration
- `.config/cloud-run-env.yaml` - Plan IDs

**Frontend** (5 files):
- `services/subscription.service.ts` (NEW)
- `pages/pricing/pricing.component.ts` - Subscription model
- `pages/pricing/pricing.component.html` - Billing toggle
- `pages/pricing/pricing.component.css` - Toggle styles
- `pages/editor/editor.component.ts` - Scene-based display

**Landing** (1 file):
- `app/page.tsx` - Subscription pricing

**Strategic Docs** (4 files):
- `pricing_strategy_2026.md` - Updated with scene model
- `scene_based_pricing_source_of_truth.md` (NEW)
- `razorpay_setup_guide.md` (NEW)
- `cloud_run_deployment_checklist.md` (NEW)

### 🚀 Deployment
- Committed to GitHub: 3 commits
  - `feat: Implement subscription model with scene-based pricing`
  - `chore: Sync product content to subscription model`
  - `docs: Add Razorpay plan IDs to Cloud Run config`
- Cloud Run environment variables configured
- Ready for production deployment

### ✅ Testing Status
- Subscription creation endpoint functional
- Webhook handlers implemented (pending live test)
- Credit calculation verified (scene-based)
- Frontend UI tested locally

### 📈 Success Metrics
- **Margins**: 58% average (sustainable)
- **Pricing**: Market-aligned ($49-$497/mo)
- **UX**: Simpler (scenes vs seconds)
- **Predictability**: No negative unit economics

---

## v1.6.0 - Pricing Strategy Analysis (2026-01-23)

### 📊 Strategic Analysis
- **Pricing Strategy Deep Dive**
  - Comprehensive CFO analysis of competitor pricing and cost structure
  - Identified critical margin vulnerabilities in current INR one-time pricing model
  - Analyzed COGS breakdown: Current "Buy" stack ($5.61/video, 30% margin) vs Target "Build" stack ($0.32/video, 85%+ margin)
  - Competitive positioning assessment vs Arcads, MakeUGC, HeyGen, Synthesia, Fliki, Affogato

### 📈 Key Findings
- **Margin Risk**: Current pricing lacks duration-based and weighted credits, creating negative unit economics on videos >45 seconds
- **Competitive Misalignment**: Priced 87% below market standards ($6-144 one-time vs $49-220/month competitors)
- **Opportunity**: Transition to USD subscription model could increase LTV by 300%+ and margins from 30% → 85%

### 📝 Documentation Created
- **CFO Report to CEO**: Comprehensive financial analysis and strategic recommendations
  - Current vs recommended pricing comparison
  - Margin analysis (Buy vs Build infrastructure stack)
  - Competitive positioning matrix
  - Financial projections (Month 1-12 scenarios)
  - 4-phase implementation roadmap
  - Risk assessment and mitigation strategies
  
- **Pricing Strategy 2026**: Detailed strategic planning document
  - Recommended USD subscription tiers: $49/$149/$497 monthly
  - Weighted credits system design
  - Self-hosted infrastructure investment plan ($2K/mo GPU + $8-12K/mo engineer)
  - Agency white-label feature roadmap
  - Success metrics and monitoring dashboard

### 🔧 Code Documentation
- **Updated `shared-content/product-content.ts`**
  - Added strategic context documenting current pricing limitations
  - Linked to CFO recommendations and pricing strategy docs
  - Noted known risks (no duration pricing, no weighted credits, non-expiring credits)
  - Documented recommended future state (pending CEO approval)

### ⚠️ Status
- **No pricing changes implemented** - this release is analysis and planning only
- Actual pricing transition to USD subscription model requires:
  1. CEO approval on strategic direction
  2. Board approval for Reserved GPU infrastructure investment
  3. Separate implementation plan for backend/frontend changes
  
### 📁 Files Created/Updated
- `docs/reports/pricing_strategy_2026.md` - Strategic planning document
- `.gemini/antigravity/brain/[conversation]/cfo_report_to_ceo.md` - CFO analysis
- `shared-content/product-content.ts` - Added strategic documentation
- `GEMINI.md` - Added pricing strategy evolution learnings (pending)
- `CHANGELOG.md` - This entry

### 🎯 Recommended Next Steps
1. CEO review of pricing strategy recommendations
2. Customer survey (50 active users) for pricing feedback validation
3. If approved: Implement Phase 1 (duration + weighted credits) immediately
4. If approved: Begin Phase 2 (USD subscription) for Feb 15, 2026 launch

---

## v1.5.2 - Public Editor & Guest Interaction (2026-01-21)

### 🚀 New Features
- **Public Editor Route**:
  - Extracted `/editor` as a public route accessible to non-logged-in users
  - Implemented "Unlock Creator Studio" modal for guest users upon interaction
  - Seamless Google Sign-in integration directly from the modal
- **SEO Optimization**:
  - Added dynamic SEO Title and Meta Description for the Editor page

### 🔐 Security & UX
- **Guest Interaction Shield**:
  - Non-intrusive "Unlock Creator Studio" modal instead of forced redirects
  - Verified security guards on all sensitivity actions (generate, download, regenerate) to prevent bypass
  - Transparent overlay pattern for intuitive "try before you buy" feel

## v1.5.1 - Critical Security Fix (2026-01-20)

### 🔐 Security Vulnerability Patched
- **Payment Verification**:
  - Fixed critical vulnerability where client-side amount was trusted for credit allocation
  - Implemented server-side `razorpay_client.payment.fetch()` verification
  - Credits now calculated based on *actual* paid amount from Razorpay
  - Added rigorous payment status checks (must be `captured`)

### 🐛 Bug Fixes
- **Razorpay Receipt Length**:
  - Fixed `receipt` field exceeding 40-character limit
  - New format: `{tier[:4]}_{timestamp}_{short_uid}` (e.g., `buil_1705758000_abc123`)
  - Prevents API errors for users with long IDs

## v1.5.0 - Free Tier Signup Implementation (2026-01-19)

### 🎁 Free Tier Launch
- **Landing Page Integration**
  - Replaced "Starter Pack" (₹499) with "Free Tier" offering 10 credits
  - Firebase SDK integration for Google OAuth on Next.js landing page
  - Auto-redirect to app with secure custom Firebase tokens
  - Seamless sign-in flow: Landing Page → Backend → App (auto-authenticated)

### 🔐 Backend Free Tier System
- **New Endpoint**: `POST /api/auth/free-signup`
  - Handles Google OAuth and email/password signups
  - Awards 10 free credits immediately for Google users
  - Awards 10 credits upon email verification for email signups
  - Generates custom Firebase tokens for auto-signin
  
- **Security Measures**
  - IP-based rate limiting (3 signups per day per IP)
  - Disposable email blocking (9+ domains blocked)
  - Email verification required for email/password signups
  - Firestore IP logging for abuse tracking

- **Email Templates**
  - New `free_tier_verification.html` template
  - Highlights credit reward in verification emails
  - SendGrid integration for email delivery

### 🎨 Frontend Auto-Signin
- **New Method**: `loginWithCustomToken()` in AuthService
  - Consumes custom tokens from URL query parameters
  - Auto-signs in users from landing page signup
  - Cleans up URL to remove token from browser history
  
- **Smart Routing**
  - New users (`?new=true`) → `/onboarding`
  - Existing users → `/dashboard`
  - Failed auth → `/sign-in` (with error handling)

### 🐛 Critical Fixes
- Fixed missing `email-validator` package causing backend crashes
- Fixed missing `uvicorn` package preventing FastAPI server startup
- Restored complete `requirements.txt` (accidentally removed `langgraph`, `openai`, `pandas`, etc.)
- Fixed custom token return type handling (bytes vs string)
- Optimized startup by loading health check before heavy routers

### 📦 Dependencies Added
```txt
email-validator>=2.1.0  # For pydantic EmailStr validation
uvicorn                  # FastAPI ASGI server
pyd antic[email]          # Email validation support
```

### 🚀 Deployment
- Backend: https://igniteai-backend-254654034407.us-central1.run.app
- Landing: https://igniteai.com
- App: https://app.igniteai.in

### 📝 Documentation
- Created comprehensive walkthrough.md with implementation details
- Updated GEMINI.md with free tier signup learnings
- Documented all debugging steps and fixes

### ⚡ User Experience
- **Signup Time**: ~3 seconds (Google OAuth)
- **Auto-Signin**: Seamless (brief flash of sign-in page before redirect)
- **Credit Award**: Instant for Google, upon email verification for email signups
- **Onboarding**: Automatic for first-time users

---

## v1.4.0 - GCP Backend Migration (2026-01-18)

### 🚀 Infrastructure Migration
- **Backend Platform Change**
  - Migrated from Hugging Face Spaces to Google Cloud Run
  - Service URL: https://igniteai-backend-254654034407.us-central1.run.app
  - 50-70% faster cold starts (<1s vs ~10-30s)
  - Auto-scaling: 0-10 instances based on traffic
  - Resources: 4Gi memory, 2 CPUs, 900s timeout

### 🔐 Security Improvements
- **Secret Manager Integration**
  - All API keys (Gemini, OpenAI, ElevenLabs, SendGrid) now stored in GCP Secret Manager
  - Service account granted `secretmanager.secretAccessor` role
  - Secrets mounted as environment variables in Cloud Run

### 📦 Configuration
- **Environment Variables**
  - YAML-based configuration for variables with special characters
  - 12 config values including Firebase, Razorpay, SendGrid settings
  - Proper escaping handled for business address and other complex values

### 🐳 Docker Changes
- Updated Dockerfile for Cloud Run compatibility
  - Port changed from 7860 → 8080
  - Fixed USER command capitalization
  - Added PORT environment variable support

### 💰 Cost Optimization
- Using GCP free tier credits (₹25,110 remaining, 85 days)
- Pay-per-request pricing vs hourly billing
- Expected cost: ~₹15-20/month (well within free tier)
- Auto-scales to zero = no idle costs

### 📜 Deployment Scripts
- `setup-gcp-tools.sh` - Install gcloud and Firebase CLI
- `configure-gcp.sh` - Authenticate and configure GCP project
- `deploy-cloud-run.sh` - Build Docker image, push to GCR, deploy to Cloud Run
- `set-cloud-run-env.sh` - Configure API keys via Secret Manager
- `cloud-run-env.yaml` - Environment variables configuration file

### ⚠️ Known Limitations
- Backend requires authenticated access due to organization IAM policies
- Returns 403 Forbidden for unauthenticated public requests
- Frontend will use service account authentication

### 📝 Documentation
- Added comprehensive GCP migration learnings to GEMINI.md
- Updated architecture diagrams in README (pending frontend migration)

---

## v1.3.0 - Pricing Section Overhaul (2026-01-17)

### 🎯 New Features
- **Conversion-Optimized Pricing Page**
  - Dedicated `/pricing` route with pixel-perfect dark UI matching design mock
  - Three tiers: Starter (₹499/15 credits), Builder (₹3,999/100 credits), Scale (₹11,999/500 credits)
  - Glass-morphism card design with gradient CTAs and glow effects
  - 3D coin stack graphics for visual appeal
  - Mobile-first responsive grid (stacks vertically on <1024px)
  - "Most Popular" badge on Builder Pack with blue accent
  - Footer credit estimate: "1-5 credits / video (varies by length)"

### 🔧 Backend Changes
- **Razorpay Integration Updates**
  - Changed from USD to INR currency
  - Tier-based order creation (accepts `tier` string instead of raw amounts)
  - Updated `PRICING_TIERS` dictionary with exact paise amounts
  - Payment verification now matches tier amounts with 1 rupee tolerance
  - Returns `credits_added` and `new_balance` in payment response

### 🎨 UI/UX Improvements
- Added "Pricing" navigation link in sidebar (⚡ zap icon)
- Fixed account-settings component compatibility with new payment service
- Consistent purple/blue color scheme across all pricing elements
- Added current balance widget (fixed position, bottom-right)

### 📦 Assets
- Generated and integrated 3D coin stack graphics (transparent PNGs)
- Copied to `assets/images/` for Builder and Scale packs

### 🐛 Bug Fixes
- Fixed payment service signature to accept tier names
- Updated account-settings buyPlan to map old tier names to new backend format

---

All notable changes to **IgniteAI** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.36] - 2026-01-17

### Fixed
- **Campaign Name Display**: Fixed campaign name from modal not appearing in editor header
  - Root cause: `resetCampaign()` was being called unconditionally in else block, resetting `projectTitle` to "New Campaign" after query param was read
  - Solution: Added conditional check to skip `resetCampaign()` if `name` query parameter exists
  - Campaign names entered in modal now properly display in header input field
  - Editing campaign name also works correctly now

## [1.2.35] - 2026-01-17

### Added
- **Campaign Name Input Modal**: Users can now name campaigns when clicking "New Campaign" button
  - Modal appears with text input field before navigating to editor
  - Optional input with placeholder "e.g., Summer Sale 2024"
  - Defaults to "New Campaign" if left blank
  - Cancel button to close without creating
  - Glassmorphism styling matching app design
  - Smooth slide-up animation with backdrop blur
  - Enter key support for quick submission
  - Query parameter passing to editor (`/campaigns?name=...`)

### Changed
- "New Campaign" button now opens modal instead of direct navigation
- Editor component reads `name` query parameter to set initial campaign title

### Technical
- Added `FormsModule` to projects component for ngModel support
- Implemented modal state management with `showNameModal` and `newCampaignName` properties
- Added `openNewCampaignModal()`, `closeNameModal()`, and `createCampaign()` methods
- CSS animations (fadeIn, slideUp) for modal transitions
- Query parameter validation (only applies to new campaigns, not existing loads)

## [1.2.34] - 2026-01-17

###Fixed
- **Tour Guide**: Fixed screen getting stuck after completing tour guide
  - Properly restores body overflow state (`hidden` for app pages)
  - Removes `tour=true` URL parameter to prevent accidental restarts
  - Added session-based guard to prevent tour from auto-restarting on page reload

### Added
- **Documentation**: Created CHANGELOG.md for release tracking

---

## [1.2.29] - 2026-01-17

### Added
- **Scene Loading Indicators:** Per-scene loading states showing "Generating [SceneName]..." during campaign generation
- **Contextual Button Messaging:** Generate button text adapts based on campaign status and credit balance
  - "Generate Campaign" (new user with credits)
  - "Generate New Campaign" (existing campaign + credits)
  - "Upgrade to Create More" (existing campaign, no credits)
- **Credit Badge Component:** Reusable component for displaying user credits
- **Onboarding Redirect:** New users automatically redirected to `/onboarding` page after sign-up
- **Community Video Preview Modal:** Clicking play button opens video in modal instead of navigating away

### Fixed
- **Community Play Button:** Fixed play button opening share dialog - now opens preview modal for public videos
- **Mobile Header Overlap:** Credit badge no longer overlaps with buttons on mobile (hidden in header, accessible via sidebar)
- **Icon Alignment:** Dollar sign icon in credit badge now perfectly vertically aligned with count

### Improved
- Credit badge visibility: Displayed in desktop sidebar and mobile sidebar drawer
- Mobile UX: Cleaner header design on small screens
- Button messaging clarity for users with/without credits
- Video viewing experience: Modal with controls, like/share buttons, proper view tracking

---

## [1.2.26] - 2026-01-15

### Added
- **Community Module**: Full community showcase with likes, views, and sharing
- **Email System**: Automated email notifications for video completion
- **Asset Library**: Display all campaign assets grouped by campaign ID

### Fixed
- **Mobile Layout**: Fixed sidebar crushing content on mobile (280px → overlay pattern)
- **Timestamp Format**: Standardized to seconds across frontend/backend
- **Event Bubbling**: Added `$event.stopPropagation()` to nested click handlers

### Changed
- **Cache Strategy**: Implemented localStorage caching for history (5-min expiry)
- **UI Polish**: Updated "Anonymous" to "Community Member" for better UX

---

## [1.2.25] - 2026-01-14

### Added
- **Authentication**: Full sign-up, forgot password, and email verification flows
- **Credit System**: New users start with 10 free credits
- **Email Preferences**: User-configurable email notification settings

###Fixed
- **Sign-In Flow**: Replaced static orb with pulsating loader animation

---

## [1.2.0] - 2026-01-13

### Added
- **Brand Kit**: Upload and manage brand colors, logos, and fonts
- **Asset Preview**: Auto-play videos on hover in Asset Library
- **Tour Guide**: Interactive onboarding tour for first-time users

### Fixed
- **Assets Library**: Now properly updates after campaign generation
- **Scrolling**: Improved scroll behavior across all pages

---

## Earlier Releases

For release notes prior to v1.2.0, see commit history in the repository.
