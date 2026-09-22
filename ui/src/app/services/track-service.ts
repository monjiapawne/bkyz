import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { Track } from '../interfaces/track';

@Injectable({
  providedIn: 'root',
})
export class TrackService {

  private readonly API_URL = `${environment.apiUrl}/playlists`;

  constructor(private http: HttpClient) { }

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

  patchTrack(playlistId: number, trackId: number, body: Partial<Track>) {
    return this.http.patch<Track>(`${this.API_URL}/${playlistId}/tracks/${trackId}`, body, { withCredentials: true });
  }

  progressTrack(playlistId: number, trackId: number, newPosition: number) {
    return this.http.post<Track>(`${this.API_URL}/${playlistId}/tracks/${trackId}/progress`,
      { new_position: newPosition }, { withCredentials: true });
  }

  deleteTrackFromPlaylist(playlistId: number, trackId: number) {
    return this.http.delete(`${this.API_URL}/${playlistId}/tracks/${trackId}`, { withCredentials: true });
  }

}
