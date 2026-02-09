import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';
import { ConfirmationService } from '../../services/confirmation.service';

@Component({
    selector: 'app-login',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './login.component.html',
    styleUrls: ['./login.component.css']
})
export class LoginComponent {
    auth = inject(AuthService);
    confirmationService = inject(ConfirmationService);

    async login() {
        try {
            await this.auth.loginWithGoogle();
        } catch (e) {
            this.confirmationService.confirm({
                title: 'Login Failed',
                message: 'Unable to sign in with Google. Please try again or check your browser console for details.',
                confirmText: 'OK',
                onConfirm: () => { }
            });
        }
    }

    logout() {
        this.auth.logout();
    }
}
