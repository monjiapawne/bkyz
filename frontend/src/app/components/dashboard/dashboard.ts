import { Component, signal, WritableSignal } from '@angular/core';
import { PlaylistService } from '../../services/playlist-service';
import { Playlist } from '../../interfaces/playlist';
import { ActivatedRoute, Router, RouterLink, RouterLinkActive } from '@angular/router';
import { TrackService } from '../../services/track-service';
import { Track } from '../../interfaces/track';
import { BookService } from '../../services/book-service';
import { Book } from '../../interfaces/book';
import { TitleCasePipe, UpperCasePipe } from '@angular/common';
import { Auth } from '../../services/auth-service';
import { AddBookComponent } from './add-book/add-book';

@Component({
  selector: 'app-dashboard',
  imports: [
    RouterLink,
    UpperCasePipe,
    RouterLinkActive,
    TitleCasePipe,
    AddBookComponent
  ],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css',
})
export class Dashboard {

  constructor(
    private playlistService: PlaylistService,
    private trackService: TrackService,
    private bookService: BookService,
    private auth: Auth,
    private route: ActivatedRoute,
    private router: Router
  ) { }

  playlistId!: number;

  playlists: WritableSignal<Playlist[]> = signal([]);
  tracks: WritableSignal<Track[]> = signal([]);
  books: WritableSignal<Book[]> = signal([]);

  username: WritableSignal<string> = signal("");

  ngOnInit() {
    this.getUsername();
    this.loadPlaylists();

    this.route.paramMap.subscribe(params => {
      const id = params.get('id');

      if (id) {
        this.playlistId = Number(id);
        this.loadTracks(this.playlistId);
      }
    });
  }

  loadPlaylists() {
    this.playlistService.getPlaylists()
      .subscribe({
        next: responseData => {
          this.playlists.set(responseData);

          if (responseData.length > 0) {
            this.router.navigate(['/playlists', responseData[0].id]);
          }
        },
        error: err => {
          console.log(err);
        }
      });
  }

  loadTracks(playlistId: number) {
    this.tracks.set([]);
    this.books.set([]);

    this.trackService.getAllTracksFromPlaylist(playlistId)
      .subscribe({
        next: responseData => {
          this.tracks.set(responseData.tracks);

          responseData.tracks.forEach(track => {
            this.loadBook(track.book_id);
          });
        },
        error: err => {
          console.log(err);
        }
      });
  }

  loadBook(bookId: number) {
    this.bookService.getBook(bookId)
      .subscribe({
        next: responseData => {
          this.books.update(books => [...books, responseData]);
        },
        error: err => {
          console.log(err);
        }
      });
  }

  getBookForTrack(track: Track): Book | undefined {
    return this.books().find(book => book.id === track.book_id);
  }

  getProgress(track: Track): number {
    const progress = Math.round(track.position / track.total * 100);
    return Math.min(progress, 100);
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
}
