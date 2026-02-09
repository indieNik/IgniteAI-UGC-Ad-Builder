# Firebase Push Notifications - Validation & Debugging Guide

## Quick Validation Checklist

Follow these steps to verify your Firebase Push Notifications implementation:

---

## 1. Check Service Worker Registration

1. **Open your app**: https://igniteai.in
2. **Open Browser DevTools**: Press `F12` or `Cmd+Option+I`
3. **Go to Application tab** → **Service Workers**
4. **Verify**: You should see `firebase-messaging-sw.js` registered
   - ✅ Status should be "activated and running"
   - ❌ If not there, the service worker file wasn't deployed

**Screenshot what you see here**

---

## 2. Check Notification Permission

In DevTools Console, run:
```javascript
Notification.permission
```

**Expected results:**
- ✅ `"granted"` - Notifications will work
- ⚠️ `"default"` - User hasn't been prompted yet
- ❌ `"denied"` - User blocked notifications (need to reset in browser settings)

**What you got:** ___________

---

## 3. Check FCM Token Generation

In DevTools Console, run:
```javascript
// Check if token exists in localStorage or check network calls
console.log('Checking FCM setup...');
```

**Look for logs that say:**
- ✅ "FCM Token obtained: ..." 
- ✅ "Service worker registered: ..."
- ✅ "FCM token saved to Firestore for user: ..."

**If you see errors**, take a screenshot.

---

## 4. Manually Check Firestore

1. Go to: https://console.firebase.google.com/
2. Select project: `ignite-ai-01`
3. Go to **Firestore Database**
4. Navigate to: `users/{your-user-id}`
5. **Check for field**: `fcmToken`

**Is it there?**
- ✅ Yes, with a value like "eXxxx..." - Token was saved correctly
- ❌ No - Token generation or saving failed

---

## 5. Check Backend Deployment

Verify the backend has the notification code:

**Check HuggingFace Space:**
1. Go to: https://huggingface.co/spaces/indieNik/IgniteAI
2. Check **Files** tab
3. Verify these files exist:
   - `projects/backend/firebase_setup.py` - should have `send_notification()` function
   - `projects/backend/routers/generation.py` - should have notification code after line 226
   - `projects/backend/services/db_service.py` - should have `get_fcm_token()` method

**Are they there?** Yes / No

---

## 6. Test Backend Notification Function

If you have access to backend logs, check if notification was sent.

**In HuggingFace Space logs, look for:**
- ✅ "Successfully sent notification to user {user_id}. Message ID: ..."
- ⚠️ "No FCM token found for user {user_id}. Notification not sent."
- ❌ "Error sending notification to user {user_id}: ..."

**What you see:** ___________

---

## 7. Common Issues & Fixes

### Issue: Service Worker Not Registered
**Fix**: The `firebase-messaging-sw.js` file needs to be at the root of your domain.
- Check: https://igniteai.in/firebase-messaging-sw.js
- Should return the service worker file, not 404

### Issue: Permission Not Granted
**Fix**: Clear browser data and reload:
1. DevTools → Application → Storage → Clear site data
2. Reload page
3. Grant permission when prompted

### Issue: FCM Token Not Saved
**Fix**: Check browser console for errors during login
- Look for: "Error getting FCM token: ..."
- VAPID key might be incorrect

### Issue: Backend Not Sending Notifications
**Fix**: 
- Verify HuggingFace space is PUBLIC
- Check if backend has latest code deployed
- Verify Firebase Admin SDK is initialized

---

## 8. Manual Test Notification

To test if FCM is working at all, you can send a test notification from Firebase Console:

1. Go to: https://console.firebase.google.com/
2. Select: `ignite-ai-01`
3. Go to: **Cloud Messaging** → **Send test message**
4. Enter your FCM token (from Firestore)
5. Click "Test"

**Did you receive it?**
- ✅ Yes - FCM is working, issue is in backend integration
- ❌ No - FCM setup has issues

---

## Quick Debug Commands

Run these in your browser console on https://igniteai.in:

```javascript
// 1. Check if Firebase is initialized
console.log('Firebase initialized:', typeof firebase !== 'undefined');

// 2. Check current user
console.log('User:', await firebase.auth().currentUser);

// 3. Check notification permission
console.log('Notification permission:', Notification.permission);

// 4. Check service worker
navigator.serviceWorker.getRegistrations().then(regs => {
    console.log('Service workers:', regs.map(r => r.active?.scriptURL));
});
```

---

## Report Back

Please share:
1. **Service Worker status** (from step 1)
2. **Notification permission** (from step 2)
3. **FCM token in Firestore** (from step 4)
4. **Any errors in console** (screenshot)

This will help me pinpoint the exact issue!
