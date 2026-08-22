import { Component, signal, WritableSignal } from '@angular/core';
import { PlaylistService } from '../../services/playlist-service';
import { Playlist } from '../../interfaces/playlist';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-dashboard',
  imports: [RouterLink],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css',
})
export class Dashboard {

  constructor(private playlistService: PlaylistService) { }

  playlists: WritableSignal<Playlist[]> = signal([]);

  ngOnInit() {
    this.loadPlaylists();
  }

  loadPlaylists() {
    this.playlistService.getPlaylists()
      .subscribe({
        next: responseData => {
          this.playlists.set(responseData);
          console.log(responseData);
        }
      })
  }

}
