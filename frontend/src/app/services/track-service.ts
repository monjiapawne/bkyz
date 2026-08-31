import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { Track } from '../interfaces/track';
import { TracksResponse } from '../interfaces/tracks-response';

@Injectable({
  providedIn: 'root',
})
export class TrackService {

  private readonly API_URL = `${environment.apiUrl}/playlists`;

  constructor(private http: HttpClient) { }

  getAllTracksFromPlaylist(playlistId: number) {
    return this.http.get<TracksResponse>(`${this.API_URL}/${playlistId}/tracks`, { withCredentials: true });
  }

  getTrackFromPlaylist(playlistId: number, trackId: number) {
    return this.http.get<Track>(`${this.API_URL}/${playlistId}/tracks/${trackId}`, { withCredentials: true });
  }

  postTrackToPlaylist(playlistId: number, bookId: number, currentPosition: number, totalPosition: number, unit: string, medium: string) {
    const body = {
      "book_id": bookId,
      "position": currentPosition,
      "total": totalPosition,
      "unit": unit,
      "medium": medium
    };

    return this.http.post<Track>(`${this.API_URL}/${playlistId}/tracks`, body, { withCredentials: true });
  }

  deleteTrackFromPlaylist(playlistId: number, trackId: number) {
    return this.http.delete(`${this.API_URL}/${playlistId}/tracks/${trackId}`, { withCredentials: true });
  }

}
