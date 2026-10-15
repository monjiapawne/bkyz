import { Component, computed, input, linkedSignal, output, signal } from '@angular/core';
import { Track } from '../../../interfaces/track';
import { Book } from '../../../interfaces/book';
import { Icon } from '../../shared/icon/icon';

@Component({
  selector: 'app-track-row',
  imports: [Icon],
  templateUrl: './track-row.html'
})
export class TrackRowComponent {

  track = input.required<Track>();
  book = input.required<Book>();
  reordering = input(false);

  edit = output<Track>();
  history = output<Track>();
  move = output<'up' | 'down'>();
  progressChange = output<number>();

  position = linkedSignal(() => this.track().position);
  mosaic = signal<string | null>(null);
  year = computed(() => this.book().publish_date?.match(/\d{4}/)?.[0]);
  lastRead = computed(() => {
    const mins = (Date.now() - Date.parse(this.track().last_read_at!)) / 60000;
    const units = [['year', 525600], ['month', 43200], ['week', 10080], ['day', 1440], ['hour', 60], ['minute', 1]] as const;
    const [unit, size] = units.find(([, size]) => mins >= size) ?? ['minute', 1];
    return new Intl.RelativeTimeFormat('en').format(-Math.floor(mins / size), unit);
  });

  sampleMosaic(img: HTMLImageElement) {
    const [cols, rows, cell] = [6, 4, 4];
    const ctx = document.createElement('canvas').getContext('2d', { willReadFrequently: true });
    if (!ctx) return;
    ctx.canvas.width = cols * cell;
    ctx.canvas.height = rows * cell;
    ctx.drawImage(img, 0, 0, ctx.canvas.width, ctx.canvas.height);
    const src = ctx.getImageData(0, 0, ctx.canvas.width, ctx.canvas.height);
    const out = ctx.createImageData(cols, rows);
    // pick the most saturated pixel per cell so busy covers don't average to grey
    for (let y = 0; y < rows; y++) {
      for (let x = 0; x < cols; x++) {
        let best = 0, bestSat = -1;
        for (let dy = 0; dy < cell; dy++) {
          for (let dx = 0; dx < cell; dx++) {
            const i = ((y * cell + dy) * src.width + x * cell + dx) * 4;
            const [r, g, b] = src.data.subarray(i, i + 3);
            const sat = Math.max(r, g, b) - Math.min(r, g, b);
            if (sat > bestSat) [best, bestSat] = [i, sat];
          }
        }
        out.data.set(src.data.subarray(best, best + 4), (y * cols + x) * 4);
      }
    }
    ctx.canvas.width = cols;
    ctx.canvas.height = rows;
    ctx.putImageData(out, 0, 0);
    this.mosaic.set(`url(${ctx.canvas.toDataURL()})`);
  }

  progress(): number {
    const track = this.track();
    const progress = Math.round(track.position / track.total * 100);
    return Math.min(progress, 100);
  }
}
