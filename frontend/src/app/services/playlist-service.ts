import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { Playlist } from '../interfaces/playlist';

@Injectable({
  providedIn: 'root',
})
export class PlaylistService {
  private readonly API_URL = `${environment.apiUrl}/playlists`

  constructor(private http: HttpClient) { }

  getPlaylists() {
    return this.http.get<Playlist[]>(this.API_URL);
  }

  postPlaylist(name: string, description: string) {
    const body = {
      name: name,
      description: description
    };

    return this.http.post<Playlist>(this.API_URL, body);
  }

  deletePlaylist(id: number) {
    return this.http.delete(`${this.API_URL}/${id}`)
  }
}
