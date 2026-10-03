import { Component } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { Auth } from './services/auth-service';
import { NoticeBanner } from './components/shared/notice/notice';

@Component({
  selector: 'app-root',
  imports: [RouterLink, RouterLinkActive, RouterOutlet, NoticeBanner],
  templateUrl: './app.html'
})
export class App {

  constructor(public auth: Auth) { }
}
