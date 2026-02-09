import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { AuthService } from '../services/auth.service';
import { switchMap, take } from 'rxjs/operators';
import { from } from 'rxjs';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
    const authService = inject(AuthService);

    // Skip token for auth-related calls if needed, or if no user.
    // We try to get the token. 
    return from(authService.getIdToken()).pipe(
        switchMap(token => {
            if (token) {
                const cloned = req.clone({
                    setHeaders: {
                        Authorization: `Bearer ${token}`
                    }
                });
                return next(cloned);
            }
            return next(req);
        })
    );
};
