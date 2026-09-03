import { Component, ElementRef, EventEmitter, Output, signal, ViewChild } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { finalize } from 'rxjs';
import { BookService } from '../../../services/book-service';
import { Book } from '../../../interfaces/book';

@Component({
  selector: 'app-add-book',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './add-book.html'
})
export class AddBookComponent {

  @Output() bookAdded = new EventEmitter<Book>();
  @ViewChild('modal') modal!: ElementRef<HTMLDialogElement>;

  isSubmitting = signal(false);

  bookForm: FormGroup;

  constructor(
    private fb: FormBuilder,
    private bookService: BookService
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
        finalize(() => this.isSubmitting.set(false))
      )
      .subscribe({
        next: book => {
          this.bookForm.reset();
          this.modal.nativeElement.close();
          this.bookAdded.emit(book);
        },
        error: err => {
          console.error(err);
        }
      });
  }
}