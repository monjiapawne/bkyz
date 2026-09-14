import { Component, ElementRef, EventEmitter, Input, Output, signal, ViewChild } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { finalize } from 'rxjs';
import { TrackService } from '../../../services/track-service';
import { Track } from '../../../interfaces/track';

@Component({
  selector: 'app-add-track',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './add-track.html'
})
export class AddTrackComponent {

  @Input() playlistId!: number;
  @Input() bookId!: number;
  @Output() trackAdded = new EventEmitter<void>();
  @ViewChild('modal') modal!: ElementRef<HTMLDialogElement>;

  isSubmitting = signal(false);
  editing: Track | null = null;

  trackForm: FormGroup;

  constructor(
    private fb: FormBuilder,
    private trackService: TrackService
  ) {
    this.trackForm = this.fb.group({
      position: [0, [
        Validators.required,
        Validators.min(0),
        Validators.pattern(/^\d+$/)
      ]],
      total: [null, [
        Validators.required,
        Validators.min(1),
        Validators.pattern(/^\d+$/)
      ]],
      unit: ['pages', Validators.required],
      customUnit: [''],
      medium: ['physical', Validators.required]
    });
  }

  open(track?: Track): void {
    this.editing = track ?? null;
    if (track) {
      this.trackForm.patchValue(track);
    }
    this.modal.nativeElement.showModal();
  }

  onSubmit(): void {
    if (this.trackForm.invalid || this.isSubmitting()) {
      return;
    }

    this.isSubmitting.set(true);

    const form = this.trackForm.getRawValue();

    const unit = form.unit === 'other' ? form.customUnit.trim() : form.unit;

    const request = this.editing
      ? this.trackService.patchTrack(this.playlistId, this.editing.id, {
        position: form.position!,
        total: form.total!,
        unit,
        medium: form.medium!
      })
      : this.trackService.postTrackToPlaylist(
        this.playlistId,
        this.bookId,
        form.position!,
        form.total!,
        unit,
        form.medium!
      );

    request
      .pipe(
        finalize(() => this.isSubmitting.set(false))
      )
      .subscribe({
        next: () => {
          this.trackForm.reset({
            position: 0,
            total: null,
            unit: 'pages',
            medium: 'physical'
          });
          this.modal.nativeElement.close();
          this.trackAdded.emit();
        },
        error: err => {
          console.error(err);
        }
      });
  }
}