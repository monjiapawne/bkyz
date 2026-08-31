import { Component, ElementRef, EventEmitter, Input, Output, signal, ViewChild } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { switchMap, finalize } from 'rxjs';
import { BookService } from '../../../services/book-service';
import { TrackService } from '../../../services/track-service';

@Component({
  selector: 'app-add-book',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './add-book.html'
})
export class AddBookComponent {

  @Input() playlistId!: number;
  @Output() bookAdded = new EventEmitter<void>();
  @ViewChild('modal') modal!: ElementRef<HTMLDialogElement>;

  isSubmitting = signal(false);

  bookForm: FormGroup;

  constructor(
    private fb: FormBuilder,
    private bookService: BookService,
    private trackService: TrackService
  ) {
    this.bookForm = this.fb.group({
      title: ['', Validators.required],
      authors: ['', Validators.required],
      isbn: ['', [
        Validators.required,
        Validators.pattern(/^\d+$/)
      ]],
      number_of_pages: [null, [
        Validators.required,
        Validators.min(1),
        Validators.pattern(/^\d+$/)
      ]]
    });
  }

  open(): void {
    this.modal.nativeElement.showModal();
  }

  onSubmit(): void {
    if (this.bookForm.invalid || this.isSubmitting()) {
      return;
    }

    this.isSubmitting.set(true);

    const form = this.bookForm.getRawValue();

    this.bookService.postBooks(
      form.authors!,
      form.isbn!,
      form.number_of_pages!,
      form.title!
    )
      .pipe(
        switchMap(book =>
          this.trackService.postTrackToPlaylist(
            this.playlistId,
            book.id,
            0,
            form.number_of_pages!,
            'pages',
            'physical'
          )
        ),
        finalize(() => this.isSubmitting.set(false))
      )
      .subscribe({
        next: () => {
          this.bookForm.reset();
          this.bookAdded.emit();
        },
        error: err => {
          console.error(err);
        }
      });
  }
}
