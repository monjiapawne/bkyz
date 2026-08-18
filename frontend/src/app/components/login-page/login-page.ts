import { Component, signal, WritableSignal } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { Auth } from '../../services/auth';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-login-page',
  imports: [FormsModule, RouterLink, RouterLinkActive],
  templateUrl: './login-page.html',
  styleUrl: './login-page.css',
})
export class LoginPage {

  constructor(private auth: Auth) { }

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
            console.log(this.userId);
            this.invalidLoginErrorMessage.set("");
          },
          error: (err) => {
            console.log(err);
            this.invalidLoginErrorMessage.set(err['error']['error']);
          }
        }
      )
  }

}
