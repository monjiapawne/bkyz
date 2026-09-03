import { Component, computed, input } from '@angular/core';
import { UpperCasePipe } from '@angular/common';
import { Track } from '../../../interfaces/track';
import { Book } from '../../../interfaces/book';

@Component({
  selector: 'app-track-row',
  imports: [UpperCasePipe],
  templateUrl: './track-row.html'
})
export class TrackRowComponent {

  track = input.required<Track>();
  book = input.required<Book>();

  progress(): number {
    const track = this.track();
    const progress = Math.round(track.position / track.total * 100);
    return Math.min(progress, 100);
  } 
}
