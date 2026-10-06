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

  open(track: Track) {
    this.rows.set([]);
    this.dialog().open();
    this.trackService.getTrackHistory(this.playlistId(), track.id).subscribe(history => {
      this.rows.set(history.map(h => ({ ...h, created_at: formatDate(h.created_at, 'MMM d', 'en') })));
      const daily = Object.fromEntries(history.map(h => [formatDate(h.created_at, 'MMM d', 'en'), h.to_position]));
      Chart.getChart(this.canvas().nativeElement)?.destroy();
      new Chart(this.canvas().nativeElement, {
        type: 'line',
        data: {
          labels: Object.keys(daily),
          datasets: [{ data: Object.values(daily), borderColor: 'green' }],
        },
        options: { plugins: { legend: { display: false } } },
      });
    });
  }
}
