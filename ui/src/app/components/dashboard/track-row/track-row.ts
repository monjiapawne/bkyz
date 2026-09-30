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
    const mins = (Date.now() - Date.parse(this.track().updated_at)) / 60000;
    const units = [['year', 525600], ['month', 43200], ['week', 10080], ['day', 1440], ['hour', 60], ['minute', 1]] as const;
    const [unit, size] = units.find(([, size]) => mins >= size) ?? ['minute', 1];
    return new Intl.RelativeTimeFormat('en').format(-Math.floor(mins / size), unit);
  });

  progress(): number {
    const track = this.track();
    const progress = Math.round(track.position / track.total * 100);
    return Math.min(progress, 100);
  }
}
