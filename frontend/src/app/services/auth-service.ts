import { Injectable, signal } from '@angular/core';
import { environment } from '../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { User } from '../interfaces/user';

@Injectable({
  providedIn: 'root',
})
export class Auth {

  private apiURL = environment.apiUrl;

  constructor(private httpClient: HttpClient) {
    this.checkSession();
  }

  isLoggedIn = signal(false);
  user = signal<User | null>(null);

  register(username: string, password: string) {
    const body = {
      "username": username,
      "password": password
    }

    return this.httpClient.post<User>(this.apiURL + '/user/register', body);
  }

  login(username: string, password: string) {
    const body = {
      "username": username,
      "password": password
    };

    return this.httpClient.post<User>(this.apiURL + '/user/login', body, { withCredentials: true });
  }

  getUser() {
    return this.httpClient.get<User>(this.apiURL + '/user', { withCredentials: true });
  }

  checkSession() {
    this.httpClient.get<User>(this.apiURL + '/user', { withCredentials: true })
      .subscribe({
        next: (user) => {
          this.user.set(user);
          this.isLoggedIn.set(true);
        },
        error: () => {
          this.user.set(null);
          this.isLoggedIn.set(false);
        }
      });
  }

  signOut() {

  }

}
