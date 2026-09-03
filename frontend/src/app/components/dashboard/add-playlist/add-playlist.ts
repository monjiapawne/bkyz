import { Component, ElementRef, EventEmitter, Output, ViewChild, signal } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { PlaylistService } from '../../../services/playlist-service';

@Component({
  selector: 'app-add-playlist',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './add-playlist.html'
})
export class AddPlaylistComponent {

  @Output() playlistAdded = new EventEmitter<number>();
  @ViewChild('modal') modal!: ElementRef<HTMLDialogElement>;

  isSubmitting = signal(false);

  playlistForm: FormGroup;

  constructor(
    private playlistService: PlaylistService,
    private fb: FormBuilder
  ) {
    this.playlistForm = this.fb.group({
      name: ['', Validators.required],
      description: ['', Validators.required]
    });
  }

  open(): void {
    this.modal.nativeElement.showModal();
  }

  onSubmit(): void {
    if (this.playlistForm.invalid || this.isSubmitting()) {
      return;
    }

    this.isSubmitting.set(true);

    const form = this.playlistForm.getRawValue();

    this.playlistService.postPlaylist(
      form.name!,
      form.description!
    )
      .subscribe({
        next: responseData => {
          this.playlistForm.reset();
          this.isSubmitting.set(false);
          this.modal.nativeElement.close();
          this.playlistAdded.emit(responseData.id);
        },
        error: err => {
          console.log(err);
          this.isSubmitting.set(false);
        }
      });
  }
}