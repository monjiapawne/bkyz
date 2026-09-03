import { Component, ElementRef, EventEmitter, Output, ViewChild, signal } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { debounceTime, distinctUntilChanged, filter, switchMap } from 'rxjs';
import { BookService } from '../../../services/book-service';
import { AddBookComponent } from '../add-book/add-book';
import { Book } from '../../../interfaces/book';

@Component({
  selector: 'app-search-book',
  standalone: true,
  imports: [ReactiveFormsModule, AddBookComponent],
  templateUrl: './search-book.html'
})
export class SearchBookComponent {

  @Output() bookSelected = new EventEmitter<Book>();
  @ViewChild('modal') modal!: ElementRef<HTMLDialogElement>;

  searchControl = new FormControl('');
  results = signal<Book[]>([]);
  isSearching = signal(false);

  constructor(private bookService: BookService) {
    this.searchControl.valueChanges
      .pipe(
        debounceTime(300),
        distinctUntilChanged(),
        filter((query): query is string => !!query && query.trim().length > 0),
        switchMap(query => {
          this.isSearching.set(true);
          return this.bookService.searchBooks(query);
        })
      )
      .subscribe({
        next: responseData => {
          this.results.set(responseData.books);
          this.isSearching.set(false);
        },
        error: err => {
          console.error(err);
          this.isSearching.set(false);
        }
      });
  }

  open(): void {
    this.searchControl.reset('');
    this.results.set([]);
    this.modal.nativeElement.showModal();
  }

  selectBook(book: Book): void {
    this.bookSelected.emit(book);
    this.modal.nativeElement.close();
  }

  onBookAdded(book: Book): void {
    this.bookSelected.emit(book);
    this.modal.nativeElement.close();
  }

  close(): void {
    this.modal.nativeElement.close();
  }
}