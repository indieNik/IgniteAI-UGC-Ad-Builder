// Firebase Cloud Messaging Service Worker
// This file must be at the root of the domain for FCM to work properly

importScripts('https://www.gstatic.com/firebasejs/10.14.1/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.14.1/firebase-messaging-compat.js');

// Initialize Firebase in the service worker
firebase.initializeApp({
    apiKey: "AI...",
    authDomain: "ignite-ai-01.firebaseapp.com",
    projectId: "ignite-ai-01",
    storageBucket: "ignite-ai-01.firebasestorage.app",
    messagingSenderId: "491013116254",
    appId: "1:491013116254:web:fb34bb1c311d308ea1ffcf",
    measurementId: "G-E2QRD1563P"
});

const messaging = firebase.messaging();

// Handle background notifications
messaging.onBackgroundMessage((payload) => {
    console.log('[firebase-messaging-sw.js] Received background message:', payload);

    const notificationTitle = payload.notification?.title || 'IgniteAI Notification';
    const notificationOptions = {
        body: payload.notification?.body || 'Your video is ready!',
        icon: payload.notification?.icon || '/favicon.ico',
        badge: '/favicon.ico',
        tag: payload.data?.runId || 'igniteai-notification',
        requireInteraction: true,
        data: {
            url: payload.data?.clickAction || payload.data?.url || '/'
        }
    };

    // Add image if provided
    if (payload.notification?.image || payload.data?.image) {
        notificationOptions.image = payload.notification?.image || payload.data?.image;
    }

    return self.registration.showNotification(notificationTitle, notificationOptions);
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
    console.log('[firebase-messaging-sw.js] Notification clicked:', event);
    
    event.notification.close();

    // Get the URL to open from notification data
    const urlToOpen = event.notification.data?.url || '/';

    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true })
            .then((clientList) => {
                // Check if there's already a window open
                for (let i = 0; i < clientList.length; i++) {
                    const client = clientList[i];
                    if (client.url.includes(self.registration.scope) && 'focus' in client) {
                        // Navigate to the URL and focus the window
                        return client.focus().then(client => {
                            if ('navigate' in client) {
                                return client.navigate(urlToOpen);
                            }
                        });
                    }
                }
                // If no window is open, open a new one
                if (clients.openWindow) {
                    return clients.openWindow(urlToOpen);
                }
            })
    );
});
