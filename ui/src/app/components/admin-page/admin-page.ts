import { Component, computed, signal } from '@angular/core';
import { ActivatedRoute, RouterLink, RouterLinkActive } from '@angular/router';
import { Page } from '../shared/page/page';
import { Auth } from '../../services/auth-service';
import { User } from '../../interfaces/user';

@Component({
  selector: 'app-admin-page',
  imports: [Page, RouterLink, RouterLinkActive],
  templateUrl: './admin-page.html',
})
export class AdminPage {

  sections = [{ path: 'users', label: 'Users' }];
  section = signal<string | null>(null);
  title = computed(() => this.sections.find(s => s.path === this.section())?.label ?? 'Admin');

  users = signal<User[] | null>(null);

  constructor(private auth: Auth, route: ActivatedRoute) {
    route.paramMap.subscribe(params => {
      this.section.set(params.get('section'));
      this.users.set(null);
      if (this.section() === 'users') {
        this.auth.getUsers().subscribe(users => this.users.set(users));
      }
    });
  }
}
