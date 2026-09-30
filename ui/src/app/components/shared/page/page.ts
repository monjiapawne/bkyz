import { Component, computed, DestroyRef, effect, inject, input, linkedSignal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ActivatedRoute, CanActivateFn, NavigationEnd, Router } from '@angular/router';
import { filter } from 'rxjs';

export const restoreLast = (sidebarTitle: string): CanActivateFn => (_, state) => {
  const last = localStorage.getItem(`last:${sidebarTitle}`);
  return last && last !== state.url ? inject(Router).parseUrl(last) : true;
};

@Component({
  selector: 'app-page',
  templateUrl: './page.html',
})
export class Page {

  title = input<string>();
  description = input<string>();
  sidebarTitle = input.required<string>();

  desktop = matchMedia('(min-width: 768px)');
  private storageKey = computed(() => `sidebar:${this.sidebarTitle()}`);
  sidebarOpen = linkedSignal(() => this.desktop.matches && localStorage.getItem(this.storageKey()) !== 'closed');

  private route = inject(ActivatedRoute);
  private destroyRef = inject(DestroyRef);

  constructor(router: Router) {
    router.events
      .pipe(filter(e => e instanceof NavigationEnd), takeUntilDestroyed())
      .subscribe(() => {
        if (!this.desktop.matches) this.sidebarOpen.set(false);
      });

    effect(() => {
      if (this.desktop.matches) {
        localStorage.setItem(this.storageKey(), this.sidebarOpen() ? 'open' : 'closed');
      }
    });
  }

  ngOnInit() {
    this.route.url
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(() => {
        const url = '/' + this.route.pathFromRoot.flatMap(r => r.snapshot.url).map(s => s.path).join('/');
        localStorage.setItem(`last:${this.sidebarTitle()}`, url);
      });
  }
}
