import { Component, ElementRef, EventEmitter, Output, ViewChild, signal } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { finalize } from 'rxjs';
import { PlaylistService } from '../../../services/playlist-service';
import { Playlist } from '../../../interfaces/playlist';

@Component({
  selector: 'app-add-playlist',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './add-playlist.html'
})
export class AddPlaylistComponent {

  @Output() playlistAdded = new EventEmitter<number>();
  @Output() playlistDeleted = new EventEmitter<void>();
  @ViewChild('modal') modal!: ElementRef<HTMLDialogElement>;

  isSubmitting = signal(false);
  editing: Playlist | null = null;

  playlistForm: FormGroup;

  constructor(
    private playlistService: PlaylistService,
    private fb: FormBuilder
  ) {
    this.playlistForm = this.fb.group({
      name: ['', Validators.required],
      description: ['']
    });
  }

  open(playlist?: Playlist): void {
    this.editing = playlist ?? null;
    this.playlistForm.reset({
      name: playlist?.name ?? '',
      description: playlist?.description ?? ''
    });
    this.modal.nativeElement.showModal();
  }

  onSubmit(): void {
    if (this.playlistForm.invalid || this.isSubmitting()) {
      return;
    }

    this.isSubmitting.set(true);

    const form = this.playlistForm.getRawValue();

    const request = this.editing
      ? this.playlistService.patchPlaylist(this.editing.id, form.name, form.description)
      : this.playlistService.postPlaylist(form.name, form.description);

    request
      .pipe(
        finalize(() => this.isSubmitting.set(false))
      )
      .subscribe({
        next: responseData => {
          this.modal.nativeElement.close();
          this.playlistAdded.emit(responseData.id);
        },
        error: err => {
          console.error(err);
        }
      });
  }
}
