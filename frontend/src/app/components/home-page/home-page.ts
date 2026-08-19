import { Component, signal, WritableSignal } from '@angular/core';
import { Book } from '../../interfaces/book';
import { BookService } from '../../services/book-service';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-home-page',
  imports: [FormsModule, CommonModule],
  templateUrl: './home-page.html',
  styleUrl: './home-page.css',
})
export class HomePage {

  constructor(private bookService: BookService) { }

  books: WritableSignal<Book[]> = signal([]);

  ngOnInit(): void {
    this.loadBooks();
  }

  loadBooks() {
    this.bookService.getBooks()
      .subscribe({
        next: responseData => {
          this.books.set(responseData.books);
        },
        error: err => {
          console.log(err);
        }
      })
  }
}
