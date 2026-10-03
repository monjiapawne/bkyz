import { Component, signal, WritableSignal } from '@angular/core';
import { Router, RouterLink, RouterLinkActive } from '@angular/router';
import { Auth } from '../../services/auth-service';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-login-page',
  imports: [FormsModule, RouterLink, RouterLinkActive],
  templateUrl: './login-page.html',
})
export class LoginPage {

  constructor(private auth: Auth, private router: Router) { }

  invalidLoginErrorMessage: WritableSignal<String> = signal("");

  username: string = '';
  password: string = '';
  rememberMe: boolean = false;
  attemptLogin() {
    this.auth.login(this.username, this.password, this.rememberMe)
      .subscribe(
        {
          next: responseData => {
            this.auth.user.set(responseData);
            this.auth.isLoggedIn.set(true);
            this.router.navigate(['/dashboard']);
          },
          error: (err) => {
            this.invalidLoginErrorMessage.set(err['error']['error']);
          }
        }
      )
  }

}
