import { Injectable, inject } from '@angular/core';
import { CanActivate, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { AdminService } from '../services/admin.service';
import { map, switchMap, take, catchError } from 'rxjs/operators';
import { of } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class AdminGuard implements CanActivate {
    private auth = inject(AuthService);
    private adminService = inject(AdminService);
    private router = inject(Router);

    canActivate() {
        return this.auth.authState$.pipe(
            take(1),
            switchMap(async (user) => {
                if (!user) {
                    this.router.navigate(['/']);
                    return false;
                }

                try {
                    return await this.adminService.checkAdmin();
                } catch (e) {
                    this.router.navigate(['/']);
                    return false;
                }
            })
        );
    }
}
