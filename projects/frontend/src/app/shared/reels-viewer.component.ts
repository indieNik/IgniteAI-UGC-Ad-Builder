import { Component, Input, Output, EventEmitter, ViewChildren, QueryList, ElementRef, AfterViewInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

interface CommunityVideo {
    run_id: string;
    user_id: string;
    user_name: string;
    project_name: string;
    video_url: string;
    thumbnail_url: string;
    likes: number;
    views: number;
    shared_at: number;
    is_liked_by_user: boolean;
}

@Component({
    selector: 'app-reels-viewer',
    standalone: true,
    imports: [CommonModule],
    template: `
        <div class="reels-container">
            <!-- Close button -->
            <button class="back-btn" (click)="close()">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M19 12H5M12 19l-7-7 7-7"/>
                </svg>
            </button>

            <!-- Scrollable videos -->
            <div class="reels-scroll" #scrollContainer (scroll)="onScroll()">
                <div *ngFor="let video of videos; let i = index" class="reel-item" [attr.data-index]="i">
                    <video 
                        #videoElement
                        [src]="video.video_url" 
                        [poster]="video.thumbnail_url"
                        loop 
                        playsinline
                        preload="metadata"
                        class="reel-video"
                    ></video>

                    <!-- Right-side controls -->
                    <div class="reel-controls">
                        <button class="control-btn like-btn" 
                                [class.liked]="video.is_liked_by_user"
                                (click)="toggleLike(video); $event.stopPropagation()">
                            <svg width="32" height="32" viewBox="0 0 24 24" 
                                 [attr.fill]="video.is_liked_by_user ? 'currentColor' : 'none'" 
                                 stroke="currentColor" stroke-width="2">
                                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
                            </svg>
                            <span class="control-label">{{ formatNumber(video.likes) }}</span>
                        </button>

                        <button class="control-btn share-btn" (click)="shareVideo(video); $event.stopPropagation()">
                            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <circle cx="18" cy="5" r="3"></circle>
                                <circle cx="6" cy="12" r="3"></circle>
                                <circle cx="18" cy="19" r="3"></circle>
                                <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line>
                                <line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line>
                            </svg>
                            <span class="control-label">Share</span>
                        </button>

                        <button class="control-btn views-btn">
                            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                                <circle cx="12" cy="12" r="3"></circle>
                            </svg>
                            <span class="control-label">{{ formatNumber(video.views) }}</span>
                        </button>
                    </div>

                    <!-- Bottom info -->
                    <div class="reel-info">
                        <h3 class="reel-title">{{ video.project_name }}</h3>
                        <p class="reel-creator">by {{ video.user_name === 'Anonymous' ? 'Community Member' : video.user_name }}</p>
                    </div>
                </div>
            </div>
        </div>
    `,
    styles: [`
        .reels-container {
            position: fixed;
            inset: 0;
            background: #000;
            z-index: 10000;
            overflow: hidden;
        }

        .back-btn {
            position: fixed;
            top: 20px;
            left: 20px;
            width: 44px;
            height: 44px;
            border-radius: 50%;
            background: rgba(0, 0, 0, 0.6);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10001;
            transition: all 0.2s;
        }

        .back-btn:hover {
            background: rgba(0, 0, 0, 0.8);
            transform: scale(1.05);
        }

        .reels-scroll {
            height: 100vh;
            overflow-y: scroll;
            scroll-snap-type: y mandatory;
            -webkit-overflow-scrolling: touch;
            scrollbar-width: none;
        }

        .reels-scroll::-webkit-scrollbar {
            display: none;
        }

        .reel-item {
            height: 100vh;
            width: 100vw;
            scroll-snap-align: start;
            scroll-snap-stop: always;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #000;
        }

        .reel-video {
            width: 100%;
            height: 100%;
            object-fit: contain;
        }

        /* Right-side controls */
        .reel-controls {
            position: absolute;
            right: 12px;
            bottom: 180px;
            display: flex;
            flex-direction: column;
            gap: 20px;
            z-index: 10;
            background: rgba(0, 0, 0, 0.4);
            backdrop-filter: blur(10px);
            padding: 12px 8px;
            border-radius: 50px;
        }

        .control-btn {
            background: none;
            border: none;
            color: white;
            cursor: pointer;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 4px;
            transition: all 0.2s;
        }

        .control-btn:active {
            transform: scale(0.9);
        }

        .control-label {
            font-size: 12px;
            font-weight: 600;
        }

        .like-btn.liked {
            color: #FF4458;
        }

        .views-btn {
            opacity: 0.8;
            cursor: default;
        }

        /* Bottom info */
        .reel-info {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 80px;
            padding: 20px;
            background: linear-gradient(to top, rgba(0,0,0,0.8) 0%, transparent 100%);
            color: white;
            z-index: 9;
        }

        .reel-title {
            font-size: 16px;
            font-weight: 600;
            margin: 0 0 4px 0;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .reel-creator {
            font-size: 14px;
            opacity: 0.8;
            margin: 0;
        }

        /* Mobile optimization */
        @media (max-width: 768px) {
            .back-btn {
                top: 16px;
                left: 16px;
                width: 40px;
                height: 40px;
            }

            .reel-controls {
                right: 5px;
                bottom: 260px;
                gap: 16px;
                padding: 15px 5px;
            }

            .control-btn svg {
                width: 28px;
                height: 28px;
            }

            .reel-info {
                right: 60px;
                padding: 16px;
            }

            .reel-title {
                font-size: 15px;
            }

            .reel-creator {
                font-size: 13px;
            }
        }
    `]
})
export class ReelsViewerComponent implements AfterViewInit, OnDestroy {
    @Input() videos: CommunityVideo[] = [];
    @Input() initialVideoId?: string;
    @Output() closeViewer = new EventEmitter<void>();

    @ViewChildren('videoElement') videoElements!: QueryList<ElementRef<HTMLVideoElement>>;
    @ViewChildren('scrollContainer') scrollContainer!: QueryList<ElementRef<HTMLDivElement>>;

    private observer?: IntersectionObserver;
    private currentVideoIndex = 0;

    constructor(private http: HttpClient) { }

    ngAfterViewInit() {
        // Scroll to initial video if specified
        if (this.initialVideoId) {
            setTimeout(() => this.scrollToVideo(this.initialVideoId!), 100);
        }

        // Setup Intersection Observer for auto-play
        this.setupAutoPlay();

        // Setup keyboard navigation
        this.setupKeyboardNav();
    }

    ngOnDestroy() {
        if (this.observer) {
            this.observer.disconnect();
        }
        document.removeEventListener('keydown', this.handleKeyPress);
    }

    setupAutoPlay() {
        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                const video = entry.target as HTMLVideoElement;

                if (entry.isIntersecting && entry.intersectionRatio > 0.5) {
                    video.play().catch(() => {
                        // Auto-play failed, user needs to interact
                    });
                } else {
                    video.pause();
                }
            });
        }, { threshold: 0.5 });

        // Observe all videos
        this.videoElements.forEach(videoRef => {
            this.observer!.observe(videoRef.nativeElement);
        });
    }

    setupKeyboardNav() {
        document.addEventListener('keydown', this.handleKeyPress);
    }

    handleKeyPress = (event: KeyboardEvent) => {
        if (event.key === 'ArrowDown') {
            this.scrollToIndex(this.currentVideoIndex + 1);
        } else if (event.key === 'ArrowUp') {
            this.scrollToIndex(this.currentVideoIndex - 1);
        } else if (event.key === 'Escape') {
            this.close();
        }
    }

    onScroll() {
        const container = this.scrollContainer.first?.nativeElement;
        if (!container) return;

        // Determine current video index based on scroll position
        const scrollPosition = container.scrollTop;
        const viewportHeight = window.innerHeight;
        this.currentVideoIndex = Math.round(scrollPosition / viewportHeight);
    }

    scrollToVideo(videoId: string) {
        const index = this.videos.findIndex(v => v.run_id === videoId);
        if (index !== -1) {
            this.scrollToIndex(index);
        }
    }

    scrollToIndex(index: number) {
        if (index < 0 || index >= this.videos.length) return;

        const container = this.scrollContainer.first?.nativeElement;
        if (container) {
            container.scrollTo({
                top: index * window.innerHeight,
                behavior: 'smooth'
            });
        }
    }

    toggleLike(video: CommunityVideo) {
        const method = video.is_liked_by_user ? 'delete' : 'post';
        const request = method === 'delete'
            ? this.http.delete(`${environment.apiUrl}/api/community/like/${video.run_id}`)
            : this.http.post(`${environment.apiUrl}/api/community/like/${video.run_id}`, {});

        // Optimistic update
        video.is_liked_by_user = !video.is_liked_by_user;
        video.likes += video.is_liked_by_user ? 1 : -1;

        request.subscribe({
            error: () => {
                // Revert on error
                video.is_liked_by_user = !video.is_liked_by_user;
                video.likes += video.is_liked_by_user ? 1 : -1;
            }
        });
    }

    shareVideo(video: CommunityVideo) {
        const shareUrl = `${window.location.origin}/community?video=${video.run_id}`;

        if (navigator.share) {
            navigator.share({
                title: video.project_name,
                text: `Check out this video created with IgniteAI!`,
                url: shareUrl
            }).catch(() => { });
        } else {
            // Fallback: copy to clipboard
            navigator.clipboard.writeText(shareUrl);
        }
    }

    formatNumber(num: number): string {
        if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
        if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
        return num.toString();
    }

    close() {
        this.closeViewer.emit();
    }
}
