import { Component, signal, WritableSignal } from '@angular/core';
import { PlaylistService } from '../../services/playlist-service';
import { Playlist } from '../../interfaces/playlist';
import { ActivatedRoute, RouterLink, RouterLinkActive } from '@angular/router';
import { TrackService } from '../../services/track-service';
import { Track } from '../../interfaces/track';
import { BookService } from '../../services/book-service';
import { Book } from '../../interfaces/book';
import { UpperCasePipe } from '@angular/common';

@Component({
  selector: 'app-dashboard',
  imports: [RouterLink, UpperCasePipe, RouterLinkActive],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css',
})
export class Dashboard {

  constructor(
    private playlistService: PlaylistService,
    private trackService: TrackService,
    private bookService: BookService,
    private route: ActivatedRoute
  ) { }

  playlists: WritableSignal<Playlist[]> = signal([]);
  tracks: WritableSignal<Track[]> = signal([]);
  books: WritableSignal<Book[]> = signal([]);

  ngOnInit() {
    this.loadPlaylists();

    this.route.paramMap.subscribe(params => {
      const playlistId = params.get('id');

      if (playlistId) {
        this.loadTracks(Number(playlistId));
      }
    });
  }

  loadPlaylists() {
    this.playlistService.getPlaylists()
      .subscribe({
        next: responseData => {
          this.playlists.set(responseData);
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
          })
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
          console.log(this.books());
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
    let progress = Math.round(track.position / track.total * 100)
    return Math.min(progress, 100)
  }

}
