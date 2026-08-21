import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root',
})
export class PlaylistService {
  private readonly API_URL = `${environment.apiUrl}/playlists`

  constructor(private http: HttpClient) { }

  getPlaylists() {
    return this.http.get<>(this.API_URL);
  }
}
