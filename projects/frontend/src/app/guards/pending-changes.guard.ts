import { inject } from '@angular/core';
import { CanDeactivateFn } from '@angular/router';
import { EditorComponent } from '../pages/editor/editor.component';
import { ConfirmationService } from '../services/confirmation.service';

export const pendingChangesGuard: CanDeactivateFn<EditorComponent> = async (component: EditorComponent) => {
    const confirmationService = inject(ConfirmationService);

    // Check if generation is active (either blocking start or background polling)
    if (component.isStarting || component.isBackgroundProcessing) {
        return await confirmationService.confirmAsync({
            title: 'Generation in Progress',
            message: 'Leaving this page might disconnect you from real-time updates.\n\nAre you sure you want to leave?',
            confirmText: 'Leave',
            cancelText: 'Stay'
        });
    }
    return true;
};
