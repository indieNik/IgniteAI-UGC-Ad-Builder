import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HistoryService } from '../../services/history.service';
import { AuthService } from '../../services/auth.service';
import { ConfirmationService } from '../../services/confirmation.service';
import { Firestore, collection, addDoc, doc, updateDoc, getDoc } from '@angular/fire/firestore';
import { map } from 'rxjs/operators';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { LucideAngularModule } from 'lucide-angular';
import { IconComponent } from '../../shared/icon.component';

interface Asset {
  type: 'video' | 'image';
  url: string;
  thumbnail?: string;
  sourceRunId: string;
  createdAt: number;
  label: string;
}

interface CampaignGroup {
  run_id: string;
  status: string;
  timestamp: number;
  project_name: string;
  assets: Asset[];
}

@Component({
  selector: 'app-library',
  standalone: true,
  imports: [CommonModule, LucideAngularModule, IconComponent],
  template: `
    <div class="library-page">
      <main class="main-content">
        <div class="library-header">
           <h2 class="text-gradient">Assets Library</h2>
           <p class="subtitle">Your generated videos and images from all campaigns.</p>
        </div>

        <div class="campaigns-container" *ngIf="campaigns$ | async as campaigns">
          <!-- Empty State -->
          <div *ngIf="campaigns.length === 0" class="empty-state">
            <div class="icon">
              <lucide-icon name="image" style="width: 48px; height: 48px; opacity: 0.5;"></lucide-icon>
            </div>
            <h3>No Assets Yet</h3>
            <p>Generate your first campaign to see assets here.</p>
          </div>

          <!-- Campaign Groups -->
          <div class="campaign-group" *ngFor="let campaign of campaigns; trackBy: trackByCampaign">
            <div class="campaign-header" (click)="toggleCampaign(campaign.run_id)">
              <div class="campaign-info">
                <span class="status-indicator" [class.success]="campaign.status === 'completed'" [class.failed]="campaign.status === 'failed'"></span>
                <h3 class="campaign-title">
                  <span class="campaign-name">{{ campaign.project_name }}</span>
                </h3>
              </div>
              <div class="campaign-meta">
                <span class="timestamp">{{ campaign.timestamp * 1000 | date:'MMM d, y' }}</span>
                <span class="asset-count">{{ campaign.assets.length }} {{ campaign.assets.length === 1 ? 'asset' : 'assets' }}</span>
                <lucide-icon 
                  [name]="expandedCampaigns.has(campaign.run_id) ? 'chevron-down' : 'chevron-right'" 
                  class="chevron"
                  style="width: 20px; height: 20px;">
                </lucide-icon>
              </div>
            </div>

            <!-- Assets Container with Segregation -->
            <div class="assets-container" *ngIf="expandedCampaigns.has(campaign.run_id)" [@slideDown]>
              <ng-container *ngIf="segregateAssets(campaign.assets) as segregated">
                
                <!-- Videos Section -->
                <div class="asset-section" *ngIf="segregated.videos.length > 0">
                  <h4 class="section-title">Videos ({{ segregated.videos.length }})</h4>
                  <div class="assets-row">
                    <div class="asset-card" 
                         *ngFor="let asset of segregated.videos; trackBy: trackByAsset"
                         (click)="openPreview(asset); $event.stopPropagation()">
                      <div class="asset-preview">
                        <video [src]="asset.url"
                               (mouseenter)="playVideo($event)"
                               (mouseleave)="pauseVideo($event)"
                               muted
                               preload="metadata"
                               (error)="handleAssetError($event, true)"></video>
                        <div class="asset-badge">Video</div>
                        <div class="action-overlay">
                          <button class="action-btn" (click)="downloadAsset(asset, $event)" title="Download">
                            <lucide-icon name="download" style="width: 20px; height: 20px;"></lucide-icon>
                          </button>
                          <button class="action-btn" (click)="toggleShareMenu(asset, $event)" title="Share">
                            <app-icon name="share" size="20"></app-icon>
                          </button>
                          <button class="action-btn" (click)="shareToCommunity(asset, $event)" title="Share to Community">
                            <app-icon name="globe" size="20"></app-icon>
                          </button>
                        </div>
                        <!-- Share Menu -->
                        <div class="share-menu" *ngIf="activeShareMenu === asset.url" (click)="$event.stopPropagation()">
                          <button (click)="shareAsset(asset, 'whatsapp', $event)">WhatsApp</button>
                          <button (click)="shareAsset(asset, 'facebook', $event)">Facebook</button>
                          <button (click)="shareAsset(asset, 'twitter', $event)">Twitter</button>
                          <button (click)="shareAsset(asset, 'instagram', $event)">Instagram</button>
                        </div>
                      </div>
                      <div class="asset-info">
                        <div class="asset-name">{{ asset.label }}</div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Images Section -->
                <div class="asset-section" *ngIf="segregated.images.length > 0">
                  <h4 class="section-title">Images ({{ segregated.images.length }})</h4>
                  <div class="assets-row">
                    <div class="asset-card" 
                         *ngFor="let asset of segregated.images; trackBy: trackByAsset"
                         (click)="openPreview(asset); $event.stopPropagation()">
                      <div class="asset-preview">
                        <img [src]="asset.url" 
                             loading="lazy" 
                             [alt]="asset.label"
                             (error)="handleAssetError($event, false)">
                        <div class="asset-badge">Image</div>
                        <div class="action-overlay">
                          <button class="action-btn" (click)="downloadAsset(asset, $event)" title="Download">
                            <lucide-icon name="download" style="width: 20px; height: 20px;"></lucide-icon>
                          </button>
                          <button class="action-btn" (click)="toggleShareMenu(asset, $event)" title="Share">
                            <app-icon name="share" size="20"></app-icon>
                          </button>
                          <button class="action-btn" (click)="shareToCommunity(asset, $event)" title="Share to Community">
                            <app-icon name="globe" size="20"></app-icon>
                          </button>
                        </div>
                        <!-- Share Menu -->
                        <div class="share-menu" *ngIf="activeShareMenu === asset.url" (click)="$event.stopPropagation()">
                          <button (click)="shareAsset(asset, 'whatsapp', $event)">WhatsApp</button>
                          <button (click)="shareAsset(asset, 'facebook', $event)">Facebook</button>
                          <button (click)="shareAsset(asset, 'twitter', $event)">Twitter</button>
                          <button (click)="shareAsset(asset, 'instagram', $event)">Instagram</button>
                        </div>
                      </div>
                      <div class="asset-info">
                        <div class="asset-name">{{ asset.label }}</div>
                      </div>
                    </div>
                  </div>
                </div>

              </ng-container>
            </div>
          </div>
        </div>

        <!-- Preview Modal -->
        <div class="modal-overlay" *ngIf="previewAsset" (click)="closePreview()" [@fadeIn]>
          <div class="modal-content" (click)="$event.stopPropagation()">
            <button class="close-btn" (click)="closePreview()" aria-label="Close preview">
              <lucide-icon name="x" style="width: 24px; height: 24px;"></lucide-icon>
            </button>
            
            <button class="nav-btn prev" 
                    (click)="navigatePreview(-1)" 
                    *ngIf="allAssets.length > 1"
                    aria-label="Previous asset">
              <lucide-icon name="arrow-left" style="width: 32px; height: 32px;"></lucide-icon>
            </button>
            
            <button class="nav-btn next" 
                    (click)="navigatePreview(1)" 
                    *ngIf="allAssets.length > 1"
                    aria-label="Next asset">
              <lucide-icon name="chevron-right" style="width: 32px; height: 32px;"></lucide-icon>
            </button>

            <div class="modal-media">
              <video *ngIf="previewAsset.type === 'video'"
                     [src]="previewAsset.url"
                     controls
                     autoplay
                     #previewVideo></video>
              <img *ngIf="previewAsset.type === 'image'" 
                   [src]="previewAsset.url"
                   [alt]="previewAsset.label">
            </div>

            <div class="modal-info">
              <h3>{{ previewAsset.label }}</h3>
              <p class="modal-meta">
                <span>{{ previewAsset.type | titlecase }}</span>
                <span>•</span>
                <span>{{ previewAsset.createdAt * 1000 | date:'medium' }}</span>
              </p>
              <a [href]="previewAsset.url" 
                 target="_blank" 
                 download 
                 class="download-btn"
                 (click)="$event.stopPropagation()">
                <lucide-icon name="download" style="width: 16px; height: 16px;"></lucide-icon>
                Download
              </a>
            </div>
          </div>
        </div>
      </main>

      <style>
        .library-page {
          display: grid;
          height: 100vh;
          background: #0a0a0a;
        }

        .main-content {
          padding: 20px;
          overflow-y: auto;
        }

        .library-header {
          margin-bottom: 30px;
          border-bottom: 1px solid rgba(255,255,255,0.05);
          padding-bottom: 20px;
        }

        .subtitle {
          color: var(--text-secondary);
          font-size: 0.9rem;
          margin-top: 8px;
        }

        .campaigns-container {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .empty-state {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          text-align: center;
          padding: 80px 20px;
          color: var(--text-secondary);
        }

        .empty-state .icon {
          margin-bottom: 20px;
        }

        .empty-state h3 {
          margin-bottom: 8px;
          color: var(--text-primary);
        }

        /* Campaign Group */
        .campaign-group {
          background: rgba(255,255,255,0.02);
          border: 1px solid rgba(255,255,255,0.05);
          border-radius: 12px;
          overflow: hidden;
          transition: all 0.3s ease;
        }

        .campaign-group:hover {
          border-color: rgba(255,255,255,0.1);
          background: rgba(255,255,255,0.03);
        }

        .campaign-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px 20px;
          cursor: pointer;
          user-select: none;
          transition: background 0.2s ease;
        }

        .campaign-header:hover {
          background: rgba(255,255,255,0.02);
        }

        .campaign-info {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .status-indicator {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: rgba(255,255,255,0.3);
          flex-shrink: 0;
        }

        .status-indicator.success {
          background: #10b981;
          box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);
        }

        .status-indicator.failed {
          background: #ef4444;
          box-shadow: 0 0 8px rgba(239, 68, 68, 0.5);
        }

        .campaign-title {
          display: flex;
          align-items: center;
          gap: 12px;
          margin: 0;
          font-size: 1rem;
        }

        .campaign-name {
          font-weight: 500;
          color: var(--text-primary);
        }

        .campaign-meta {
          display: flex;
          align-items: center;
          gap: 16px;
          color: var(--text-secondary);
          font-size: 0.85rem;
        }

        .timestamp {
          font-weight: 500;
        }

        .asset-count {
          padding: 4px 8px;
          background: rgba(255,255,255,0.05);
          border-radius: 4px;
          font-size: 0.75rem;
          font-weight: 600;
        }

        .chevron {
          color: var(--text-secondary);
          transition: transform 0.3s ease;
        }

        /* Assets Row */
        .assets-row {
          padding: 0 20px 20px;
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
          gap: 16px;
          animation: slideDown 0.3s ease;
        }

        @keyframes slideDown {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .asset-card {
          background: rgba(255,255,255,0.02);
          border: 1px solid rgba(255,255,255,0.05);
          border-radius: 8px;
          overflow: hidden;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .asset-card:hover {
          transform: translateY(-4px);
          border-color: var(--accent-primary);
          background: rgba(255,255,255,0.05);
          box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        }

        .asset-preview {
          position: relative;
          aspect-ratio: 1/1;
          background: #000;
          display: flex;
          align-items: center;
          justify-content: center;
          overflow: hidden;
        }

        .asset-preview video,
        .asset-preview img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }

        .asset-badge {
          position: absolute;
          top: 8px;
          right: 8px;
          background: rgba(0,0,0,0.8);
          padding: 4px 8px;
          border-radius: 4px;
          font-size: 0.65rem;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .play-overlay {
          position: absolute;
          inset: 0;
          display: flex;
          align-items: center;
          justify-content: center;
          background: rgba(0,0,0,0.3);
          opacity: 0;
          transition: opacity 0.3s ease;
          pointer-events: none;
        }

        .asset-card:hover .play-overlay {
          opacity: 1;
        }

        .action-overlay {
          position: absolute;
          bottom: 0;
          left: 0;
          right: 0;
          background: linear-gradient(to top, rgba(0,0,0,0.9), transparent);
          padding: 12px;
          display: flex;
          justify-content: center;
          align-items: center;
          gap: 12px;
          opacity: 0;
          transition: opacity 0.2s ease;
          z-index: 10;
        }

        .action-btn {
          background: rgba(255, 255, 255, 0.15);
          border: 1px solid rgba(255, 255, 255, 0.3);
          border-radius: 8px;
          padding: 8px;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s ease;
          backdrop-filter: blur(10px);
        }

        .action-btn:hover {
          background: rgba(255, 255, 255, 0.25);
          transform: scale(1.1);
        }

        .action-btn lucide-icon {
          color: white;
          filter: drop-shadow(0 2px 4px rgba(0,0,0,0.5));
        }

        .asset-card:hover .action-overlay {
          opacity: 1;
        }

        .share-menu {
          position: absolute;
          bottom: 60px;
          left: 50%;
          transform: translateX(-50%);
          background: rgba(20, 20, 20, 0.98);
          border: 1px solid rgba(255, 255, 255, 0.2);
          border-radius: 12px;
          padding: 8px;
          display: flex;
          flex-direction: column;
          gap: 4px;
          z-index: 20;
          backdrop-filter: blur(20px);
          box-shadow: 0 8px 32px rgba(0,0,0,0.5);
          min-width: 140px;
        }

        .share-menu button {
          background: transparent;
          border: none;
          color: white;
          padding: 10px 16px;
          text-align: left;
          cursor: pointer;
          border-radius: 8px;
          font-size: 0.9rem;
          transition: background 0.2s;
        }

        .share-menu button:hover {
          background: rgba(255, 255, 255, 0.1);
        }

        .assets-container {
          padding: 0 16px 16px;
        }

        .asset-section {
          margin-bottom: 32px;
        }

        .asset-section:last-child {
          margin-bottom: 0;
        }

        .section-title {
          font-size: 0.85rem;
          color: rgba(255, 255, 255, 0.5);
          margin: 0 0 16px 0;
          text-transform: uppercase;
          letter-spacing: 1px;
          font-weight: 600;
        }
        }

        .asset-info {
          padding: 12px;
        }

        .asset-name {
          font-weight: 600;
          font-size: 0.85rem;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        /* Modal */
        .modal-overlay {
          position: fixed;
          inset: 0;
          background: rgba(0,0,0,0.95);
          backdrop-filter: blur(10px);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
          animation: fadeIn 0.2s ease;
        }

        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }

        .modal-content {
          position: relative;
          max-width: 90vw;
          max-height: 90vh;
          display: flex;
          flex-direction: column;
          gap: 20px;
        }

        .close-btn {
          position: absolute;
          top: -50px;
          right: 0;
          background: rgba(255,255,255,0.1);
          border: 1px solid rgba(255,255,255,0.2);
          border-radius: 50%;
          width: 40px;
          height: 40px;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: all 0.3s ease;
          color: white;
        }

        .close-btn:hover {
          background: rgba(255,255,255,0.2);
          transform: scale(1.1);
        }

        .nav-btn {
          position: absolute;
          top: 50%;
          transform: translateY(-50%);
          background: rgba(255,255,255,0.1);
          border: 1px solid rgba(255,255,255,0.2);
          border-radius: 50%;
          width: 48px;
          height: 48px;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: all 0.3s ease;
          color: white;
          z-index: 10;
        }

        .nav-btn:hover {
          background: rgba(255,255,255,0.2);
          transform: translateY(-50%) scale(1.1);
        }

        .nav-btn.prev {
          left: -60px;
        }

        .nav-btn.next {
          right: -60px;
        }

        .modal-media {
          max-width: 800px;
          max-height: 70vh;
          display: flex;
          align-items: center;
          justify-content: center;
          background: #000;
          border-radius: 8px;
          overflow: hidden;
        }

        .modal-media video,
        .modal-media img {
          max-width: 100%;
          max-height: 70vh;
          object-fit: contain;
        }

        .modal-info {
          text-align: center;
          color: white;
        }

        .modal-info h3 {
          margin: 0 0 8px 0;
          font-size: 1.2rem;
        }

        .modal-meta {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          color: rgba(255,255,255,0.7);
          font-size: 0.9rem;
          margin-bottom: 16px;
        }

        .download-btn {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          padding: 10px 20px;
          background: var(--accent-primary);
          color: white;
          text-decoration: none;
          border-radius: 6px;
          font-weight: 600;
          font-size: 0.9rem;
          transition: all 0.3s ease;
        }

        .download-btn:hover {
          background: var(--accent-secondary);
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }

        /* Responsive */
        @media (max-width: 768px) {
          .campaign-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 12px;
          }

          .campaign-meta {
            width: 100%;
            justify-content: space-between;
          }

          .assets-row {
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 12px;
          }

          .nav-btn.prev {
            left: 10px;
          }

          .nav-btn.next {
            right: 10px;
          }

          .modal-content {
            max-width: 95vw;
          }
        }
      </style>
    </div>
  `
})
export class LibraryComponent implements OnInit {
  historyService = inject(HistoryService);
  authService = inject(AuthService);
  confirmationService = inject(ConfirmationService);
  firestore = inject(Firestore);

  campaigns$!: Observable<CampaignGroup[]>;
  expandedCampaigns: Set<string> = new Set();
  allAssets: Asset[] = [];
  previewAsset: Asset | null = null;
  currentPreviewIndex = 0;
  activeShareMenu: string | null = null; // Track which asset's share menu is open

  ngOnInit() {
    // Group runs into campaigns and auto-expand first one
    this.campaigns$ = this.historyService.history$.pipe(
      map(runs => {
        const campaigns = this.groupByCampaign(runs);
        // Auto-expand first campaign to show assets above the fold
        if (campaigns.length > 0 && this.expandedCampaigns.size === 0) {
          this.expandedCampaigns.add(campaigns[0].run_id);
        }
        return campaigns;
      })
    );

    // Maintain flat list for modal navigation
    this.historyService.history$.pipe(
      map(runs => this.extractAllAssets(runs))
    ).subscribe(assets => {
      this.allAssets = assets;
    });
  }

  groupByCampaign(runs: any[]): CampaignGroup[] {
    return runs.map(run => ({
      run_id: run.run_id,
      status: run.status || 'unknown',
      timestamp: run.updated_at || run.created_at || run.timestamp || (Date.now() / 1000),
      project_name: run.request?.project_title || run.project_name || 'Untitled Campaign',
      assets: this.extractAssetsFromRun(run)
    })).filter(campaign => campaign.assets.length > 0); // Only show campaigns with assets
  }

  extractAssetsFromRun(run: any): Asset[] {
    const assets: Asset[] = [];
    const result = run.result || {};
    const request_data = run.request || {};
    const outputUrl = run.output_url || result.output_url || result.video_url;
    const sceneResults = run.scene_results || result.scene_results;
    const createdAt = run.created_at || run.timestamp || run.updated_at || (Date.now() / 1000);
    const projectName = request_data.project_title || run.project_name || 'Generated Asset';

    // Add final video
    if (outputUrl) {
      assets.push({
        type: 'video',
        url: outputUrl,
        sourceRunId: run.run_id,
        createdAt: createdAt,
        label: `${projectName} - Final Video`
      });
    }

    // Add scene results
    if (sceneResults) {
      Object.entries(sceneResults).forEach(([sceneId, res]: [string, any]) => {
        if (res.url) {
          assets.push({
            type: res.type || 'video',
            url: res.url,
            sourceRunId: run.run_id,
            createdAt: createdAt,
            label: `${projectName} - ${sceneId}`
          });
        }
      });
    }

    // Add remote assets
    if (result.remote_assets) {
      Object.entries(result.remote_assets).forEach(([key, url]: [string, any]) => {
        // Skip end card and validate URL
        if (!url || typeof url !== 'string' || url.trim() === '' || key.toLowerCase().includes('end_card') || key.toLowerCase().includes('endcard')) {
          return;
        }

        const isImage = key.includes('_image') || key.includes('image');
        // Clean up label: remove 'Generated Asset' prefix and clean key
        let cleanLabel = key.replace(/_/g, ' ').replace(/Generated Asset - /gi, '').trim();
        cleanLabel = cleanLabel.charAt(0).toUpperCase() + cleanLabel.slice(1);

        assets.push({
          type: isImage ? 'image' : 'video',
          url: url,
          sourceRunId: run.run_id,
          createdAt: createdAt,
          label: cleanLabel
        });
      });
    }

    return assets;
  }

  extractAllAssets(runs: any[]): Asset[] {
    const allAssets: Asset[] = [];
    runs.forEach(run => {
      allAssets.push(...this.extractAssetsFromRun(run));
    });
    return allAssets.sort((a, b) => b.createdAt - a.createdAt);
  }

  getCampaignId(runId: string): string {
    // Extract numeric ID from run_1234567890 format
    const parts = runId.split('_');
    return parts[parts.length - 1];
  }

  toggleCampaign(runId: string) {
    // Simple toggle: if clicking the same one, close it. Otherwise, open the new one and close others.
    if (this.expandedCampaigns.has(runId)) {
      this.expandedCampaigns.clear();
    } else {
      this.expandedCampaigns.clear();
      this.expandedCampaigns.add(runId);
    }
  }

  segregateAssets(assets: Asset[]) {
    return {
      videos: assets.filter(a => a.type === 'video'),
      images: assets.filter(a => a.type === 'image')
    };
  }

  async downloadAsset(asset: Asset, event: Event) {
    event.stopPropagation();
    try {
      // Fetch the asset as a blob to trigger download instead of opening in new tab
      const response = await fetch(asset.url);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);

      const link = document.createElement('a');
      link.href = url;
      link.download = asset.label || 'asset';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      // Clean up the blob URL
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download failed:', error);
      // Fallback to opening in new tab if fetch fails (CORS issues)
      window.open(asset.url, '_blank');
    }
  }

  shareAsset(asset: Asset, platform: 'whatsapp' | 'facebook' | 'twitter' | 'instagram', event: Event) {
    event.stopPropagation();
    const text = `Check out this ${asset.type}: ${asset.label}`;
    const url = asset.url;

    let shareUrl = '';
    switch (platform) {
      case 'whatsapp':
        shareUrl = `https://wa.me/?text=${encodeURIComponent(text + ' ' + url)}`;
        break;
      case 'facebook':
        shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`;
        break;
      case 'twitter':
        shareUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`;
        break;
      case 'instagram':
        // Instagram doesn't support direct web sharing, copy to clipboard instead
        navigator.clipboard.writeText(url).then(() => {
          this.confirmationService.confirm({
            title: 'Link Copied',
            message: 'Link copied! Open Instagram and paste the link.',
            confirmText: 'OK',
            onConfirm: () => { }
          });
        });
        return;
    }

    window.open(shareUrl, '_blank', 'width=600,height=400');
  }

  toggleShareMenu(asset: Asset, event: Event) {
    event.stopPropagation();
    // Toggle menu: if clicking same asset, close it. Otherwise open new one.
    this.activeShareMenu = this.activeShareMenu === asset.url ? null : asset.url;
  }

  async shareToCommunity(asset: Asset, event: Event) {
    event.stopPropagation();
    this.activeShareMenu = null; // Close any open share menu

    // Check if user is authenticated using AuthService
    const currentUser = this.authService.currentUser(); // Call signal
    if (!currentUser) {
      this.confirmationService.confirm({
        title: 'Sign In Required',
        message: 'Please sign in to share assets to the community.',
        confirmText: 'OK',
        cancelText: '',
        onConfirm: () => { }
      });
      return;
    }

    // Show custom confirmation dialog
    this.confirmationService.confirm({
      title: 'Share to Community',
      message: `Share "${asset.label}" to the Community?\n\nThis will make it visible to all users.`,
      confirmText: 'Share',
      cancelText: 'Cancel',
      onConfirm: async () => {
        try {
          // Show loading state (optional, but good UX if we could)
          // Since we can't easily update the modal content without closing/opening,
          // we'll proceed and rely on the success modal.

          // IMPORTANT: Backend looks for 'is_public' flag on the execution document
          // It does NOT look at 'community' collection.
          // So we must update the original execution document.

          if (!asset.sourceRunId) {
            throw new Error('Cannot share asset without source run ID');
          }


          console.log('[IgniteAI] Sharing Run ID:', asset.sourceRunId);
          const runDocRef = doc(this.firestore, 'executions', asset.sourceRunId);

          // Verify existence first (optional but helpful for debug)
          const docSnap = await getDoc(runDocRef);
          if (!docSnap.exists()) {
            throw new Error(`Run document ${asset.sourceRunId} not found in Firestore`);
          }

          // Update the document
          await updateDoc(runDocRef, {
            is_public: true,
            shared_at: Date.now() / 1000, // Unix timestamp in seconds (matches Python backend)
            shared_by: currentUser.uid,
            shared_by_email: currentUser.email
          });

          console.log('[IgniteAI] Document updated successfully. is_public=true');

          // Verify update
          const verifySnap = await getDoc(runDocRef);
          if (!verifySnap.data()?.['is_public']) {
            console.warn('[IgniteAI] Warning: Read-after-write check failed for is_public');
          } else {
            console.log('[IgniteAI] Verified: Document is now public.');
          }

          // Show success modal
          this.confirmationService.confirm({
            title: 'Success!',
            message: '✅ Asset shared to Community successfully!',
            confirmText: 'OK',
            cancelText: '', // Hide cancel button
            onConfirm: () => { }
          });
        } catch (error) {
          console.error('Error sharing to community:', error);
          this.confirmationService.confirm({
            title: 'Error',
            message: 'Failed to share to community. Please try again.',
            confirmText: 'OK',
            cancelText: '',
            onConfirm: () => { }
          });
        }
      }
    });
  }

  playVideo(event: Event) {
    const video = event.target as HTMLVideoElement;
    video.play().catch(err => {
      console.log('Auto-play prevented:', err);
    });
  }

  pauseVideo(event: Event) {
    const video = event.target as HTMLVideoElement;
    video.pause();
    video.currentTime = 0;
  }

  openPreview(asset: Asset) {
    this.previewAsset = asset;
    this.currentPreviewIndex = this.allAssets.findIndex(a =>
      a.url === asset.url && a.sourceRunId === asset.sourceRunId
    );
  }

  closePreview() {
    this.previewAsset = null;
  }

  navigatePreview(direction: number) {
    this.currentPreviewIndex += direction;

    // Wrap around
    if (this.currentPreviewIndex < 0) {
      this.currentPreviewIndex = this.allAssets.length - 1;
    } else if (this.currentPreviewIndex >= this.allAssets.length) {
      this.currentPreviewIndex = 0;
    }

    this.previewAsset = this.allAssets[this.currentPreviewIndex];
  }

  handleAssetError(event: any, isVideo: boolean = false) {
    console.error(`Failed to load ${isVideo ? 'video' : 'image'}:`, event.target.src);
    const card = event.target.closest('.asset-card');
    if (card) {
      card.style.opacity = '0.5';
      card.style.pointerEvents = 'none';
    }
  }

  // TrackBy functions for performance
  trackByCampaign(index: number, campaign: CampaignGroup): string {
    return campaign.run_id;
  }

  trackByAsset(index: number, asset: Asset): string {
    return asset.url + asset.sourceRunId;
  }
}
