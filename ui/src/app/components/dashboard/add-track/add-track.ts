import { Component, EventEmitter, Input, Output, ViewChild } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Field } from '../../shared/field/field';
import { FormDialog } from '../../shared/form-dialog/form-dialog';
import { TrackService } from '../../../services/track-service';
import { Track } from '../../../interfaces/track';
import { Playlist } from '../../../interfaces/playlist';
import { formatDate } from '@angular/common';

@Component({
  selector: 'app-add-track',
  standalone: true,
  imports: [ReactiveFormsModule, Field, FormDialog],
  templateUrl: './add-track.html'
})
export class AddTrackComponent {

  @Input() playlistId!: number;
  @Input() bookId!: number;
  @Input() playlists: Playlist[] = [];
  @Output() trackAdded = new EventEmitter<void>();
  @Output() trackDeleted = new EventEmitter<Track>();
  @ViewChild('dialog') dialog!: FormDialog;

  editing: Track | null = null;

  units = [
    { value: 'pages', label: 'Pages' },
    { value: 'chapters', label: 'Chapters' },
    { value: '%', label: 'Percent' },
    { value: 'other', label: 'Other' },
  ];
  mediums = [
    { value: 'physical', label: 'Physical' },
    { value: 'ebook', label: 'E-book' },
    { value: 'audiobook', label: 'Audiobook' },
  ];

  get playlistOptions() {
    return this.playlists.map(p => ({ value: p.id, label: p.name }));
  }

  trackForm: FormGroup;

  constructor(
    private fb: FormBuilder,
    private trackService: TrackService
  ) {
    this.trackForm = this.fb.group({
      playlistId: [null, Validators.required],
      position: [0, [
        Validators.required,
        Validators.min(0),
        Validators.pattern(/^\d+$/)
      ]],
      total: [null, [
        Validators.min(1),
        Validators.pattern(/^\d+$/)
      ]],
      unit: ['pages', Validators.required],
      customUnit: [''],
      medium: ['physical', Validators.required],
      active: [false],
      notes: ['', Validators.maxLength(255)],
      rating: [null, [Validators.min(1), Validators.max(10)]],
      position_updated_at: [null]
    });
  }

  open(track?: Track): void {
    this.editing = track ?? null;
    this.trackForm.reset({
      playlistId: this.playlistId,
      position: 0,
      total: null,
      unit: 'pages',
      medium: 'physical',
      active: false,
      notes: '',
      rating: null,
      position_updated_at: null
    });
    if (track) {
      this.trackForm.patchValue({
        ...track,
        notes: track.notes ?? '',
        position_updated_at: track.position_updated_at && formatDate(track.position_updated_at, 'yyyy-MM-dd', 'en')
      });
    }
    this.dialog.open();
  }

  save = () => {
    const form = this.trackForm.getRawValue();

    const unit = form.unit === 'other' ? form.customUnit.trim() : form.unit;

    return this.editing
      ? this.trackService.patchTrack(this.playlistId, this.editing.id, {
        position: form.position!,
        total: form.total!,
        unit,
        medium: form.medium!,
        active: form.active,
        notes: form.notes.trim() || null,
        rating: form.rating,
        ...(this.trackForm.get('position_updated_at')!.dirty && {
          position_updated_at: form.position_updated_at ? new Date(form.position_updated_at + 'T00:00').toISOString() : null
        }),
        playlist_id: form.playlistId
      })
      : this.trackService.postTrackToPlaylist(
        form.playlistId,
        this.bookId,
        form.position!,
        form.total!,
        unit,
        form.medium!,
        form.active,
        form.notes.trim() || null,
        form.rating
      );
  };
}