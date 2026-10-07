import { Component, ElementRef, inject, input, signal, viewChild } from '@angular/core';
import { formatDate } from '@angular/common';
import Chart from 'chart.js/auto';
import { DataTable } from '../../shared/data-table/data-table';
import { Dialog } from '../../shared/dialog/dialog';
import { TrackService } from '../../../services/track-service';
import { Track } from '../../../interfaces/track';

@Component({
  selector: 'app-track-history',
  imports: [DataTable, Dialog],
  templateUrl: './track-history.html',
})
export class TrackHistory {

  playlistId = input.required<number>();

  rows = signal<any[]>([]);
  columns = [
    { key: 'created_at', label: 'Date' },
    { key: 'from_position', label: 'From' },
    { key: 'to_position', label: 'To' },
    { key: 'delta', label: 'Change' },
  ];

  private trackService = inject(TrackService);
  private dialog = viewChild.required(Dialog);
  private canvas = viewChild.required<ElementRef>('chart');

  showProjection = signal(false);
  finishDate = signal('');
  private history: any[] = [];
  private track!: Track;

  open(track: Track) {
    this.track = track;
    this.rows.set([]);
    this.dialog().open();
    this.trackService.getTrackHistory(this.playlistId(), track.id).subscribe(history => {
      this.history = history;
      this.rows.set(history.map(h => ({ ...h, created_at: formatDate(h.created_at, 'MMM d', 'en') })));
      this.draw();
    });
  }

  toggleProjection() {
    this.showProjection.update(v => !v);
    this.draw();
  }

  private draw() {
    const pct = (p: number) => Math.round(p / this.track.total * 100);
    const day = (s: string | Date) => new Date(new Date(s).setHours(0, 0, 0, 0));
    const byDay = Object.fromEntries(this.history.map(h => [formatDate(h.created_at, 'MMM d', 'en'), pct(h.to_position)]));
    const first = this.history[0], last = this.history.at(-1);
    const span = last ? (day(last.created_at).getTime() - day(first.created_at).getTime()) / 864e5 : 0;
    const rate = span ? (pct(last.to_position) - pct(first.to_position)) / span : 0;
    const project = this.showProjection() && rate > 0;
    const today = new Date();
    const end = new Date(today);
    let finishKey = '';
    this.finishDate.set('');
    if (project) {
      const finish = day(today);
      finish.setDate(finish.getDate() + Math.ceil((100 - pct(last.to_position)) / rate));
      finishKey = formatDate(finish, 'MMM d', 'en');
      this.finishDate.set(formatDate(finish, 'MMM d, y', 'en'));
      if (finish > end) end.setTime(finish.getTime());
    }
    const daily: Record<string, number | null> = {};
    const projection: (number | null)[] = [];
    let pos: number | undefined;
    for (const d = day(first?.created_at); d <= end; d.setDate(d.getDate() + 1)) {
      const key = formatDate(d, 'MMM d', 'en');
      pos = byDay[key] ?? pos;
      daily[key] = d <= today ? pos! : null;
      const t = Math.round((d.getTime() - day(today).getTime()) / 864e5);
      projection.push(project && t >= 0 ? Math.min(100, Math.round(pct(last.to_position) + rate * t)) : null);
    }
    Chart.getChart(this.canvas().nativeElement)?.destroy();
    new Chart(this.canvas().nativeElement, {
      type: 'line',
      data: {
        labels: Object.keys(daily),
        datasets: [
          { data: Object.values(daily), borderColor: 'green', pointRadius: Object.keys(daily).map(k => k in byDay ? 3 : 0) },
          { data: projection, borderColor: 'rgba(0, 128, 0, 0.3)', borderDash: [4, 4], pointRadius: 0 },
        ],
      },
      options: {
        plugins: { legend: { display: false } },
        scales: {
          x: { ticks: { autoSkip: false, callback: (_, i) => { const k = Object.keys(daily)[i]; return k in byDay || k === finishKey ? k : ''; } } },
          y: { min: 0, max: 100, ticks: { callback: v => `${v}%` } },
        },
      },
    });
  }
}
