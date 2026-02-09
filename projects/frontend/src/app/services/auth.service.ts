import { Injectable, inject, signal } from '@angular/core';
import { Auth, GoogleAuthProvider, signInWithPopup, signInWithEmailAndPassword, createUserWithEmailAndPassword, sendPasswordResetEmail, signOut, User, user, authState, signInWithCustomToken } from '@angular/fire/auth';
import { Router } from '@angular/router';
import { Subscription } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class AuthService {
    private auth: Auth = inject(Auth);
    private router: Router = inject(Router);

    user$ = user(this.auth);
    authState$ = authState(this.auth);
    currentUser = signal<User | null>(null);

    private userSubscription: Subscription;

    constructor() {
        // Sync signal with observable
        this.userSubscription = this.user$.subscribe((u) => {
            this.currentUser.set(u);
        });
    }

    async loginWithGoogle() {
        const provider = new GoogleAuthProvider();
        try {
            const credential = await signInWithPopup(this.auth, provider);
            return credential.user;
        } catch (error) {
            console.error('Login failed', error);
            throw error;
        }
    }

    async loginWithEmail(email: string, password: string) {
        try {
            const credential = await signInWithEmailAndPassword(this.auth, email, password);
            return credential.user;
        } catch (error: any) {
            console.error('Email login failed', error);
            // Provide user-friendly error messages
            if (error.code === 'auth/user-not-found' || error.code === 'auth/wrong-password') {
                throw new Error('Invalid email or password');
            } else if (error.code === 'auth/invalid-email') {
                throw new Error('Invalid email address');
            } else if (error.code === 'auth/user-disabled') {
                throw new Error('This account has been disabled');
            }
            throw new Error('Failed to sign in. Please try again.');
        }
    }

    async loginWithCustomToken(token: string) {
        try {
            const credential = await signInWithCustomToken(this.auth, token);
            return credential.user;
        } catch (error: any) {
            console.error('Custom token login failed', error);
            throw new Error('Failed to sign in automatically. Please try signing in manually.');
        }
    }

    async signUp(email: string, password: string) {
        try {
            const credential = await createUserWithEmailAndPassword(this.auth, email, password);
            // Create user profile with 10 free credits
            await this.createUserProfile(credential.user);
            return credential.user;
        } catch (error: any) {
            console.error('Sign up failed', error);
            if (error.code === 'auth/email-already-in-use') {
                throw new Error('This email is already registered');
            } else if (error.code === 'auth/invalid-email') {
                throw new Error('Invalid email address');
            } else if (error.code === 'auth/weak-password') {
                throw new Error('Password should be at least 6 characters');
            }
            throw new Error('Failed to create account. Please try again.');
        }
    }

    async resetPassword(email: string) {
        try {
            await sendPasswordResetEmail(this.auth, email);
        } catch (error: any) {
            console.error('Password reset failed', error);
            if (error.code === 'auth/user-not-found') {
                throw new Error('No account found with this email');
            } else if (error.code === 'auth/invalid-email') {
                throw new Error('Invalid email address');
            }
            throw new Error('Failed to send reset email. Please try again.');
        }
    }

    private async createUserProfile(user: User) {
        // This will be implemented with Firestore
        // For now, just log the user creation
        console.log('User profile created for:', user.email, 'with 10 free credits');
        // TODO: Create Firestore document with user profile and credits
    }

    async logout() {
        await signOut(this.auth);
        this.router.navigate(['/']);
    }

    async getIdToken() {
        return this.currentUser()?.getIdToken();
    }
}
