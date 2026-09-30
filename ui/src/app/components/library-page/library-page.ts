import { Component, computed, signal } from '@angular/core';
import { ActivatedRoute, RouterLink, RouterLinkActive } from '@angular/router';
import { Page } from '../shared/page/page';
import { DataTable } from '../shared/data-table/data-table';
import { BookService } from '../../services/book-service';
import { Book } from '../../interfaces/book';

@Component({
  selector: 'app-library-page',
  imports: [Page, RouterLink, RouterLinkActive, DataTable],
  templateUrl: './library-page.html',
})
export class LibraryPage {

  sections = [{ path: 'books', label: 'Books' }];
  section = signal<string | null>(null);
  title = computed(() => this.sections.find(s => s.path === this.section())?.label ?? 'Library');

  books = signal<Book[] | null>(null);
  bookColumns = [
    { key: 'title', label: 'Title' },
    { key: 'authors', label: 'Authors' },
    { key: 'pages', label: 'Pages' },
    { key: 'isbn', label: 'ISBN' },
    { key: 'added_by', label: 'Added by' }
  ];

  constructor(private bookService: BookService, route: ActivatedRoute) {
    route.paramMap.subscribe(params => {
      this.section.set(params.get('section'));
      this.books.set(null);
      if (this.section() === 'books') {
        this.bookService.getBooks().subscribe(res => this.books.set(res.books));
      }
    });
  }
}
