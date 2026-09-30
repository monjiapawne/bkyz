import { ApplicationConfig, inject, provideBrowserGlobalErrorListeners } from '@angular/core';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideRouter } from '@angular/router';
import { catchError, throwError } from 'rxjs';

import { routes } from './app.routes';
import { NotificationService } from './services/notification-service';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideRouter(routes),
    provideHttpClient(withInterceptors([
      (req, next) => {
        const notifications = inject(NotificationService);
        return next(req).pipe(catchError(err => {
          if (err.status !== 401) notifications.show(err.error?.error ?? err.message, 'error');
          return throwError(() => err);
        }));
      }
    ]))
  ]
};
