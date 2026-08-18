import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { User } from '../interfaces/user';

@Injectable({
  providedIn: 'root',
})
export class Auth {
  private apiURL = environment.apiUrl;

  constructor(private httpClient: HttpClient){}

  register(username: string, password: string){
    const body = {
      "username": username,
      "password": password
    }

    return this.httpClient.post<User>(this.apiURL + '/register', body);
  }

}
