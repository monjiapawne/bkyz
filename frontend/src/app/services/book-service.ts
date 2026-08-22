import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { Book } from '../interfaces/book';
import { BookResponse } from '../interfaces/book-response';

@Injectable({
  providedIn: 'root',
})
export class BookService {

  private readonly API_URL = `${environment.apiUrl}/books`;

  constructor(private http: HttpClient) { }

  getBooks() {
    return this.http.get<BookResponse>(this.API_URL)
  }

  postBooks(authors: string, isbn: number, numberOfPages: number, title: string) {
    return this
  }

}
