import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, ActivatedRoute } from '@angular/router';
import { LucideAngularModule } from 'lucide-angular';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-onboarding',
  standalone: true,
  imports: [CommonModule, LucideAngularModule, FormsModule],
  template: `
    <div class="onboarding-container" [class.loading]="isTransitioning">
      <!-- Step 1: Survey -->
      <div *ngIf="step === 'survey'" class="survey-step animate-fade-in">
        <div class="survey-header">
          <div class="progress-bar-container">
            <div class="progress-bar" style="width: 33%;"></div>
          </div>
          <h1 class="text-gradient">How do you plan to use IgniteAI?</h1>
          <p class="subtext">We'll tailor features and AI tools to your goals</p>
        </div>

        <div class="survey-grid">
          <div *ngFor="let option of options" 
               class="survey-card glass-panel" 
               (click)="selectOption(option.id)">
            <div class="card-icon">
              <lucide-icon [name]="option.icon" style="width: 24px; height: 24px;"></lucide-icon>
            </div>
            <h3>{{ option.title }}</h3>
            <p>{{ option.desc }}</p>
          </div>
        </div>
      </div>

      <!-- Step 2: Action Screen (Step 0) -->
      <div *ngIf="step === 'action'" class="action-step animate-fade-in">
        <div class="survey-header">
          <div class="progress-bar-container">
            <div class="progress-bar" style="width: 66%;"></div>
          </div>
          <h1 class="text-gradient">Let's build your first ad</h1>
          <p class="subtext">Upload a product image and pick a style to start igniting.</p>
        </div>

        <div class="action-card glass-panel">
          <div class="action-grid">
            <!-- Left: Image Upload -->
            <div class="upload-section">
              <div class="drop-zone" (click)="fileInput.click()" 
                   [style.backgroundImage]="previewUrl ? 'url(' + previewUrl + ')' : ''"
                   [class.has-image]="previewUrl">
                <input #fileInput type="file" (change)="onFileSelected($event)" style="display:none" accept="image/*">
                <lucide-icon *ngIf="!previewUrl" name="camera" class="camera-icon"></lucide-icon>
                <p *ngIf="!previewUrl">Upload Product Image</p>
              </div>
            </div>

            <!-- Right: Controls -->
            <div class="controls-section">
                <div class="input-group">
                    <label>What's the vibe?</label>
                    <input type="text" [(ngModel)]="prompt" placeholder="e.g. Trendy sneakers on a neon street..." class="glass-input">
                </div>

                <div class="input-group">
                    <label>Campaign Style</label>
                    <div class="preset-chips">
                        <button *ngFor="let preset of presets" 
                                [class.active]="selectedPreset === preset.id"
                                (click)="selectedPreset = preset.id"
                                class="chip">
                            {{ preset.label }}
                        </button>
                    </div>
                </div>

                <button class="btn-neon full-width" (click)="generateFirstAd()" [disabled]="!prompt || isUploading">
                    <span>{{ isUploading ? 'Preparing Engine...' : 'Ignite My First Ad' }}</span>
                    <lucide-icon name="zap" class="icon-sm" *ngIf="!isUploading"></lucide-icon>
                </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Step 3: Transition / Loading -->
      <div *ngIf="step === 'loading'" class="loading-step animate-fade-in">
        <div class="loader-content">
          <div class="spinner-ring"></div>
          <p class="loading-text">{{ loadingMessage }}</p>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .onboarding-container {
      min-height: 100vh;
      background: #050505;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 40px 20px;
    }

    .survey-step, .action-step {
      width: 100%;
      max-width: 1000px;
      text-align: center;
    }

    .survey-header {
      margin-bottom: 40px;
    }

    .progress-bar-container {
      width: 120px;
      height: 4px;
      background: rgba(255,255,255,0.1);
      border-radius: 2px;
      margin: 0 auto 30px;
      overflow: hidden;
    }

    .progress-bar {
      height: 100%;
      background: var(--accent-primary);
      transition: width 0.5s ease;
    }

    .survey-header h1 {
      font-size: 2.8rem;
      margin-bottom: 15px;
      font-weight: 800;
      letter-spacing: -1px;
    }

    .survey-header .subtext {
      color: var(--text-secondary);
      font-size: 1.1rem;
    }

    .survey-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 20px;
    }

    .survey-card {
      padding: 30px;
      cursor: pointer;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      border: 1px solid rgba(255,255,255,0.05);
      background: rgba(255,255,255,0.02);
      text-align: left;
    }

    .survey-card:hover {
      background: rgba(255,255,255,0.05);
      border-color: var(--accent-primary);
      transform: translateY(-5px);
      box-shadow: 0 15px 30px rgba(0,0,0,0.4);
    }

    .card-icon {
      width: 48px;
      height: 48px;
      border-radius: 12px;
      background: rgba(99, 102, 241, 0.1);
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 20px;
      color: var(--accent-primary);
    }

    .survey-card h3 {
      font-size: 1.2rem;
      margin-bottom: 8px;
      color: var(--text-primary);
    }

    .survey-card p {
      color: var(--text-muted);
      font-size: 0.9rem;
      line-height: 1.5;
    }

    /* Action Step */
    .action-card {
        padding: 40px;
        text-align: left;
    }

    .action-grid {
        display: grid;
        grid-template-columns: 350px 1fr;
        gap: 40px;
    }

    .upload-section .drop-zone {
        height: 100%;
        min-height: 350px;
        border: 2px dashed rgba(255,255,255,0.1);
        border-radius: 20px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.3s ease;
        background-color: rgba(255,255,255,0.02);
        background-position: center;
        background-size: cover;
    }

    .upload-section .drop-zone:hover {
        border-color: var(--accent-primary);
        background-color: rgba(99, 102, 241, 0.05);
    }

    .upload-section .drop-zone.has-image {
        border-style: solid;
        border-color: var(--accent-primary);
    }

    .camera-icon {
        width: 48px;
        height: 48px;
        color: var(--text-muted);
        margin-bottom: 15px;
    }

    .controls-section {
        display: flex;
        flex-direction: column;
        gap: 25px;
    }

    .input-group {
        display: flex;
        flex-direction: column;
        gap: 10px;
    }

    .input-group label {
        color: var(--text-secondary);
        font-size: 0.9rem;
        font-weight: 500;
    }

    .preset-chips {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }

    .chip {
        padding: 8px 16px;
        border-radius: 100px;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        color: var(--text-secondary);
        font-size: 0.85rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .chip:hover {
        background: rgba(255,255,255,0.1);
    }

    .chip.active {
        background: var(--accent-primary);
        color: white;
        border-color: var(--accent-primary);
    }

    /* Loading Step */
    .loading-step {
      text-align: center;
    }

    .loader-content {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 25px;
    }

    .spinner-ring {
      width: 60px;
      height: 60px;
      border: 4px solid rgba(99, 102, 241, 0.1);
      border-top-color: var(--accent-primary);
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }

    .loading-text {
      font-size: 1.3rem;
      color: var(--text-primary);
      font-weight: 400;
    }

    @keyframes spin {
      to { transform: rotate(360deg); }
    }

    .animate-fade-in {
      animation: fadeIn 0.6s ease-out forwards;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .full-width { width: 100%; }

    @media (max-width: 1024px) {
        .action-grid {
            grid-template-columns: 1fr;
            gap: 20px;
        }
        .upload-section .drop-zone {
            min-height: 200px;
        }
    }
  `]
})
export class OnboardingComponent implements OnInit {
  private router = inject(Router);
  private route = inject(ActivatedRoute);
  private apiService = inject(ApiService);

  step: 'survey' | 'action' | 'loading' = 'survey';
  isTransitioning = false;
  selectedPlan: string | null = null;
  loadingMessage = 'Tailoring your experience...';

  // Action Step State
  prompt = '';
  selectedPreset = 'sales';
  selectedFile: File | null = null;
  previewUrl: string | null = null;
  isUploading = false;

  presets = [
    { id: 'sales', label: 'High-Energy Sales', duration: 15, mood: 'Energetic' },
    { id: 'lifestyle', label: 'Premium Lifestyle', duration: 30, mood: 'Relaxed' },
    { id: 'talking', label: 'Founder Story', duration: 15, mood: 'Professional' }
  ];

  options = [
    { id: 'marketing', icon: 'bar-chart', title: 'Marketing & Ads', desc: 'Create ads that convert without studio costs' },
    { id: 'social', icon: 'smartphone', title: 'Social Media Growth', desc: 'Create viral TikTok and Reels daily' },
    { id: 'freelance', icon: 'monitor', title: 'Freelance Projects', desc: 'Deliver high-quality videos with better margins' },
    { id: 'personal', icon: 'sparkles', title: 'Personal Brand', desc: 'Experiment, create, and share for fun' }
  ];

  ngOnInit() {
    this.route.queryParams.subscribe(params => {
      this.selectedPlan = params['plan'] || null;
    });
  }

  selectOption(id: string) {
    console.log('User selected onboarding option:', id);
    this.isTransitioning = true;

    setTimeout(() => {
      this.step = 'action';
      this.isTransitioning = false;
    }, 800);
  }

  onFileSelected(event: any) {
    const file = event.target.files[0];
    if (file) {
      this.selectedFile = file;
      const reader = new FileReader();
      reader.onload = (e: any) => this.previewUrl = e.target.result;
      reader.readAsDataURL(file);
    }
  }

  generateFirstAd() {
    this.isUploading = true;
    this.step = 'loading';
    this.loadingMessage = 'Igniting your creative engine...';

    const preset = this.presets.find(p => p.id === this.selectedPreset);
    const config = {
      duration: preset?.duration || 15,
      music_mood: preset?.mood || 'Energetic',
      preset: this.selectedPreset,
      tour: 'true'
    };

    if (this.selectedFile) {
      this.apiService.uploadImage(this.selectedFile).subscribe({
        next: (res) => {
          this.navigateToEditor(res.run_id, res.path, config);
        },
        error: (err) => {
          console.error('Upload failed', err);
          this.navigateToEditor(undefined, undefined, config);
        }
      });
    } else {
      this.navigateToEditor(undefined, undefined, config);
    }
  }

  private navigateToEditor(runId?: string, imagePath?: string, config?: any) {
    const queryParams: any = {
      prompt: this.prompt,
      config: JSON.stringify(config)
    };
    if (runId) queryParams.runId = runId;
    if (imagePath) queryParams.imagePath = imagePath;
    if (this.selectedPlan) queryParams.plan = this.selectedPlan;

    setTimeout(() => {
      this.router.navigate(['/campaigns'], { queryParams });
    }, 1500);
  }
}

