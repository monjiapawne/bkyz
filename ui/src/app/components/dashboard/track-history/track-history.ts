import { Component, ElementRef, inject, input, signal, viewChild } from '@angular/core';
import { formatDate } from '@angular/common';
import { DataTable } from '../../shared/data-table/data-table';
import { TrackService } from '../../../services/track-service';
import { Track } from '../../../interfaces/track';

@Component({
  selector: 'app-track-history',
  imports: [DataTable],
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
  private modal = viewChild.required<ElementRef<HTMLDialogElement>>('modal');

  open(track: Track) {
    this.rows.set([]);
    this.modal().nativeElement.showModal();
    this.trackService.getTrackHistory(this.playlistId(), track.id).subscribe(history => {
      this.rows.set(history.map(h => ({ ...h, created_at: formatDate(h.created_at, 'MMM d, y', 'en') })));
    });
  }

  close() { this.modal().nativeElement.close(); }
}
