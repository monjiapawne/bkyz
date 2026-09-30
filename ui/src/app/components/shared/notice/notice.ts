import { Component } from '@angular/core';
import { NotificationService } from '../../../services/notification-service';

@Component({
  selector: 'app-notice-banner',
  templateUrl: './notice.html',
})
export class NoticeBanner {
  constructor(public notifications: NotificationService) { }
}
