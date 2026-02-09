import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { PaymentService } from '../../services/payment.service';
import { ApiService } from '../../services/api.service';
import { LucideAngularModule } from 'lucide-angular';
import { ConfirmationService } from '../../services/confirmation.service';

@Component({
  selector: 'app-account-settings',
  standalone: true,
  imports: [CommonModule, LucideAngularModule, FormsModule, RouterModule],
  templateUrl: './account-settings.component.html',
  styleUrls: ['./account-settings.component.css']
})
export class AccountSettingsComponent implements OnInit {
  userCredits: number = 0;
  activeTab: 'credits' | 'brand' = 'credits';
  private confirmationService = inject(ConfirmationService);

  // Brand Kit State
  brand = {
    name: '',
    logo_url: '',
    colors: ['#6366f1'],
    character_prompt: '',
    music_style: 'Energetic',
    font_family: 'Inter, sans-serif'
  };
  isSavingBrand = false;
  brandColorsInput: string = '#6366f1';

  constructor(
    private paymentService: PaymentService,
    private apiService: ApiService
  ) { }

  ngOnInit() {
    this.loadCredits();
    this.loadBrand();
  }

  loadCredits() {
    this.paymentService.getCredits().subscribe({
      next: (res) => this.userCredits = res.credits,
      error: (err) => console.error('Failed to load credits', err)
    });
  }

  loadBrand() {
    this.apiService.getBrand().subscribe({
      next: (res) => {
        if (res.brand) {
          this.brand = { ...this.brand, ...res.brand };
          if (this.brand.colors && this.brand.colors.length > 0) {
            this.brandColorsInput = this.brand.colors.join(', ');
          }
        }
      },
      error: (err) => console.error('Failed to load brand', err)
    });
  }

  saveBrand() {
    this.isSavingBrand = true;
    // Parse colors
    this.brand.colors = this.brandColorsInput.split(',').map(c => c.trim()).filter(c => c);

    this.apiService.updateBrand(this.brand).subscribe({
      next: () => {
        this.isSavingBrand = false;
        this.confirmationService.confirm({
          title: 'Success',
          message: 'Brand Kit updated successfully!',
          confirmText: 'OK',
          onConfirm: () => { }
        });
      },
      error: (err) => {
        this.isSavingBrand = false;
        console.error('Failed to save brand', err);
        this.confirmationService.confirm({
          title: 'Error',
          message: 'Failed to save Brand Kit. Please try again.',
          confirmText: 'OK',
          onConfirm: () => { }
        });
      }
    });
  }

  uploadLogo(event: any) {
    const file = event.target.files[0];
    if (file) {
      this.apiService.uploadImage(file).subscribe({
        next: (res: any) => {
          this.brand.logo_url = res.remote_url || (this.apiService.baseUrl + '/outputs/' + res.filename);
        },
        error: (err) => console.error('Logo upload failed', err)
      });
    }
  }

  buyPlan(tier: string) {
    // Map tier names to what backend expects
    const tierMap: { [key: string]: string } = {
      'starter': 'starter',
      'growth': 'builder' // Map old "growth" tier to new "builder" tier
    };

    const backendTier = tierMap[tier] || tier;

    this.paymentService.createOrder(backendTier).subscribe({
      next: (order) => {
        this.paymentService.initiatePayment(order, { name: 'Valued Member', email: '', contact: '' }).then(() => {
          this.loadCredits();
        }).catch(err => console.error('Payment failed', err));
      },
      error: (err) => console.error('Order creation failed', err)
    });
  }
}
