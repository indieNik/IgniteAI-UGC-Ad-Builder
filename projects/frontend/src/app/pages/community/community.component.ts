import { Component, OnInit, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { Router, ActivatedRoute } from '@angular/router';
import { environment } from '../../../environments/environment';
import { ConfirmationService } from '../../services/confirmation.service';
import { ReelsViewerComponent } from '../../shared/reels-viewer.component';

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
    selector: 'app-community',
    standalone: true,
    imports: [CommonModule, ReelsViewerComponent],
    templateUrl: './community.component.html',
    styleUrls: ['./community.component.css']
})
export class CommunityComponent implements OnInit {
    videos: CommunityVideo[] = [];
    loading = true;
    sortBy = 'recent';
    currentlyPlayingId: string | null = null;
    private confirmationService = inject(ConfirmationService);

    // Reels viewer state
    showReelsViewer = false;
    initialVideoId?: string;

    constructor(
        private http: HttpClient,
        private router: Router,
        private route: ActivatedRoute
    ) { }

    ngOnInit() {
        this.loadVideos();

        // Check for shared video query param
        this.route.queryParams.subscribe(params => {
            const videoId = params['video'];
            if (videoId) {
                this.openSharedVideo(videoId);
            }
        });
    }

    loadVideos() {
        this.loading = true;
        this.http.get<any>(`${environment.apiUrl}/api/community/videos?sort_by=${this.sortBy}&limit=50`)
            .subscribe({
                next: (response) => {
                    this.videos = response.videos;
                    this.loading = false;
                },
                error: (error) => {
                    console.error('Error loading community videos:', error);
                    this.loading = false;
                }
            });
    }

    changeSortBy(sortBy: string) {
        this.sortBy = sortBy;
        this.loadVideos();
    }

    toggleLike(video: CommunityVideo) {
        const endpoint = video.is_liked_by_user ? 'like' : 'like';
        const method = video.is_liked_by_user ? 'delete' : 'post';

        const request = method === 'delete'
            ? this.http.delete(`${environment.apiUrl}/api/community/like/${video.run_id}`)
            : this.http.post(`${environment.apiUrl}/api/community/like/${video.run_id}`, {});

        // Optimistic update
        video.is_liked_by_user = !video.is_liked_by_user;
        video.likes += video.is_liked_by_user ? 1 : -1;

        request.subscribe({
            error: (error) => {
                // Revert on error
                video.is_liked_by_user = !video.is_liked_by_user;
                video.likes += video.is_liked_by_user ? 1 : -1;
                console.error('Error toggling like:', error);
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
            }).catch(err => console.log('Error sharing:', err));
        } else {
            // Fallback: copy to clipboard
            navigator.clipboard.writeText(shareUrl).then(() => {
                this.confirmationService.confirm({
                    title: 'Link Copied',
                    message: 'Share link copied to clipboard!',
                    confirmText: 'OK',
                    onConfirm: () => { }
                });
            });
        }
    }

    playVideo(event: Event, videoId: string) {
        const videoEl = event.target as HTMLVideoElement;
        videoEl.play();

        // Track view
        this.http.post(`${environment.apiUrl}/api/community/view/${videoId}`, {}).subscribe({
            error: (e) => console.error('Error tracking view', e)
        });
    }

    pauseVideo(event: Event) {
        const video = event.target as HTMLVideoElement;
        video.pause();
        video.currentTime = 0;
    }

    formatDate(timestamp: number): string {
        if (!timestamp) return '';

        // Context detection: Seconds vs Milliseconds
        // If timestamp is small (e.g. < 1 trillion), it's likely Seconds (Python time.time())
        // If > 1 trillion, it's Milliseconds (JS Date.now())
        const isSeconds = timestamp < 1000000000000;
        const date = new Date(isSeconds ? timestamp * 1000 : timestamp);

        const now = new Date();
        const diffMs = now.getTime() - date.getTime();

        // Safety for future clocks or mismatches
        if (diffMs < 0) return 'Just now';

        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

        if (diffDays === 0) return 'Today';
        if (diffDays === 1) return 'Yesterday';
        if (diffDays < 7) return `${diffDays} days ago`;
        if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
        return date.toLocaleDateString();
    }


    toggleVideoPlayback(event: Event, video: CommunityVideo) {
        event.stopPropagation();

        const videoEl = (event.target as HTMLElement).closest('.video-card')?.querySelector('video') as HTMLVideoElement;
        if (!videoEl) return;

        // Pause all other videos first
        if (this.currentlyPlayingId && this.currentlyPlayingId !== video.run_id) {
            const allVideos = document.querySelectorAll('.video-card video') as NodeListOf<HTMLVideoElement>;
            allVideos.forEach(v => {
                if (v !== videoEl) {
                    v.pause();
                    v.currentTime = 0;
                }
            });
        }

        // Toggle current video
        if (videoEl.paused) {
            videoEl.play();
            videoEl.muted = false; // Unmute when playing via button
            this.currentlyPlayingId = video.run_id;

            // Track view on play
            this.http.post(`${environment.apiUrl}/api/community/view/${video.run_id}`, {}).subscribe({
                error: (e) => console.error('Error tracking view', e)
            });
        } else {
            videoEl.pause();
            this.currentlyPlayingId = null;
        }
    }

    isVideoPlaying(videoId: string): boolean {
        return this.currentlyPlayingId === videoId;
    }

    openSharedVideo(runId: string) {
        // Fetch the specific video from community
        this.http.get<any>(`${environment.apiUrl}/api/community/videos?sort_by=recent&limit=100`)
            .subscribe({
                next: (response) => {
                    const video = response.videos.find((v: CommunityVideo) => v.run_id === runId);
                    if (video) {
                        this.initialVideoId = video.run_id;
                        this.showReelsViewer = true;

                        // Track view on modal open
                        this.http.post(`${environment.apiUrl}/api/community/view/${runId}`, {}).subscribe({
                            error: (e) => console.error('Error tracking view', e)
                        });
                    } else {
                        console.error('Shared video not found in community');
                        this.confirmationService.confirm({
                            title: 'Video Not Found',
                            message: 'This video may have been removed or is no longer available.',
                            confirmText: 'OK',
                            onConfirm: () => {
                                // Clean up query param
                                this.router.navigate([], {
                                    queryParams: {},
                                    replaceUrl: true
                                });
                            }
                        });
                    }
                },
                error: (err) => {
                    console.error('Error fetching shared video:', err);
                    this.confirmationService.confirm({
                        title: 'Error',
                        message: 'Failed to load the shared video. Please try again.',
                        confirmText: 'OK',
                        onConfirm: () => { }
                    });
                }
            });
    }

    openVideoModal(video: CommunityVideo) {
        // Open Reels viewer with video data
        this.initialVideoId = video.run_id;
        this.showReelsViewer = true;

        // Update URL with query param for sharing
        this.router.navigate([], {
            queryParams: { video: video.run_id },
            replaceUrl: true
        });

        // Track view on open
        this.http.post(`${environment.apiUrl}/api/community/view/${video.run_id}`, {}).subscribe({
            error: (e) => console.error('Error tracking view', e)
        });
    }

    closeReelsViewer() {
        this.showReelsViewer = false;
        this.initialVideoId = undefined;

        // Remove query param without full navigation
        this.router.navigate([], {
            queryParams: {},
            replaceUrl: true
        });
    }
}
