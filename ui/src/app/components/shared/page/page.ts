import { Component, computed, effect, input, linkedSignal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { NavigationEnd, Router } from '@angular/router';
import { filter } from 'rxjs';

@Component({
  selector: 'app-page',
  templateUrl: './page.html',
})
export class Page {

  title = input<string>();
  description = input<string>();
  sidebarTitle = input<string>();

  desktop = matchMedia('(min-width: 768px)');
  private storageKey = computed(() => `sidebar:${this.sidebarTitle()}`);
  sidebarOpen = linkedSignal(() => this.desktop.matches && localStorage.getItem(this.storageKey()) !== 'closed');

  constructor(router: Router) {
    router.events
      .pipe(filter(e => e instanceof NavigationEnd), takeUntilDestroyed())
      .subscribe(() => {
        if (!this.desktop.matches) this.sidebarOpen.set(false);
      });

    effect(() => {
      if (this.sidebarTitle() && this.desktop.matches) {
        localStorage.setItem(this.storageKey(), this.sidebarOpen() ? 'open' : 'closed');
      }
    });
  }
}
