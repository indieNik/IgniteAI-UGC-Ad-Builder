import { Routes } from '@angular/router';
import { EditorComponent } from './pages/editor/editor.component';
import { ProjectsComponent } from './pages/projects/projects.component';
import { LibraryComponent } from './pages/library/library.component';

import { authGuard } from './guards/auth.guard';
import { guestGuard } from './guards/guest.guard';
import { AdminGuard } from './guards/admin.guard';
import { AccountSettingsComponent } from './pages/account-settings/account-settings.component';
import { pendingChangesGuard } from './guards/pending-changes.guard';

export const routes: Routes = [
    // Marketing landing is on igniteai.in (Next.js)
    // App root redirects to sign-in for guests or projects for authenticated users
    { path: '', redirectTo: 'sign-in', pathMatch: 'full' },
    { path: 'sign-in', loadComponent: () => import('./pages/sign-in/sign-in.component').then(m => m.SignInComponent), canActivate: [guestGuard] },
    { path: 'onboarding', loadComponent: () => import('./pages/onboarding/onboarding.component').then(m => m.OnboardingComponent), canActivate: [authGuard] },
    { path: 'projects', component: ProjectsComponent, canActivate: [authGuard] },

    // Legal Pages
    { path: 'terms', loadComponent: () => import('./pages/legal/terms.component').then(m => m.TermsComponent) },
    { path: 'privacy', loadComponent: () => import('./pages/legal/privacy.component').then(m => m.PrivacyComponent) },
    { path: 'shipping', loadComponent: () => import('./pages/legal/shipping.component').then(m => m.ShippingComponent) },
    { path: 'contact', loadComponent: () => import('./pages/legal/contact.component').then(m => m.ContactComponent) },
    { path: 'cancellation-refund', loadComponent: () => import('./pages/legal/refunds.component').then(m => m.RefundsComponent) },

    // Google Cloud Startup Program Landing Page
    { path: 'google-cloud', loadComponent: () => import('./pages/google-cloud/google-cloud.component').then(m => m.GoogleCloudComponent) },

    { path: 'campaigns', component: EditorComponent, canActivate: [authGuard], canDeactivate: [pendingChangesGuard] }, // Main Editor
    { path: 'editor', component: EditorComponent, canDeactivate: [pendingChangesGuard] }, // Public Editor (interactions guarded)
    { path: 'campaigns/:id', component: EditorComponent, canActivate: [authGuard], canDeactivate: [pendingChangesGuard] },
    { path: 'library', component: LibraryComponent, canActivate: [authGuard] },
    { path: 'credits', component: AccountSettingsComponent, canActivate: [authGuard] },

    // Email & Community Pages
    { path: 'verify-email', loadComponent: () => import('./pages/verify-email/verify-email.component').then(m => m.VerifyEmailComponent) },
    { path: 'email-preferences', loadComponent: () => import('./pages/email-preferences/email-preferences.component').then(m => m.EmailPreferencesComponent), canActivate: [authGuard] },
    { path: 'community', loadComponent: () => import('./pages/community/community.component').then(m => m.CommunityComponent), canActivate: [authGuard] },
    { path: 'pricing', loadComponent: () => import('./pages/pricing/pricing.component').then(m => m.PricingComponent) },
    { path: 'examples', redirectTo: 'community', pathMatch: 'full' }, // Redirect examples to community

    {
        path: 'admin',
        loadChildren: () => import('./pages/admin/admin.routes').then(m => m.ADMIN_ROUTES),
        canActivate: [AdminGuard]
    },
    { path: '**', redirectTo: 'projects' }
];
