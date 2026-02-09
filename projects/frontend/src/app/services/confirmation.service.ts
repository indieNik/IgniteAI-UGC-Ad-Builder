import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

export interface ConfirmationConfig {
    title: string;
    message: string;
    confirmText?: string;
    cancelText?: string;
    onConfirm: () => void;
    onCancel?: () => void;
}

@Injectable({
    providedIn: 'root'
})
export class ConfirmationService {
    private confirmationSubject = new BehaviorSubject<ConfirmationConfig | null>(null);
    confirmation$ = this.confirmationSubject.asObservable();

    confirm(config: ConfirmationConfig) {
        this.confirmationSubject.next({
            ...config,
            confirmText: config.confirmText || 'OK',
            cancelText: config.cancelText || 'Cancel'
        });
    }

    confirmAsync(config: Omit<ConfirmationConfig, 'onConfirm' | 'onCancel'>): Promise<boolean> {
        return new Promise((resolve) => {
            this.confirm({
                ...config,
                onConfirm: () => {
                    resolve(true);
                    this.close();
                },
                onCancel: () => {
                    resolve(false);
                    this.close();
                }
            });
        });
    }

    close() {
        this.confirmationSubject.next(null);
    }
}
