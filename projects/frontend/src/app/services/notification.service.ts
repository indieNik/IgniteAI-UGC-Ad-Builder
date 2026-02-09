import { Injectable } from '@angular/core';
import { Messaging, getToken, onMessage } from '@angular/fire/messaging';
import { Firestore, doc, setDoc } from '@angular/fire/firestore';
import { Observable } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class NotificationService {
    private readonly VAPID_KEY = 'BBCxff-7TW-7p5OIBNLli7Ba38ZYxPMjBNlgV_ZqeADAmzW701ZjsXBtzNmE-9yJnQ6E_7A-MOoItGM5rK-bQko'; // You'll need to generate this

    constructor(
        private messaging: Messaging,
        private firestore: Firestore
    ) { }

    /**
     * Request notification permission from the user
     * @returns Promise<boolean> - true if permission granted
     */
    async requestPermission(): Promise<boolean> {
        try {
            const permission = await Notification.requestPermission();
            console.log('Notification permission:', permission);
            return permission === 'granted';
        } catch (error) {
            console.error('Error requesting notification permission:', error);
            return false;
        }
    }

    /**
     * Get the current permission status without requesting
     * @returns NotificationPermission - 'granted', 'denied', or 'default'
     */
    getPermissionStatus(): NotificationPermission {
        return Notification.permission;
    }

    /**
     * Get FCM token and save it to Firestore
     * @param userId - The authenticated user's ID
     * @returns Promise<string | null> - The FCM token or null if failed
     */
    async getAndSaveToken(userId: string): Promise<string | null> {
        try {
            // Check if notifications are supported
            if (!('Notification' in window)) {
                console.warn('This browser does not support notifications');
                return null;
            }

            // Check permission
            if (Notification.permission !== 'granted') {
                console.warn('Notification permission not granted');
                return null;
            }

            // Register service worker if not already registered
            const registration = await this.registerServiceWorker();
            if (!registration) {
                console.error('Service worker registration failed');
                return null;
            }

            // Get FCM token
            const token = await getToken(this.messaging, {
                vapidKey: this.VAPID_KEY,
                serviceWorkerRegistration: registration
            });

            if (token) {
                // Save token to Firestore
                await this.saveTokenToFirestore(userId, token);

                return token;
            } else {
                console.warn('No FCM token available');
                return null;
            }
        } catch (error) {
            console.error('Error getting FCM token:', error);
            return null;
        }
    }

    /**
     * Register the Firebase Messaging service worker
     * @returns Promise<ServiceWorkerRegistration | null>
     */
    private async registerServiceWorker(): Promise<ServiceWorkerRegistration | null> {
        try {
            if ('serviceWorker' in navigator) {
                const registration = await navigator.serviceWorker.register('/firebase-messaging-sw.js', {
                    scope: '/'
                });

                // Wait for the service worker to be ready
                await navigator.serviceWorker.ready;

                return registration;
            }
            return null;
        } catch (error) {
            console.error('Service worker registration failed:', error);
            return null;
        }
    }

    /**
     * Save FCM token to Firestore user document
     * @param userId - The user's ID
     * @param token - The FCM token
     */
    private async saveTokenToFirestore(userId: string, token: string): Promise<void> {
        try {
            const userDocRef = doc(this.firestore, `users/${userId}`);
            await setDoc(userDocRef, {
                fcmToken: token,
                fcmTokenUpdatedAt: new Date().toISOString()
            }, { merge: true });

        } catch (error) {
            console.error('Error saving FCM token to Firestore:', error);
            throw error;
        }
    }

    /**
     * Listen for foreground messages (when app is open)
     * @returns Observable that emits notification payloads
     */
    listenForMessages(): Observable<any> {
        return new Observable(observer => {
            onMessage(this.messaging, (payload) => {
                console.log('Foreground message received:', payload);
                observer.next(payload);

                // Show notification even when app is in foreground
                if (payload.notification) {
                    this.showForegroundNotification(payload.notification, payload.data);
                }
            });
        });
    }

    /**
     * Display notification when app is in foreground
     * @param notification - Notification payload
     * @param data - Additional data
     */
    private showForegroundNotification(notification: any, data?: any): void {
        if (Notification.permission === 'granted') {
            const options: NotificationOptions = {
                body: notification.body,
                icon: notification.icon || '/favicon.ico',
                badge: '/favicon.ico',
                tag: data?.runId || 'igniteai-notification',
                requireInteraction: true,
                data: {
                    url: data?.clickAction || data?.url || '/'
                }
            };

            // Add image if available (using type assertion as 'image' is supported but not in TS types)
            if (notification.image) {
                (options as any).image = notification.image;
            }

            const notif = new Notification(notification.title, options);

            notif.onclick = (event) => {
                event.preventDefault();
                window.focus();
                if (data?.clickAction || data?.url) {
                    window.location.href = data.clickAction || data.url;
                }
                notif.close();
            };
        }
    }

    /**
     * Delete FCM token from Firestore (for logout/cleanup)
     * @param userId - The user's ID
     */
    async deleteToken(userId: string): Promise<void> {
        try {
            const userDocRef = doc(this.firestore, `users/${userId}`);
            await setDoc(userDocRef, {
                fcmToken: null,
                fcmTokenUpdatedAt: null
            }, { merge: true });

        } catch (error) {
            console.error('Error deleting FCM token from Firestore:', error);
        }
    }
}
