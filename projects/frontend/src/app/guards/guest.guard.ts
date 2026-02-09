import { CanActivateFn, Router } from '@angular/router';
import { inject } from '@angular/core';
import { AuthService } from '../services/auth.service';
import { map, take, tap } from 'rxjs/operators';

export const guestGuard: CanActivateFn = (route, state) => {
    const authService = inject(AuthService);
    const router = inject(Router);

    return authService.user$.pipe(
        take(1),
        map(user => !user), // Allow if NO user (guest)
        tap(isGuest => {
            if (!isGuest) {
                // If user is logged in, redirect to returnUrl or projects
                const returnUrl = route.queryParams['returnUrl'] || '/projects';
                router.navigate([returnUrl]);
            }
        })
    );
};
