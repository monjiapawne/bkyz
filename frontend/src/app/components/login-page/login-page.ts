import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { Auth } from '../../services/auth';

@Component({
  selector: 'app-login-page',
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './login-page.html',
  styleUrl: './login-page.css',
})
export class LoginPage {

  constructor(private auth: Auth) { }

  username: string = '';
  password: string = '';

}
