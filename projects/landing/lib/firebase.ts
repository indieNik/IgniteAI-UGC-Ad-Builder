import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider, signInWithPopup, createUserWithEmailAndPassword } from 'firebase/auth';

const firebaseConfig = {
    apiKey: "AIzaSyDmvzFcgDYAN-4GzZBNVsYINYymGhw_4qc",
    authDomain: "ignite-ai-01.firebaseapp.com",
    projectId: "ignite-ai-01",
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();
