import { Component, signal } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { Auth } from './services/auth-service';
import { CommonModule } from '@angular/common';
import { NoticeBanner } from './components/shared/notice/notice';

@Component({
  selector: 'app-root',
  imports: [RouterLink, RouterLinkActive, RouterOutlet, CommonModule, NoticeBanner],
  templateUrl: './app.html'
})
export class App {

  constructor(public auth: Auth) { }

  accountMenuOpen = false;

  protected readonly title = signal('bkyz');
}
