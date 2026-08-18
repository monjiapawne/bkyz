import { Component } from '@angular/core';
import { Auth } from '../../services/auth';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-register-page',
  imports: [FormsModule],
  templateUrl: './register-page.html',
  styleUrl: './register-page.css',
})
export class RegisterPage {

  constructor(private auth: Auth){}

  username: string = '';
  password: string = '';
  userId: number = -1;

  attemptRegistration() {
    this.auth.register(this.username, this.password)
    .subscribe(
    {
      next: responseData => { 
        this.userId = responseData.id;
        console.log(this.userId);
      },
      error: (err) => {
        console.log(err);
      }
    })
  }
}
