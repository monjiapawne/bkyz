import { Injectable, signal } from '@angular/core';

export interface Notice {
  message: string;
  type: 'info' | 'error';
}

@Injectable({
  providedIn: 'root',
})
export class NotificationService {

  notification = signal<Notice | null>(null);

  show(message: string, type: Notice['type'] = 'info') {
    this.notification.set({ message, type });
  }

  dismiss() {
    this.notification.set(null);
  }
}
