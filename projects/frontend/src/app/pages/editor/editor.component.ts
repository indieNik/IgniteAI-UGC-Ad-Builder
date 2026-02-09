import { Component, OnInit, OnDestroy, ViewChild, ElementRef, HostListener, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule, ActivatedRoute, Router } from '@angular/router';
import { Meta, Title } from '@angular/platform-browser';
import { LucideAngularModule } from 'lucide-angular';
import { ApiService } from '../../services/api.service';
import { HistoryService } from '../../services/history.service';
import { LoaderComponent } from '../../components/loader/loader.component';
import { PaymentService } from '../../services/payment.service';
import { AuthService } from '../../services/auth.service';
import { ConfirmationService } from '../../services/confirmation.service';

@Component({
    selector: 'app-editor',
    standalone: true,
    imports: [CommonModule, FormsModule, RouterModule, LucideAngularModule, LoaderComponent],
    templateUrl: './editor.component.html',
    styleUrls: ['./editor.component.css']
})
export class EditorComponent implements OnInit {
    // Economy
    userCredits: number = 0;
    get COST_PER_GEN(): number {
        return this.getCreditCost(this.numScenes);
    }

    // State
    prompt: string = '';
    uploadedImage: File | null = null;
    uploadedImageUrl: string | null = null;
    isDragging = false;
    // UX REFACTOR: Split generating state
    isStarting = false; // Blocking (Validation, Upload, Queueing)
    isBackgroundProcessing = false; // Non-blocking (Polling)
    // Deprecated: isGenerating (kept for compat if needed, but logic moves to above)
    get isGenerating(): boolean { return this.isStarting; }

    isLoadingRun = false;
    isFailed = false;
    sceneLoadingStates: { [key: string]: boolean } = {}; // Track per-scene loading
    generationStatus = '';

    // Mobile Properties Panel State
    isPropertiesOpen = false;

    // Regeneration State
    regenerationPrompt: string = '';
    sceneToRegenerate: string | null = null;
    showRegenerateModal = false;

    logs: { timestamp: Date, message: string }[] = [];
    showLogs = false;
    friendlyStatus = '';
    finalVideoUrl: string | null = null;
    videoVersions: { url: string, label: string }[] = [];
    sceneAssets: { [key: string]: string } = {};
    sceneScripts: { [key: string]: string } = {};
    failureReason: string | null = null;

    fallbackUsed: boolean = false;


    // Preview Modal Logic
    previewModalVisible = false;
    selectedVideoUrl: string | null = null;
    selectedSceneName = '';

    private socket: WebSocket | null = null;

    // Connection State
    isConnected = false;

    // Scene Menu State
    activeMenuScene: string | null = null;

    @HostListener('window:beforeunload', ['$event'])
    unloadNotification($event: any) {
        if (this.isStarting || this.isBackgroundProcessing) {
            $event.returnValue = true;
        }
    }

    @HostListener('document:click', ['$event'])
    onDocumentClick(event: MouseEvent) {
        if (this.activeMenuScene) {
            this.closeSceneMenu();
        }
    }

    toggleSceneMenu(scene: string, event: Event) {
        event.stopPropagation();
        if (this.activeMenuScene === scene) {
            this.activeMenuScene = null;
        } else {
            this.activeMenuScene = scene;
        }
    }

    closeSceneMenu() {
        this.activeMenuScene = null;
    }
    isCheckingHealth = true;
    connectionFailed = false;
    retryCount = 0;
    readonly MAX_RETRIES = 3;

    // Guest Modal State
    showSignInModal = false;

    // Config State
    duration: number = 15;
    videoModel: string = 'veo-3.1-fast-generate-preview';
    imageModel: string = 'gemini-2.5-flash-image';
    aspectRatio: string = '9:16';
    musicMood: string = 'Energetic';
    customMusicPrompt: string = '';

    get projectedCost(): number {
        return this.getCreditCost(this.numScenes);
    }

    // Scene Configuration (Source of Truth for pricing)
    get numScenes(): number {
        return Math.floor(this.duration / 5);
    }

    websiteUrl: string = '';
    projectTitle: string = 'Awesome Campaign';
    Math = Math;


    currentRunId: string | null = null;
    isDownloading = false;

    // Tour State
    showTour = false;
    currentTourStep = 0;
    tourBoxStyle: any = {};
    backdropStyle: any = {};
    tourSteps = [
        {
            title: 'Your Creative Engine',
            content: 'Describe your vision here. AI will craft scripts and scenes based on your prompt.',
            target: '.ignition-box'
        },
        {
            title: 'Storyboard Flow',
            content: 'Your campaign is broken into Hook, Feature, and CTA. You can preview or regenerate them individually.',
            target: '.storyboard-flow'
        },
        {
            title: 'Fine-Tuning',
            content: 'Adjust aspect ratios, AI models, and background music to match your brand vibe.',
            target: '.properties-panel'
        },
        {
            title: 'Ready for Launch?',
            content: 'Click here to generate your final video. Each generation costs 10 <lucide-icon name="circle-dollar-sign" style="width: 14px; height: 14px; vertical-align: middle;" class="gold-icon"></lucide-icon>.',
            target: '.floating-action .btn-neon'
        }
    ];

    // Presets
    presets = [
        { id: 'sales', label: 'High-Energy Sales', duration: 15, mood: 'Energetic', description: 'Fast-paced, high conversions.' },
        { id: 'lifestyle', label: 'Premium Lifestyle', duration: 30, mood: 'Relaxed', description: 'Cinematic, brand focused.' },
        { id: 'talking', label: 'Founder Story', duration: 15, mood: 'Professional', description: 'Direct and authentic.' }
    ];
    selectedPresetId: string = 'sales';

    /**
     * Calculate credit cost based on video duration.
     * Matches backend tiered pricing logic.
     */
    // State
    features = {
        generative_background: false,
        premium_tts: false,
        '4k_resolution': false
    };

    /**
     * Calculate credit cost based on scene count and features.
     * Source of Truth: 2 credits per scene
     * 
     * Examples:
     * - 3 scenes = 6 credits
     * - 6 scenes = 12 credits
     * - Scene + Gen BG = 6 + 2 = 8 credits
     */
    getCreditCost(numScenes: number): number {
        // Base: 2 credits per scene
        let cost = numScenes * 2;

        // Weighted Features
        if (this.features.generative_background) cost += 2;
        if (this.features.premium_tts) cost += 1;
        if (this.features['4k_resolution']) cost += 1;
        if (this.imageModel === 'gemini-3-pro-image-preview') cost += 1; // Premium Image Model

        return cost;
    }

    private confirmationService = inject(ConfirmationService);

    constructor(
        private apiService: ApiService,
        private historyService: HistoryService,
        private route: ActivatedRoute,
        private router: Router,
        private paymentService: PaymentService,
        public authService: AuthService,
        private title: Title,
        private meta: Meta
    ) { }

    ngOnInit() {
        // SEO for Public Editor Route
        this.title.setTitle('AI Video Editor - IgniteAI');
        this.meta.updateTag({ name: 'description', content: 'Create viral UGC ad videos in seconds with IgniteAI\'s free AI video editor. No design skills needed.' });

        this.checkBackendHealth();
        this.loadCredits();

        // 1. Check Route and Query Params
        this.route.params.subscribe(params => {
            const runIdParam = params['id'];

            this.route.queryParams.subscribe(queryParams => {
                // Check for campaign name from "New Campaign" modal
                if (queryParams['name'] && !runIdParam) {
                    this.projectTitle = queryParams['name'];
                }

                if (runIdParam) {
                    this.loadRun({ run_id: runIdParam, status: 'unknown' });
                } else if (queryParams['runId']) {
                    // Coming from Onboarding Step 0
                    this.currentRunId = queryParams['runId'];
                    this.prompt = queryParams['prompt'] || '';
                    if (queryParams['imagePath']) {
                        // We use a simplified preview for newly triggered onboarding runs
                        this.uploadedImageUrl = 'assets/placeholder.svg';
                    }

                    if (queryParams['config']) {
                        try {
                            const config = JSON.parse(queryParams['config']);
                            this.duration = config.duration || 15;
                            this.musicMood = config.music_mood || 'Energetic';
                            this.selectedPresetId = config.preset || 'sales';
                        } catch (e) {
                            console.error('Failed to parse config from query params', e);
                        }
                    }

                    // Auto-trigger if prompt and image/runId are there
                    if (this.prompt && this.currentRunId) {
                        this.isBackgroundProcessing = true;
                        this.startLogStream(this.currentRunId);
                        this.pollStatus(this.currentRunId);
                    }
                } else if (queryParams['tour'] === 'true') {
                    // Only start tour if not already completed in this session
                    const tourCompleted = sessionStorage.getItem('igniteai_tour_completed');
                    if (!tourCompleted) {
                        this.setupDummyProject();
                        this.startTour();
                    } else {
                        // Tour already completed, just clear the param and show normal editor
                        const url = new URL(window.location.href);
                        url.searchParams.delete('tour');
                        window.history.replaceState({}, '', url.toString());
                        this.resetCampaign();
                    }
                } else {
                    // Only reset if no name query param was provided
                    if (!queryParams['name']) {
                        this.resetCampaign();
                    }
                }
            });
        });

        // 3. Fallback to service selection
        this.historyService.selectedRun$.subscribe(run => {
            if (run && !this.route.snapshot.params['id'] && !this.route.snapshot.queryParams['runId']) {
                this.loadRun(run);
            }
        });
    }

    setupDummyProject() {
        this.projectTitle = 'Premium Coffee Ad';
        this.prompt = 'High-end close up shot of roasting coffee beans, steam rising, followed by a lifestyle shot of a professional enjoying a cup in a minimalist office.';
        this.uploadedImageUrl = 'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&q=80&w=600'; // Dummy high quality image
        this.duration = 15;
        this.selectedPresetId = 'lifestyle';
        this.musicMood = 'Relaxed';
    }

    applyPreset(presetId: string) {
        const preset = this.presets.find(p => p.id === presetId);
        if (preset) {
            this.selectedPresetId = presetId;
            this.duration = preset.duration;
            this.musicMood = preset.mood;
        }
    }



    startTour() {
        if (window.innerWidth < 1024) return; // Desktop only

        // Clear the completion flag when manually starting tour
        sessionStorage.removeItem('igniteai_tour_completed');

        this.showTour = true;
        this.currentTourStep = 0;
        setTimeout(() => this.updateTourPosition(), 100);
    }

    nextTourStep() {
        if (this.currentTourStep < this.tourSteps.length - 1) {
            this.currentTourStep++;
            this.updateTourPosition();
        } else {
            this.closeTour();
        }
    }

    updateTourPosition() {
        const step = this.tourSteps[this.currentTourStep];
        const element = document.querySelector(step.target);

        if (element) {
            // Ensure element is visible
            element.scrollIntoView({ behavior: 'smooth', block: 'center' });

            setTimeout(() => {
                const rect = element.getBoundingClientRect();
                const cardWidth = 400;
                const cardHeight = 300; // Estimated max height
                const padding = 20;

                // Default: Try to show below and centered
                let left = rect.left + (rect.width / 2) - (cardWidth / 2);
                let top = rect.bottom + padding;

                // SPECIAL: If it's the Properties Panel (sidebar), place card to the left of it
                if (step.target === '.properties-panel') {
                    left = rect.left - cardWidth - 40; // Increased padding to 40
                    top = rect.top + 20;
                }

                // Vertical boundary safety (General)
                if (top + cardHeight > window.innerHeight - padding) {
                    top = rect.top - cardHeight - padding;
                }
                if (top < padding) top = padding;

                // Horizontal boundary safety (General)
                if (left < padding) left = padding;
                if (left + cardWidth > window.innerWidth - padding) {
                    left = window.innerWidth - cardWidth - padding;
                }

                this.tourBoxStyle = {
                    'top': top + 'px',
                    'left': left + 'px'
                };

                // Hole Punch Logic (clip-path)
                const holePadding = 10;
                const holeLeft = rect.left - holePadding;
                const holeTop = rect.top - holePadding;
                const holeRight = rect.right + holePadding;
                const holeBottom = rect.bottom + holePadding;

                // Path for the hole: 
                // outer rectangle (clockwise) + inner hole (counter-clockwise)
                this.backdropStyle = {
                    'clip-path': `polygon(
                        0% 0%, 0% 100%, 100% 100%, 100% 0%, 0% 0%,
                        ${holeLeft}px ${holeTop}px, 
                        ${holeRight}px ${holeTop}px, 
                        ${holeRight}px ${holeBottom}px, 
                        ${holeLeft}px ${holeBottom}px, 
                        ${holeLeft}px ${holeTop}px
                    )`
                };

                // Spotlight feedback
                document.querySelectorAll('.tour-spotlight-item').forEach(el => el.classList.remove('tour-spotlight-item'));
                element.classList.add('tour-spotlight-item');
            }, 300); // Wait for scroll to settle
        } else {
            // Fallback to center
            this.tourBoxStyle = {
                'position': 'fixed',
                'top': '50%',
                'left': '50%',
                'transform': 'translate(-50%, -50%)'
            };
            this.backdropStyle = {};
        }
    }

    closeTour() {
        console.log('Closing tour guide and resetting state...');
        this.showTour = false;
        this.backdropStyle = {};
        this.tourBoxStyle = {};
        this.currentTourStep = 0;

        // Remove spotlight classes
        document.querySelectorAll('.tour-spotlight-item').forEach(el => {
            el.classList.remove('tour-spotlight-item');
        });

        // Restore body overflow to app's default state (app pages should be 'hidden')
        // The app.component manages this based on route, so we restore to hidden for app pages
        document.body.style.overflow = 'hidden';
        document.body.style.overscrollBehaviorY = 'none';

        // Clean up URL parameter to prevent tour from restarting on reload
        const url = new URL(window.location.href);
        if (url.searchParams.has('tour')) {
            url.searchParams.delete('tour');
            window.history.replaceState({}, '', url.toString());
        }

        // Mark tour as completed in session to prevent auto-restart
        sessionStorage.setItem('igniteai_tour_completed', 'true');
    }

    loadCredits() {
        this.paymentService.getCredits().subscribe({
            next: (res) => {
                this.userCredits = res.credits;
            },
            error: (err) => console.error('Failed to load credits', err)
        });
    }

    resetCampaign() {
        this.prompt = '';
        this.uploadedImage = null;
        this.uploadedImageUrl = null;
        this.uploadedImageUrl = null;
        this.currentRunId = null;
        this.isStarting = false;
        this.isBackgroundProcessing = false;
        this.isLoadingRun = false;
        this.isFailed = false;
        this.sceneAssets = {};
        this.logs = [];
        this.showLogs = false;
        this.friendlyStatus = '';
        this.finalVideoUrl = null;
        this.videoVersions = [];
        this.generationStatus = '';
        this.projectTitle = 'New Campaign';
        this.customMusicPrompt = '';
        this.duration = 15;
        this.aspectRatio = '9:16';
        this.videoModel = 'veo-3.1-fast-generate-preview';
        this.imageModel = 'gemini-2.5-flash-image';
        this.musicMood = 'Energetic';
        this.websiteUrl = '';
    }

    get sceneList(): string[] {
        const numScenes = this.numScenes;
        const allIds = ["Hook", "Feature", "Lifestyle", "Benefit", "SocialProof", "CTA"];
        if (numScenes <= 3) return ["Hook", "Feature", "CTA"];
        const core = allIds.slice(0, numScenes - 1);
        return [...core, "CTA"];
    }

    loadHistory() {
        // Handled by service
    }

    loadRun(run: any) {
        if (!run.run_id) return;
        this.currentRunId = run.run_id;
        this.isLoadingRun = true;
        this.currentRunId = run.run_id;
        this.isLoadingRun = true;
        this.generationStatus = `Resuming Run ID: ${run.run_id}`;

        // RESUME AS BACKGROUND PROCESS
        if (run.status === 'running' || run.status === 'queued') {
            this.isBackgroundProcessing = true;
            this.startLogStream(run.run_id);
        }

        // Always call pollStatus to load campaign data into editor
        // pollStatus will handle completed vs running campaigns appropriately
        console.log('[Editor] Loading campaign:', run.run_id, 'Status:', run.status);
        this.pollStatus(run.run_id);
    }

    checkBackendHealth() {
        this.apiService.checkHealth().subscribe({
            next: () => {
                this.isConnected = true;
                this.isCheckingHealth = false;
                this.connectionFailed = false;
                this.retryCount = 0;
            },
            error: () => {
                this.isConnected = false;
                if (this.retryCount >= this.MAX_RETRIES) {
                    this.connectionFailed = true;
                    this.isCheckingHealth = false;
                } else {
                    this.isCheckingHealth = true;
                    this.connectionFailed = false;
                    this.retryCount++;
                    setTimeout(() => this.checkBackendHealth(), 3000);
                }
            }
        });
    }

    retryConnection() {
        this.retryCount = 0;
        this.connectionFailed = false;
        this.isCheckingHealth = true;
        this.checkBackendHealth();
    }

    onDragOver(event: DragEvent) {
        event.preventDefault();
        event.stopPropagation();
        this.isDragging = true;
    }

    onDragLeave(event: DragEvent) {
        event.preventDefault();
        event.stopPropagation();
        this.isDragging = false;
    }

    onDrop(event: DragEvent) {
        event.preventDefault();
        event.stopPropagation();
        this.isDragging = false;
        if (event.dataTransfer?.files.length) {
            this.handleFile(event.dataTransfer.files[0]);
        }
    }

    onFileSelected(event: any) {
        if (event.target.files.length) {
            this.handleFile(event.target.files[0]);
        }
    }

    handleFile(file: File) {
        if (file.type.startsWith('image/')) {
            this.uploadedImage = file;
            const reader = new FileReader();
            reader.onload = (e: any) => {
                this.uploadedImageUrl = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    }

    generate() {
        // Validate campaign name first
        if (!this.projectTitle || this.projectTitle.trim().length === 0) {
            this.confirmationService.confirm({
                title: 'Campaign Name Required',
                message: 'Please enter a campaign name before generating!',
                confirmText: 'OK',
                onConfirm: () => { }
            });
            return;
        }

        // --- SECURITY CHECK (Anti-Tamper) ---
        if (!this.authService.currentUser()) {
            this.handleGuestInteraction();
            return;
        }

        if (!this.prompt) {
            this.confirmationService.confirm({
                title: 'Prompt Required',
                message: 'Please enter a prompt to describe your video!',
                confirmText: 'OK',
                onConfirm: () => { }
            });
            return;
        }

        // --- PRE-FLIGHT CREDIT CHECK ---
        if (this.userCredits < this.COST_PER_GEN) {
            this.confirmationService.confirm({
                title: 'Insufficient Credits',
                message: `You need at least ${this.COST_PER_GEN} credits to generate a video.\nCurrent balance: ${this.userCredits} credits`,
                confirmText: 'Buy Credits',
                cancelText: 'Cancel',
                onConfirm: () => {
                    this.router.navigate(['/pricing']);
                },
                onCancel: () => { }
            });
            return;
        }

        // --- CONFIRMATION ---
        const cost = this.getCreditCost(this.numScenes);
        this.confirmationService.confirm({
            title: 'Confirm Generation',
            message: `This will use approximately ${cost} credits.\nDo you want to proceed?`,
            confirmText: 'Generate',
            cancelText: 'Cancel',
            onConfirm: () => {
                this.executeGeneration();
            }
        });
    }

    private executeGeneration() {
        console.log('================================================================================');
        console.log('🚀 [FE DEBUG] GENERATION EXECUTION STARTING');
        console.log('================================================================================');
        console.log('[FE DEBUG] User:', this.authService.currentUser()?.uid);
        console.log('[FE DEBUG] Project Title:', this.projectTitle);
        console.log('[FE DEBUG] Prompt:', this.prompt);
        console.log('[FE DEBUG] Credits:', this.userCredits);
        console.log('[FE DEBUG] Has uploaded image:', !!this.uploadedImage);
        console.log('================================================================================');

        this.isStarting = true; // Blocking start
        this.isBackgroundProcessing = false;
        this.isFailed = false;
        this.generationStatus = 'Igniting engines...';
        this.friendlyStatus = 'Warming up...';
        this.logs = [];
        this.sceneAssets = {};

        if (this.uploadedImage) {
            console.log('[FE DEBUG] Uploading image...');
            this.generationStatus = 'Uploading asset...';
            this.apiService.uploadImage(this.uploadedImage).subscribe({
                next: (res) => {
                    console.log('[FE DEBUG] Image uploaded successfully:', res);
                    const runId = res.run_id;
                    const serverPath = res.path;
                    this.startLogStream(runId);
                    this.triggerBackend(runId, serverPath);
                },
                error: (err) => {
                    console.error("[FE DEBUG] Upload failed", err);
                    this.isStarting = false; // Unblock
                    this.generationStatus = 'Upload failed.';
                }
            });
        } else {
            console.log('[FE DEBUG] No image to upload, triggering backend directly');
            this.triggerBackend(undefined, undefined);
        }
    }

    triggerBackend(existingRunId?: string, imagePath?: string) {
        this.generationStatus = 'Starting generation...';
        const config: any = {
            video_model: this.videoModel,
            image_provider: this.imageModel,
            target_duration: this.duration + 's',
            aspect_ratio: this.aspectRatio,
            music_mood: this.musicMood,
            custom_music_prompt: this.customMusicPrompt,
            website_url: this.websiteUrl,
            project_title: this.projectTitle,
            features: this.features
        };
        if (existingRunId) {
            config.run_id = existingRunId;
        }

        this.apiService.triggerGeneration(this.prompt, imagePath, config).subscribe({
            next: (res) => {
                const runId = res.run_id;
                this.currentRunId = runId;

                // UNBLOCK UI -> MOVE TO BACKGROUND
                this.isStarting = false;
                this.isBackgroundProcessing = true;

                if (!existingRunId) {
                    this.startLogStream(runId);
                }
                this.generationStatus = 'Generating... (Run ID: ' + runId + ')';
                this.pollStatus(runId);
                this.loadCredits(); // Refresh credits after deduction
                setTimeout(() => this.loadHistory(), 1000);
            },
            error: (err: any) => {
                console.error(err);
                this.isStarting = false;
                this.isBackgroundProcessing = false;
                if (err.status === 402) {
                    this.generationStatus = 'Insufficient balance.';
                    this.confirmationService.confirm({
                        title: 'Insufficient Balance',
                        message: 'Please recharge your credits to continue.',
                        confirmText: 'Buy Credits',
                        cancelText: 'Cancel',
                        onConfirm: () => {
                            this.router.navigate(['/pricing']);
                        }
                    });
                } else {
                    this.generationStatus = 'Error launching generation.';
                }
            }
        });
    }

    async startLogStream(runId: string) {
        // Get Firebase ID token for WebSocket authentication
        const token = await this.authService.getIdToken();
        if (!token) {
            console.error('Failed to get Firebase token for WebSocket');
            this.generationStatus = 'Authentication error. Please refresh and try again.';
            // Don't kill background processing, just log error
            return;
        }

        const url = this.apiService.getLogStream(runId, token);
        this.socket = new WebSocket(url);

        this.socket.onopen = () => {
            console.log('WebSocket connection established');
        };

        this.socket.onmessage = (event: MessageEvent) => {
            const msg = event.data;

            // Check if message is an error from backend
            if (msg.startsWith('Error:')) {
                console.error('Backend error:', msg);
                this.logs.unshift({ timestamp: new Date(), message: msg });
                // Close the generation UI on authentication errors
                if (msg.includes('Authentication') || msg.includes('Unauthorized') || msg.includes('not found')) {
                    this.isBackgroundProcessing = false; // Stop polling/watching
                    this.generationStatus = msg;
                    if (msg.includes('Unauthorized')) {
                        this.confirmationService.confirm({
                            title: 'Access Denied',
                            message: 'You do not have permission to view this run. This may belong to another user.',
                            confirmText: 'OK',
                            onConfirm: () => { }
                        });
                    }
                }
                return;
            }

            this.logs.unshift({ timestamp: new Date(), message: msg });
            this.updateFriendlyStatus(msg);
        };

        this.socket.onclose = (event: CloseEvent) => {
            console.log(`WebSocket closed: code=${event.code}, reason=${event.reason}`);
            if (event.code === 1008) {
                // 1008 = Policy Violation (used for auth errors)
                this.generationStatus = `Connection closed: ${event.reason || 'Authentication failed'}`;
                this.isBackgroundProcessing = false;
            }
        };

        this.socket.onerror = (error: Event) => {
            console.error('WebSocket error:', error);
            this.generationStatus = 'Connection error. Please check your internet and refresh.';
        };
    }

    updateFriendlyStatus(log: string) {
        if (log.toLowerCase().includes('script')) this.friendlyStatus = 'Writing the script...';
        else if (log.toLowerCase().includes('image')) this.friendlyStatus = 'Dreaming up visuals...';
        else if (log.toLowerCase().includes('video')) this.friendlyStatus = 'Shooting the scenes...';
        else if (log.toLowerCase().includes('audio') || log.toLowerCase().includes('music')) this.friendlyStatus = 'Composing the soundtrack...';
        else if (log.toLowerCase().includes('upload')) this.friendlyStatus = 'Uploading assets...';
        else if (log.toLowerCase().includes('error')) this.friendlyStatus = 'Hit a snag, retrying...';
    }

    toggleLogs() {
        this.showLogs = !this.showLogs;
    }

    pollStatus(runId: string) {
        // Initialize all scenes as loading
        this.sceneList.forEach(scene => {
            this.sceneLoadingStates[scene] = true;
        });

        const startTime = Date.now();
        const MAX_POLLING_DURATION = 10 * 60 * 1000; // 10 minutes

        const interval = setInterval(() => {
            // Check for timeout
            if (Date.now() - startTime > MAX_POLLING_DURATION) {
                clearInterval(interval);
                this.isBackgroundProcessing = false;
                this.isFailed = true;
                this.failureReason = 'Generation timed out. The backend might still be processing, please check your history later.';
                this.generationStatus = 'Process timed out.';
                this.friendlyStatus = 'Taking longer than expected...';
                if (this.socket) this.socket.close();
                this.confirmationService.confirm({
                    title: 'Taking Longer Than Expected',
                    message: 'Generation is taking longer than expected. We stopped watching it, but it might finish in the background.\n\nCheck your "History" tab in a few minutes.',
                    confirmText: 'OK',
                    onConfirm: () => { }
                });
                return;
            }

            this.apiService.checkStatus(runId).subscribe({
                next: (res) => {
                    this.isLoadingRun = false;
                    const status = res.status;

                    // Update scene loading states based on available assets
                    if (res.assets) {
                        Object.keys(res.assets).forEach(assetKey => {
                            // Find scene ID from asset key (e.g., "Hook_video" -> "Hook")
                            const sceneId = assetKey.replace('_video', '').replace('_image', '');
                            if (this.sceneList.includes(sceneId)) {
                                this.sceneLoadingStates[sceneId] = false;
                            }
                        });
                        this.sceneAssets = { ...this.sceneAssets, ...res.assets };
                    }

                    if (status === 'completed') {
                        this.isBackgroundProcessing = false;
                        this.isFailed = false;
                        this.failureReason = null;
                        this.fallbackUsed = res.fallback_used || false;
                        this.generationStatus = 'Generation Complete!';
                        this.friendlyStatus = 'Ready to view!';

                        // Clear all loading states
                        Object.keys(this.sceneLoadingStates).forEach(key => {
                            this.sceneLoadingStates[key] = false;
                        });

                        clearInterval(interval);
                        if (this.socket) this.socket.close();
                        if (res.result) {
                            // Populate Scene Assets & Scripts
                            if (res.result.remote_assets) {
                                this.sceneAssets = res.result.remote_assets;
                            }

                            // Map scripts from scenes_list
                            if (res.result.scenes_list) {
                                res.result.scenes_list.forEach((scene: any) => {
                                    // Prefer narrative, fallback to description or generated_prompt
                                    this.sceneScripts[scene.id] = scene.narrative || scene.description || '';
                                });
                            }
                            if (res.result.video_url) {
                                // Only update finalVideoUrl if it hasn't been manually selected (or if it's the first load)
                                // Actually, if the backend sends a new one (latest), we generally want to show it.
                                // But if user is looking at history, we shouldn't force switch?
                                // For now, simple logic: if we don't have one, take it. 
                                // Or if the one we have is NOT in the history?
                                if (!this.finalVideoUrl) {
                                    this.finalVideoUrl = res.result.video_url;
                                }

                                // Populate History
                                if (res.result.video_history && Array.isArray(res.result.video_history)) {
                                    this.videoVersions = res.result.video_history.map((url: string, index: number) => ({
                                        url: url,
                                        label: `Version ${index + 1}` + (index === res.result.video_history.length - 1 ? ' (Latest)' : '')
                                    }));

                                    // If we have a finalVideoUrl but the versions list updated and we are on "Latest", ensure we point to new latest?
                                    // Actually, let's just let the user switch.
                                }
                            } else if (res.result.result) {
                                const resultStr = res.result.result;
                                const match = resultStr.match(/tmp\/.*\.mp4/);
                                if (match) {
                                    const serverPath = match[0];
                                    this.finalVideoUrl = `${this.apiService.baseUrl}/outputs/${serverPath.replace('tmp/', '')}`;
                                }
                            }
                        }
                    } else if (status === 'failed') {
                        this.isBackgroundProcessing = false;
                        this.isFailed = true;
                        this.failureReason = res.failure_reason || 'Backend processing error.';
                        this.generationStatus = 'Generation Failed. You can still download partial assets.';
                        this.friendlyStatus = 'Something went wrong.';
                        clearInterval(interval);
                        if (this.socket) this.socket.close();
                    }

                },
                error: (err) => {
                    console.error("Polling error", err);
                }
            });
        }, 3000);
    }

    getAssetUrl(path: string): string {
        if (!path) return '';
        if (path.startsWith('http')) return path;
        return `${this.apiService.baseUrl}${path}`;
    }

    getSceneThumbnailUrl(scene: string): string | null {
        // prioritizing specific image key first, then generic key
        if (this.sceneAssets[scene + '_image']) {
            return this.getAssetUrl(this.sceneAssets[scene + '_image']);
        }
        if (this.sceneAssets[scene]) {
            return this.getAssetUrl(this.sceneAssets[scene]);
        }
        return null;
    }

    downloadAssets() {
        if (!this.currentRunId) return;

        // --- SECURITY CHECK ---
        if (!this.authService.currentUser()) {
            this.handleGuestInteraction();
            return;
        }

        this.isDownloading = true;
        this.apiService.downloadRun(this.currentRunId).subscribe({
            next: (blob) => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `ignite_assets_${this.currentRunId}.zip`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                this.isDownloading = false;
            },
            error: (err) => {
                console.error('Download failed', err);
                this.confirmationService.confirm({
                    title: 'Download Failed',
                    message: 'Failed to download assets. Please try again.',
                    confirmText: 'OK',
                    onConfirm: () => { }
                });
                this.isDownloading = false;
            }
        });
    }

    handleVideoError(event: any) {
        event.target.poster = 'assets/placeholder.svg';
    }

    regenerateScene(sceneId: string) {
        if (!this.currentRunId) {
            console.error('No run ID available for regeneration');
            this.confirmationService.confirm({
                title: 'Cannot Regenerate',
                message: 'Missing session context. Please create a new campaign.',
                confirmText: 'OK',
                onConfirm: () => { }
            });
            return;
        }

        // --- SECURITY CHECK ---
        if (!this.authService.currentUser()) {
            this.handleGuestInteraction();
            return;
        }

        // --- OPEN MODAL INSTEAD OF DIRECT CONFIRM ---
        this.sceneToRegenerate = sceneId;
        this.regenerationPrompt = ''; // Reset prompt
        this.showRegenerateModal = true;
    }

    closeRegenerateModal() {
        this.showRegenerateModal = false;
        this.sceneToRegenerate = null;
        this.regenerationPrompt = '';
    }

    confirmRegeneration() {
        if (!this.sceneToRegenerate) return;

        const sceneId = this.sceneToRegenerate;
        const prompt = this.regenerationPrompt;

        this.closeRegenerateModal();
        this.executeSceneRegeneration(sceneId, prompt);
    }

    private executeSceneRegeneration(sceneId: string, prompt?: string) {

        // Optimistically update UI
        this.generationStatus = `Regenerating ${sceneId}...`;
        this.isBackgroundProcessing = true; // Use non-blocking background logic
        this.isFailed = false;
        this.failureReason = null;

        this.apiService.regenerateScene(this.currentRunId!, sceneId, prompt).subscribe({
            next: (res: any) => {
                // Invalidate history cache since this run is being regenerated
                this.historyService.invalidateCacheForRun(this.currentRunId!);

                this.startLogStream(this.currentRunId!);
                this.pollStatus(this.currentRunId!);
            },
            error: (err: any) => {
                console.error('Regeneration failed', err);

                this.isBackgroundProcessing = false;

                // Display specific error messages
                if (err.status === 429) {
                    // Throttling error
                    const errorMsg = err.error?.detail || 'System is busy. Please wait a moment and try again.';
                    this.generationStatus = errorMsg;
                    this.confirmationService.confirm({
                        title: 'System Busy',
                        message: errorMsg,
                        confirmText: 'OK',
                        onConfirm: () => { }
                    });
                } else if (err.status === 403) {
                    // Authorization error
                    this.confirmationService.confirm({
                        title: 'Permission Denied',
                        message: 'You do not have permission to regenerate this scene.',
                        confirmText: 'OK',
                        onConfirm: () => { }
                    });
                } else if (err.status === 402) {
                    // Insufficient credits
                    this.confirmationService.confirm({
                        title: 'Insufficient Credits',
                        message: err.error?.detail || 'Insufficient credits for regeneration.',
                        confirmText: 'Buy Credits',
                        cancelText: 'Cancel',
                        onConfirm: () => {
                            this.router.navigate(['/pricing']);
                        }
                    });
                } else {
                    // Other errors
                    const errorDetail = err.error?.detail || 'Regeneration failed. Please try again.';
                    this.generationStatus = errorDetail;
                    this.confirmationService.confirm({
                        title: 'Regeneration Failed',
                        message: errorDetail,
                        confirmText: 'OK',
                        onConfirm: () => { }
                    });
                }
            }
        });
    }


    toggleProperties() {
        this.isPropertiesOpen = !this.isPropertiesOpen;
    }

    getModelPrice(model: string): string {
        switch (model) {
            case 'veo-3.1-fast-generate-preview':
                return 'Fast Model (10 Credits)';
            case 'veo-2.0-generate-001':
                return 'Stable Model (10 Credits)';
            default:
                return '10 Credits per generation';
        }
    }

    // Contextual messaging for generate button
    getGenerateButtonText(): string {
        if (this.isGenerating) return 'Creating...';

        const hasCampaign = this.currentRunId && Object.keys(this.sceneAssets).length > 0;
        const hasCredits = this.userCredits >= this.COST_PER_GEN;

        return this.isGenerating ? 'Creating...' : (this.currentRunId ? 'New' : 'Generate');
    }

    handleGuestInteraction() {
        this.showSignInModal = true;
    }

    performLogin() {
        this.authService.loginWithGoogle().then(() => {
            // Successful login will likely trigger a route guard redirect or just update state
            // But purely for safety:
            if (this.currentRunId) {
                // Refresh to ensure everything syncs
                window.location.reload();
            }
        }).catch(err => {
            console.log('Login dismissed', err);
        });
    }



    isSceneLoading(sceneId: string): boolean {
        return this.sceneLoadingStates[sceneId] === true;
    }

    openPreview(videoUrl: string, sceneName: string): void {
        this.selectedVideoUrl = videoUrl;
        this.selectedSceneName = sceneName;
        this.previewModalVisible = true;
    }

    closePreview(): void {
        this.previewModalVisible = false;
        this.selectedVideoUrl = null;
    }

    playVideo(container: HTMLElement): void {
        const video = container.querySelector('video') as HTMLVideoElement;
        if (video) video.play().catch(e => console.log('Video play failed', e));
    }

    pauseVideo(container: HTMLElement): void {
        const video = container.querySelector('video') as HTMLVideoElement;
        if (video) {
            video.pause();
            video.currentTime = 0;
        }
    }
}
