import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Playlist } from '../interfaces/playlist';
import { PlaylistFull } from '../interfaces/playlist-full';

@Injectable({
  providedIn: 'root',
})
export class PlaylistService {
  private readonly API_URL = `${environment.apiUrl}/playlists`

  constructor(private http: HttpClient) { }

  getPlaylistsFull() {
    const params = new HttpParams().set('view', 'full');
    return this.http.get<PlaylistFull[]>(this.API_URL, { params, withCredentials: true });
  }

  postPlaylist(name: string, description?: string) {
    const body = {
      name: name,
      ...(description && {description})
    };

    return this.http.post<Playlist>(this.API_URL, body, { withCredentials: true });
  }

  patchPlaylist(id: number, name: string, description?: string) {
    return this.http.patch<Playlist>(`${this.API_URL}/${id}`, { name, description }, { withCredentials: true });
  }

  deletePlaylist(id: number) {
    return this.http.delete(`${this.API_URL}/${id}`, { withCredentials: true });
  }
}
