import { Component, computed, signal, ViewChild, WritableSignal } from '@angular/core';
import { PlaylistService } from '../../services/playlist-service';
import { PlaylistFull } from '../../interfaces/playlist-full';
import { ActivatedRoute, Router, RouterLink, RouterLinkActive } from '@angular/router';
import { TrackService } from '../../services/track-service';
import { Track } from '../../interfaces/track';
import { TrackFull } from '../../interfaces/track-full';
import { Book } from '../../interfaces/book';
import { TitleCasePipe } from '@angular/common';
import { Auth } from '../../services/auth-service';
import { AddPlaylistComponent } from './add-playlist/add-playlist';
import { AddTrackComponent } from './add-track/add-track';
import { SearchBookComponent } from './search-book/search-book';
import { TrackRowComponent } from './track-row/track-row';
import { ConfirmDialog } from '../shared/confirm-dialog/confirm-dialog';

@Component({
  selector: 'app-dashboard',
  imports: [
    RouterLink,
    RouterLinkActive,
    TitleCasePipe,
    AddPlaylistComponent,
    AddTrackComponent,
    SearchBookComponent,
    TrackRowComponent,
    ConfirmDialog
  ],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css',
})
export class Dashboard {

  constructor(
    private playlistService: PlaylistService,
    private trackService: TrackService,
    private auth: Auth,
    private route: ActivatedRoute,
    private router: Router
  ) { }


  @ViewChild('addTrackModal') addTrackModal!: AddTrackComponent;

  playlistId: WritableSignal<number> = signal(0);
  selectedBookId!: number;

  playlists: WritableSignal<PlaylistFull[]> = signal([]);

  playlist = computed(() =>
    this.playlists().find(p => p.id === this.playlistId())
  );

  tracks = computed(() =>
    this.playlists().find(p => p.id === this.playlistId())?.tracks ?? []
  );

  username: WritableSignal<string> = signal("");

  ngOnInit() {
    this.getUsername();
    this.loadDashboard();

    this.route.paramMap.subscribe(params => {
      const id = params.get('id');

      if (id) {
        this.playlistId.set(Number(id));
      }
    });
  }

  loadDashboard() {
    this.playlistService.getPlaylistsFull()
      .subscribe({
        next: responseData => {
          this.playlists.set(responseData);

          if (responseData.length > 0 && !this.playlistId()) {
            this.router.navigate(['/playlists', responseData[0].id]);
          }
        },
        error: err => {
          console.log(err);
        }
      });
  }

  deletePlaylist() {
    const deletedId = this.playlistId();

    this.playlistService.deletePlaylist(deletedId)
      .subscribe({
        next: () => {
          const remaining = this.playlists().filter(p => p.id !== deletedId);
          this.playlists.set(remaining);

          if (remaining.length > 0) {
            this.router.navigate(['/playlists', remaining[0].id]);
          } else {
            this.router.navigate(['/playlists']);
          }
        },
        error: err => {
          console.log(err);
        }
      });
  }

  onPlaylistAdded(newPlaylistId: number): void {
    this.loadDashboard();
    this.router.navigate(['/playlists', newPlaylistId]);
  }

  private updateTracks(update: (tracks: TrackFull[]) => TrackFull[]) {
    this.playlists.update(playlists => playlists.map(playlist =>
      playlist.id === this.playlistId()
        ? { ...playlist, tracks: update(playlist.tracks) }
        : playlist
    ));
  }

  getUsername() {
    this.auth.getUser()
      .subscribe({
        next: responseData => {
          this.username.set(responseData.username);
        },
        error: err => {
          console.log(err);
        }
      });
  }

  onBookSelected(book: Book): void {
    this.selectedBookId = book.id;
    this.addTrackModal.open();
  }

  @ViewChild('confirmTrack') confirmTrack!: ConfirmDialog;
  pendingTrack?: Track;

  onDeleteTrack(track: Track) {
    this.pendingTrack = track;
    this.confirmTrack.open();
  }

  deleteTrack() {
    const track = this.pendingTrack!;
    this.trackService.deleteTrackFromPlaylist(this.playlistId(), track.id).subscribe(() => {
      this.updateTracks(tracks => tracks.filter(t => t.id !== track.id));
    });
  }

  onProgress(track: Track, position: number) {
    this.trackService.progressTrack(this.playlistId(), track.id, position).subscribe(updated => {
      // progress returns a bare track, so merge to keep the embedded book
      this.updateTracks(tracks => tracks.map(t => t.id === updated.id ? { ...t, ...updated } : t));
    });
  }
}
