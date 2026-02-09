import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';
import { Router, ActivatedRoute } from '@angular/router';

@Component({
    selector: 'app-sign-in',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './sign-in.component.html',
    styleUrl: './sign-in.component.css'
})
export class SignInComponent {
    private authService = inject(AuthService);
    private router = inject(Router);
    private route = inject(ActivatedRoute);

    authMethod: 'google' | 'email' = 'google';
    isSignUp = false; // Toggle between sign-in and sign-up
    isLoading = false;
    error = '';
    successMessage = '';

    // Email/Password form fields
    email = '';
    password = '';
    showPassword = false;
    rememberMe = false;

    async signIn() {
        this.isLoading = true;
        this.error = '';
        this.successMessage = '';
        try {
            await this.authService.loginWithGoogle();
            const returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/projects';
            this.router.navigate([returnUrl]);
        } catch (err: any) {
            console.error('Sign in error:', err);
            this.error = 'Failed to sign in with Google. Please try again.';
        } finally {
            this.isLoading = false;
        }
    }

    async signInWithEmail() {
        if (!this.email || !this.password) {
            this.error = 'Please enter both email and password.';
            return;
        }

        this.isLoading = true;
        this.error = '';
        this.successMessage = '';
        try {
            if (this.isSignUp) {
                await this.authService.signUp(this.email, this.password);
                this.successMessage = 'Account created successfully! Setting up your workspace...';
                // Redirect new users to onboarding
                setTimeout(() => this.router.navigate(['/onboarding']), 1000);
            } else {
                await this.authService.loginWithEmail(this.email, this.password);
                // Existing users go to requested page or projects
                const returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/projects';
                setTimeout(() => this.router.navigate([returnUrl]), 1000);
            }
        } catch (err: any) {
            console.error('Email sign in error:', err);
            this.error = err.message || 'Failed to sign in. Please check your credentials.';
        } finally {
            this.isLoading = false;
        }
    }

    async forgotPassword() {
        if (!this.email) {
            this.error = 'Please enter your email address first.';
            return;
        }

        this.isLoading = true;
        this.error = '';
        this.successMessage = '';
        try {
            await this.authService.resetPassword(this.email);
            this.successMessage = 'Password reset email sent! Check your inbox.';
        } catch (err: any) {
            console.error('Password reset error:', err);
            this.error = err.message || 'Failed to send reset email.';
        } finally {
            this.isLoading = false;
        }
    }

    toggleSignUpMode() {
        this.isSignUp = !this.isSignUp;
        this.error = '';
        this.successMessage = '';
    }
}
