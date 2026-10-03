import { Component, EventEmitter, Output, ViewChild } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Field } from '../../shared/field/field';
import { FormDialog } from '../../shared/form-dialog/form-dialog';
import { MoveButtons } from '../../shared/move-buttons/move-buttons';
import { PlaylistService } from '../../../services/playlist-service';
import { Playlist } from '../../../interfaces/playlist';

@Component({
  selector: 'app-add-playlist',
  standalone: true,
  imports: [ReactiveFormsModule, Field, FormDialog, MoveButtons],
  templateUrl: './add-playlist.html'
})
export class AddPlaylistComponent {

  @Output() playlistAdded = new EventEmitter<number>();
  @Output() playlistDeleted = new EventEmitter<void>();
  @ViewChild('dialog') dialog!: FormDialog;

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
    this.dialog.open();
  }

  move(direction: 'up' | 'down') {
    this.playlistService.movePlaylist(this.editing!.id, direction).subscribe(() => this.playlistAdded.emit(this.editing!.id));
  }

  save = () => {
    const form = this.playlistForm.getRawValue();
    return this.editing
      ? this.playlistService.patchPlaylist(this.editing.id, form.name, form.description)
      : this.playlistService.postPlaylist(form.name, form.description);
  };
}
