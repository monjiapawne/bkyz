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

  progress = computed(() => {
    const t = this.track();
    return Math.min(Math.round(t.position / t.total * 100), 100);
  });
}
