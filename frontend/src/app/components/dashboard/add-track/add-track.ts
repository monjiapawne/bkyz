import { Component, ElementRef, EventEmitter, Input, Output, signal, ViewChild } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { finalize } from 'rxjs';
import { TrackService } from '../../../services/track-service';

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

  open(): void {
    this.modal.nativeElement.showModal();
  }

  onSubmit(): void {
    if (this.trackForm.invalid || this.isSubmitting()) {
      return;
    }

    this.isSubmitting.set(true);

    const form = this.trackForm.getRawValue();

    const unit = form.unit === 'other' ? form.customUnit.trim() : form.unit;

    this.trackService.postTrackToPlaylist(
      this.playlistId,
      this.bookId,
      form.position!,
      form.total!,
      unit,
      form.medium!
    )
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