import { Component, computed, input, linkedSignal, output } from '@angular/core';
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

  edit = output<Track>();
  progressChange = output<number>();

  position = linkedSignal(() => this.track().position);
  year = computed(() => this.book().publish_date?.match(/\d{4}/)?.[0]);
  lastRead = computed(() => {
    const mins = Math.floor((Date.now() - Date.parse(this.track().updated_at)) / 60000);
    const parts = [[Math.floor(mins / 1440), 'day'], [Math.floor(mins / 60) % 24, 'hour'], [mins % 60, 'min']] as const;
    return parts.filter(([n]) => n).map(([n, unit]) => `${n} ${unit}${n > 1 && unit !== 'min' ? 's' : ''}`).join(', ') || 'just now';
  });

  progress(): number {
    const track = this.track();
    const progress = Math.round(track.position / track.total * 100);
    return Math.min(progress, 100);
  }
}
