import { Component, signal, WritableSignal } from '@angular/core';
import { Auth } from '../../services/auth-service';
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

  invalidRegisterErrorMessage: WritableSignal<String> = signal("");
  accountCreatedSuccessMessage: WritableSignal<String> = signal("");


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
              this.invalidRegisterErrorMessage.set("");
              this.accountCreatedSuccessMessage.set("Account Created Sucessfully")
            },
            error: (err) => {
              console.log(err);
              this.invalidRegisterErrorMessage.set(err['error']['error'])
            }
          })
    }
  }

  verifyPasswordMatch() {
    if (this.password != this.confirmPassword) {
      this.invalidRegisterErrorMessage.set("Passwords do not match")
      return false;
    }
    else {
      return true;
    }
  }
}
