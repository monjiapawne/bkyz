import { Component, signal, ViewChild, WritableSignal } from '@angular/core';
import { PlaylistService } from '../../services/playlist-service';
import { Playlist } from '../../interfaces/playlist';
import { ActivatedRoute, Router, RouterLink, RouterLinkActive } from '@angular/router';
import { TrackService } from '../../services/track-service';
import { Track } from '../../interfaces/track';
import { BookService } from '../../services/book-service';
import { Book } from '../../interfaces/book';
import { TitleCasePipe } from '@angular/common';
import { Auth } from '../../services/auth-service';
import { AddPlaylistComponent } from './add-playlist/add-playlist';
import { AddTrackComponent } from './add-track/add-track';
import { SearchBookComponent } from './search-book/search-book';
import { TrackRowComponent } from './track-row/track-row';

@Component({
  selector: 'app-dashboard',
  imports: [
    RouterLink,
    RouterLinkActive,
    TitleCasePipe,
    AddPlaylistComponent,
    AddTrackComponent,
    SearchBookComponent,
    TrackRowComponent
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


  @ViewChild('addTrackModal') addTrackModal!: AddTrackComponent;

  playlistId!: number;
  selectedBookId!: number;

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

  onPlaylistAdded(newPlaylistId: number): void {
    this.playlistService.getPlaylists()
      .subscribe({
        next: responseData => {
          this.playlists.set(responseData);
          this.router.navigate(['/playlists', newPlaylistId]);
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
}
