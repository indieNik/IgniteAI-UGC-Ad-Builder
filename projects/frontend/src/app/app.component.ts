import { Component, ElementRef, HostListener, ViewChild, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, RouterLink, RouterLinkActive, Router, NavigationEnd, Event, ActivatedRoute } from '@angular/router';
import { HistoryService } from './services/history.service';
import { LoginComponent } from './components/login/login.component';
import { AdminService } from './services/admin.service';
import { AuthService } from './services/auth.service';
import { NotificationService } from './services/notification.service';
import { LucideAngularModule } from 'lucide-angular';
import { APP_VERSION } from './version';
import { IconComponent } from './shared/icon.component';
import { ConfirmationModalComponent } from './components/confirmation-modal/confirmation-modal.component';
import { CreditBadgeComponent } from './components/credit-badge/credit-badge.component';
import { PaymentService } from './services/payment.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive, LoginComponent, LucideAngularModule, IconComponent, ConfirmationModalComponent, CreditBadgeComponent],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  title = 'IgniteAI';
  appVersion = APP_VERSION;

  isCampaignsOpen = false;
  isSidebarOpen = false;
  showSidebar = true;
  isPublicPage = false;
  isAdmin = false;
  userCredits = 0;

  @ViewChild('campaignsGroup') campaignsGroup!: ElementRef;

  constructor(
    public historyService: HistoryService,
    public router: Router,
    private route: ActivatedRoute,
    private adminService: AdminService,
    public authService: AuthService,
    private notificationService: NotificationService,
    private paymentService: PaymentService
  ) {

    // Check admin status when user changes
    this.authService.user$.subscribe(async (user) => {
      if (user) {
        // Only check admin status and load credits if NOT on a public page
        // This prevents unnecessary API calls on landing page, sign-in, etc.
        if (!this.isPublicPage) {
          this.isAdmin = await this.adminService.checkAdmin();

          // Load user credits
          this.loadCredits();
        }

        // Request notification permissions and save FCM token
        this.setupNotifications(user.uid);
      } else {
        this.isAdmin = false;
        this.userCredits = 0;
      }
    });
    // Close sidebar on route change & check URL
    this.router.events.subscribe((event: Event) => {
      // Only run on navigation end to ensure URL is updated
      if (event instanceof NavigationEnd) {
        this.isSidebarOpen = false;

        // Hide sidebar on landing page ('/') and sign-in. Ignore hash/params.
        const currentUrl = event.urlAfterRedirects || event.url;
        const basePath = currentUrl.split(/[?#]/)[0];

        // When strictly just '/', split might give empty or just '/'. 
        // Handle empty path case which essentially is home/landing.
        const isHome = basePath === '/' || basePath === '';
        const isSignIn = basePath === '/sign-in';
        const isOnboarding = basePath === '/onboarding';
        const isLegal = ['/terms', '/privacy', '/shipping', '/contact', '/cancellation-refund'].includes(basePath);
        const isGoogleCloud = basePath === '/google-cloud';

        this.isPublicPage = isHome || isSignIn || isOnboarding || isLegal || isGoogleCloud;
        this.showSidebar = !this.isPublicPage;

        // Control Body Scroll:
        // Landing Page, Sign In, Legal -> Scrollable (for swipe to refresh)
        // App Pages -> Hidden (for fixed app-like feel)
        // Landing Page, Sign In, Legal -> Scrollable (for swipe to refresh)
        // App Pages -> Hidden (for fixed app-like feel)
        if (this.isPublicPage) {
          document.body.style.overflow = 'auto';
          document.body.style.overscrollBehaviorY = 'auto';
        } else {
          document.body.style.overflow = 'hidden';
          document.body.style.overscrollBehaviorY = 'none';
        }
      }
    });
  }

  ngOnInit() {
    // Handle auto-signin from landing page free tier signup
    this.route.queryParams.subscribe(params => {
      const token = params['token'];
      const isNewUser = params['new'] === 'true';

      if (token) {
        console.log('Auto-signin: Custom token detected, signing in...');
        this.authService.loginWithCustomToken(token)
          .then(user => {
            console.log('Auto-signin successful:', user.email);

            // Clean up URL by removing query params
            this.router.navigate([], {
              relativeTo: this.route,
              queryParams: {},
              replaceUrl: true
            });

            // Redirect based on new user flag
            if (isNewUser) {
              console.log('New user detected, redirecting to onboarding');
              this.router.navigate(['/onboarding']);
            } else {
              console.log('Existing user, redirecting to dashboard');
              this.router.navigate(['/dashboard']);
            }
          })
          .catch(error => {
            console.error('Auto-signin failed:', error);
            // Redirect to sign-in on failure
            this.router.navigate(['/sign-in']);
          });
      }
    });
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent) {
    if (this.isCampaignsOpen && this.campaignsGroup && !this.campaignsGroup.nativeElement.contains(event.target)) {
      this.isCampaignsOpen = false;
    }
  }

  toggleCampaigns() {
    this.isCampaignsOpen = !this.isCampaignsOpen;
  }

  toggleSidebar() {
    this.isSidebarOpen = !this.isSidebarOpen;
  }

  closeSidebar() {
    this.isSidebarOpen = false;
  }

  loadCredits() {
    this.paymentService.getCredits().subscribe({
      next: (res: any) => this.userCredits = res.credits,
      error: (err) => console.error('Failed to load credits for navbar', err)
    });
  }


  async setupNotifications(userId: string) {
    try {
      // Check current permission status
      const permissionStatus = this.notificationService.getPermissionStatus();

      // Only request if not already decided
      if (permissionStatus === 'default') {
        const granted = await this.notificationService.requestPermission();

        if (granted) {
          // Get and save FCM token
          await this.notificationService.getAndSaveToken(userId);

          // Listen for foreground messages
          this.notificationService.listenForMessages().subscribe({
            next: (payload) => {
              console.log('Received foreground notification:', payload);
            },
            error: (err) => {
              console.error('Error receiving foreground messages:', err);
            }
          });
        }
      } else if (permissionStatus === 'granted') {
        // Permission already granted, just get and save token
        await this.notificationService.getAndSaveToken(userId);

        // Listen for foreground messages
        this.notificationService.listenForMessages().subscribe({
          next: (payload) => {
            console.log('Received foreground notification:', payload);
          },
          error: (err) => {
            console.error('Error receiving foreground messages:', err);
          }
        });
      }
    } catch (error) {
      console.error('Error setting up notifications:', error);
    }
  }

  selectRun(run: any) {
    this.historyService.selectRun(run);
    this.router.navigate(['/campaigns']); // Ensure we are on editor page
    this.closeSidebar(); // Close sidebar on mobile when selection made
  }

  getCampaignName(run: any): string {
    // Priority: config.project_title > request.project_title > prompt (truncated) > Untitled
    const config = run.result?.config || run.request?.config || {};
    const projectTitle = config.project_title || run.request?.project_title || run.project_name;

    if (projectTitle && projectTitle !== 'New Campaign' && projectTitle !== 'Awesome Campaign') {
      return projectTitle;
    }

    // Fallback to truncated prompt
    const prompt = run.request?.prompt || run.prompt;
    if (prompt) {
      return prompt.length > 30 ? prompt.substring(0, 30) + '...' : prompt;
    }

    return 'Untitled Campaign';
  }

  getShortId(runId: string): string {
    // Extract last 4 digits from run_1234567890
    if (!runId) return '0000';
    const parts = runId.split('_');
    const timestamp = parts[parts.length - 1];
    return timestamp.slice(-4);
  }
}
