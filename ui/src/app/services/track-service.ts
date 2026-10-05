import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { tap } from 'rxjs';
import { Track } from '../interfaces/track';
import { Label } from '../interfaces/label';
import { NotificationService } from './notification-service';

@Injectable({
  providedIn: 'root',
})
export class TrackService {

  private readonly API_URL = `${environment.apiUrl}/playlists`;

  constructor(private http: HttpClient, private notifications: NotificationService) { }

  postTrackToPlaylist(playlistId: number, bookId: number, currentPosition: number, totalPosition: number, unit: string, medium: string, active: boolean, notes: string | null, rating: number | null) {
    const body = {
      "book_id": bookId,
      "position": currentPosition,
      "total": totalPosition,
      "unit": unit,
      "medium": medium,
      "active": active,
      "notes": notes,
      "rating": rating
    };

    return this.http.post<Track>(`${this.API_URL}/${playlistId}/tracks`, body);
  }

  patchTrack(playlistId: number, trackId: number, body: Partial<Track> & { playlist_id?: number, label_ids?: number[] }) {
    return this.http.patch<Track>(`${this.API_URL}/${playlistId}/tracks/${trackId}`, body);
  }

  getLabels() {
    return this.http.get<Label[]>(`${environment.apiUrl}/labels`);
  }

  postLabel(name: string) {
    return this.http.post<Label>(`${environment.apiUrl}/labels`, { name });
  }

  moveTrack(playlistId: number, trackId: number, direction: 'up' | 'down') {
    return this.http.post(`${this.API_URL}/${playlistId}/tracks/${trackId}/move`, { direction });
  }

  progressTrack(playlistId: number, trackId: number, position: number) {
    return this.http.post<Track>(`${this.API_URL}/${playlistId}/tracks/${trackId}/progress`, { position });
  }

  getTrackHistory(playlistId: number, trackId: number) {
    return this.http.get<any[]>(`${this.API_URL}/${playlistId}/tracks/${trackId}/history`);
  }

  deleteTrackFromPlaylist(playlistId: number, trackId: number) {
    return this.http.delete(`${this.API_URL}/${playlistId}/tracks/${trackId}`)
      .pipe(tap(() => this.notifications.show('Track removed', 'info', 'short')));
  }

}
