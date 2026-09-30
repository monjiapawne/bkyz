import { Component, EventEmitter, Output, signal, ViewChild } from '@angular/core';
import { AbstractControl, FormBuilder, FormGroup, ReactiveFormsModule, ValidationErrors, ValidatorFn, Validators } from '@angular/forms';
import { finalize } from 'rxjs';
import { Field } from '../../shared/field/field';
import { FormDialog } from '../../shared/form-dialog/form-dialog';
import { BookService } from '../../../services/book-service';
import { Book } from '../../../interfaces/book';

// Validate minimal requirements to submit a book
const validateBookPost: ValidatorFn = (group: AbstractControl): ValidationErrors | null => {
  const title = group.get('title')?.value?.trim();
  const isbn = group.get('isbn')?.value?.trim();
  return title || isbn ? null : { titleOrIsbn: true };
}

@Component({
  selector: 'app-add-book',
  standalone: true,
  imports: [ReactiveFormsModule, Field, FormDialog],
  templateUrl: './add-book.html'
})
export class AddBookComponent {

  @Output() bookAdded = new EventEmitter<Book>();
  @ViewChild('dialog') dialog!: FormDialog;

  isSubmitting = signal(false);

  bookForm: FormGroup;

  constructor(
    private fb: FormBuilder,
    private bookService: BookService
  ) {
    this.bookForm = this.fb.group({
      title: [''],
      authors: [''],
      isbn: [''],
      number_of_pages: [null, [
        Validators.min(1),
        Validators.pattern(/^\d+$/)
      ]]
    }, {validators: validateBookPost});
  }

  open(): void {
    this.dialog.open();
  }

  onSubmit(): void {
    if (this.bookForm.invalid || this.isSubmitting()) {
      return;
    }

    this.isSubmitting.set(true);

    const form = this.bookForm.getRawValue();

    this.bookService.postBooks(
      form.authors || undefined,
      form.isbn! || undefined,
      form.number_of_pages! || undefined,
      form.title! || undefined
    )
      .pipe(
        finalize(() => this.isSubmitting.set(false))
      )
      .subscribe({
        next: book => {
          this.bookForm.reset();
          this.dialog.close();
          this.bookAdded.emit(book);
        },
        error: err => {
          console.error(err);
        }
      });
  }
}