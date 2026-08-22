import { Component, signal, WritableSignal } from '@angular/core';
import { Router, RouterLink, RouterLinkActive } from '@angular/router';
import { Auth } from '../../services/auth-service';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-login-page',
  imports: [FormsModule, RouterLink, RouterLinkActive],
  templateUrl: './login-page.html',
  styleUrl: './login-page.css',
})
export class LoginPage {

  constructor(private auth: Auth, private router: Router) { }

  invalidLoginErrorMessage: WritableSignal<String> = signal("");

  username: string = '';
  password: string = '';
  userId: number = -1;

  attemptLogin() {
    this.auth.login(this.username, this.password)
      .subscribe(
        {
          next: responseData => {
            this.userId = responseData.id;
            this.invalidLoginErrorMessage.set("");
            this.auth.isLoggedIn.set(true);

            this.router.navigate(['/']);
          },
          error: (err) => {
            console.log(err);
            this.invalidLoginErrorMessage.set(err['error']['error']);
          }
        }
      )
  }

}
