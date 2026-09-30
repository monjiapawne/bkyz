import { Injectable, signal } from '@angular/core';

export interface Notice {
  message: string;
  type: 'info' | 'error';
}

const DURATIONS = { short: 4000, static: 0 };

@Injectable({
  providedIn: 'root',
})
export class NotificationService {

  notification = signal<Notice | null>(null);
  private timer?: ReturnType<typeof setTimeout>;

  show(message: string, type: Notice['type'] = 'info', duration: keyof typeof DURATIONS = 'static') {
    clearTimeout(this.timer);
    this.notification.set({ message, type });
    if (DURATIONS[duration]) {
      this.timer = setTimeout(() => this.dismiss(), DURATIONS[duration]);
    }
  }

  dismiss() {
    clearTimeout(this.timer);
    this.notification.set(null);
  }
}
