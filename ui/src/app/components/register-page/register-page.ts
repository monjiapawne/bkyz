import { Component, signal, WritableSignal } from '@angular/core';
import { Auth } from '../../services/auth-service';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink, RouterLinkActive } from '@angular/router';

@Component({
  selector: 'app-register-page',
  imports: [FormsModule, RouterLink, RouterLinkActive],
  templateUrl: './register-page.html',
})
export class RegisterPage {

  constructor(private auth: Auth, private router: Router) { }

  invalidRegisterErrorMessage: WritableSignal<String> = signal("");

  username: string = '';
  password: string = '';
  confirmPassword: string = '';

  attemptRegistration() {
    if (this.verifyPasswordMatch()) {
      this.auth.register(this.username, this.password)
        .subscribe(
          {
            next: () => this.router.navigate(['/']),
            error: (err) => {
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
