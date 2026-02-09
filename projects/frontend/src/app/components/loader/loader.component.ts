import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-loader',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './loader.component.html',
  styleUrls: ['./loader.component.css']
})
export class LoaderComponent {
  @Input() isLoading = false;
  @Input() message = ''; // Optional custom message
  @Input() isError = false;
  @Input() retryCount = 0;
  @Input() maxRetries = 3;
  @Output() retry = new EventEmitter<void>();
}
