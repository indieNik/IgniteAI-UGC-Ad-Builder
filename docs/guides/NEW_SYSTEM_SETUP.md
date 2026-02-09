# 🚀 New System Setup Checklist

Use this checklist when cloning the **IgniteAI Video Builder** repository onto a fresh machine (Mac/Linux/Windows WSL).

## 1. Prerequisites (System Level)
Before cloning, ensure you have these installed:

- [ ] **Git** (`git --version`)
- [ ] **Python 3.10+** (`python3 --version`)
- [ ] **Node.js 18+** (`node -v`)
- [ ] **FFmpeg** (Required for video stitching)
    - Mac: `brew install ffmpeg`
    - Linux: `sudo apt install ffmpeg`
    - Windows: `winget install ffmpeg`

## 2. Clone & secrets (The "Missing" Files)
These files are git-ignored for security. You must manually recreate them.

- [ ] **Clone Repository**
    ```bash
    git clone https://github.com/indieNik/AI-UGC-Ad-Video-Builder.git
    cd AI-UGC-Ad-Video-Builder
    ```

- [ ] **Create `.env` file** (in root)
    Copy the following structure and fill in your keys:
    ```bash
    # --- AI Providers ---
    OPENAI_API_KEY="sk-..."
    GEMINI_API_KEY="AIza..."
    ELEVENLABS_API_KEY="..."

    # --- Infrastructure ---
    # From Firebase Console > Storage
    FIREBASE_STORAGE_BUCKET="your-project-id.appspot.com"
    
    # From SendGrid Settings
    SENDGRID_API_KEY="SG..."
    SENDGRID_FROM_EMAIL="hello@yourdomain.com"
    
    # From Razorpay Dashboard
    RAZORPAY_KEY_ID="..."
    RAZORPAY_KEY_SECRET="..."
    ```

- [ ] **Add Service Account**
    1. Go to [Firebase Console](https://console.firebase.google.com/) > Project Settings > Service Accounts.
    2. Click **Generate new private key**.
    3. Save the file as `service-account.json`.
    4. Move it to: `projects/backend/service-account.json`.

## 3. Installation

- [ ] **Install CLI Tools** (One-time setup)
    ```bash
    # Installs gcloud and firebase-tools
    ./scripts/setup/setup-gcp-tools.sh
    
    # OR manually:
    # npm install -g firebase-tools
    # pip install gcloud
    ```

- [ ] **Install Backend Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

- [ ] **Install Frontend Dependencies**
    ```bash
    cd projects/frontend
    npm install
    cd ../..
    ```

## 4. Verification & Running

- [ ] **Test Backend Locally**
    ```bash
    python3 run.py
    # Expected: "Application startup complete." at http://0.0.0.0:8000
    ```

- [ ] **Test Frontend Locally**
    ```bash
    cd projects/frontend
    npm start
    # Expected: Opens http://localhost:4200
    ```

## 5. Deployment (Production)

- [ ] **Login to Clouds**
    ```bash
    gcloud auth login
    firebase login
    ```

- [ ] **Deploy All**
    ```bash
    ./scripts/deploy/deploy-all.sh
    ```

---

### 🆘 Troubleshooting
*   **"ffmpeg not found"**: Ensure it's in your system PATH.
*   **"Auth error" / "Token invalid"**: Check `service-account.json` matches the Firebase project in `.env`.

## 6. Architecture & Components

The project is a monorepo split into 3 parts:

| Component | Path | Tech Stack | Purpose |
| :--- | :--- | :--- | :--- |
| **Backend** | `projects/backend` | Python (FastAPI) | Orchestrates AI generation, queues, and DB. |
| **App** | `projects/frontend` | Angular 18 | The main dashboard where users create videos. |
| **Landing** | `projects/landing` | Next.js 16 | The marketing homepage (SEO optimized). |

## 7. Project Aliases & Scripts

The root `package.json` contains shortcuts to manage the entire stack:

| Command | Description |
| :--- | :--- |
| `npm run dev:app` | Starts the Angular App locally (`localhost:4200`). |
| `npm run dev:landing` | Starts the Next.js Landing locally (`localhost:3000`). |
| `npm run build:app` | Builds the Angular App for production. |
| `npm run build:landing` | Builds the Next.js Landing for production. |
| `npm run deploy:all` | Deploys **both** App and Landing to Firebase Hosting. |

### Firebase Aliases
Defined in `.firebaserc`:
*   `landing` target -> Deploys to `ignite-ai-01` (Marketing URL)
*   `app` target -> Deploys to `igniteai-app` (App URL)

## 8. Recommended Shell Aliases

You had these convenient aliases in your previous system's `~/.zshrc`. You might want to add them to your new machine:

```bash
# Add to ~/.zshrc or ~/.bashrc
alias deploy-be="cd ~/Projects/AI-Projects/AI\ UGC\ Ad\ Video\ Builder && ./scripts/deploy/deploy-backend-and-update-envs.sh"
alias deploy-fe="cd ~/Projects/AI-Projects/AI\ UGC\ Ad\ Video\ Builder && ./scripts/deploy/deploy-all.sh"
```
*(Make sure to update the path if you clone to a different directory)*

## 9. Files You Might Miss (Audit)

I scanned all `.gitignore` files. These files are **excluded** from Git and won't be on the new system unless you manually copy them:

| File / Folder | Purpose | Action Needed? |
| :--- | :--- | :--- |
| `frontend-sa-key.json` | Likely a development key. | **Skip** (Not used in production code). |
| `IgniteAI_Investor_Deck.pdf` | Pitch Deck. | **Copy** if you need the presentation. |
| `investor_deck_v1/` | Source files for deck. | **Copy** if you need the source. |
| `technical_deck_v1/` | Technical architecture slides. | **Copy** if you need the architecture docs. |
| `brand/designs/image.png` | Large assets (>500KB). | **Copy** if this is a master design file. |
| `.firebase/` | Firebase Cache. | **Skip** (Will be regenerated). |
| `.vercel/` | Vercel Config. | **Skip** (We use Firebase Hosting now). |



