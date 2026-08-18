import { Component, signal, WritableSignal } from '@angular/core';
import { Auth } from '../../services/auth';
import { FormsModule } from '@angular/forms';
import { RouterLink, RouterLinkActive } from '@angular/router';

@Component({
  selector: 'app-register-page',
  imports: [FormsModule, RouterLink, RouterLinkActive],
  templateUrl: './register-page.html',
  styleUrl: './register-page.css',
})
export class RegisterPage {

  constructor(private auth: Auth) { }

  invalidLoginErrorMessage: WritableSignal<String> = signal("");

  username: string = '';
  password: string = '';
  confirmPassword: string = '';
  userId: number = -1;

  attemptRegistration() {
    if (this.verifyPasswordMatch()) {
      this.auth.register(this.username, this.password)
        .subscribe(
          {
            next: responseData => {
              this.userId = responseData.id;
              console.log(this.userId);
              this.invalidLoginErrorMessage.set("");
            },
            error: (err) => {
              console.log(err);
              this.invalidLoginErrorMessage.set("Invalid username or password")
            }
          })
    }
  }

  verifyPasswordMatch() {
    if (this.password != this.confirmPassword) {
      this.invalidLoginErrorMessage.set("Passwords do not match")
      return false;
    }
    else {
      return true;
    }
  }
}
