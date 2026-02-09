import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { Router, RouterModule } from '@angular/router';
import { LucideAngularModule } from 'lucide-angular';

@Component({
  selector: 'app-projects',
  standalone: true,
  imports: [CommonModule, RouterModule, LucideAngularModule, FormsModule],
  templateUrl: './projects.component.html',
  styleUrls: ['./projects.component.css']
})
export class ProjectsComponent implements OnInit {
  private api = inject(ApiService);
  private router = inject(Router);
  projects$ = this.api.getHistory();


  previewModalVisible = false;
  selectedVideoUrl: string | null = null;
  selectedProjectTitle = '';

  // Campaign name modal
  showNameModal = false;
  newCampaignName = '';

  constructor() { }

  ngOnInit(): void {
  }



  openQuickFolder(): void {
    const latestRun = document.querySelector('.project-card') as HTMLElement;
    if (latestRun) {
      latestRun.click();
    } else {
      this.router.navigate(['/campaigns']);
    }
  }

  openPreferences(): void {
    this.router.navigate(['/credits']);
  }

  openPreview(event: Event, videoUrl: string, title: string): void {
    event.stopPropagation(); // Don't navigate to editor
    this.selectedVideoUrl = videoUrl;
    this.selectedProjectTitle = title;
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

  openNewCampaignModal(): void {
    this.newCampaignName = '';
    this.showNameModal = true;
  }

  closeNameModal(): void {
    this.showNameModal = false;
    this.newCampaignName = '';
  }

  createCampaign(): void {
    const name = this.newCampaignName.trim() || 'New Campaign';
    this.closeNameModal();
    this.router.navigate(['/campaigns'], { queryParams: { name } });
  }
}
