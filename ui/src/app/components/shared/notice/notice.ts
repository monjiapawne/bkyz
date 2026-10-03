import { Component } from '@angular/core';
import { NotificationService } from '../../../services/notification-service';
import { Icon } from '../icon/icon';

@Component({
  selector: 'app-notice-banner',
  imports: [Icon],
  templateUrl: './notice.html',
})
export class NoticeBanner {
  constructor(public notifications: NotificationService) { }
}
