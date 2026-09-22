import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Book } from '../interfaces/book';
import { BookResponse } from '../interfaces/book-response';

@Injectable({
  providedIn: 'root',
})
export class BookService {

  private readonly API_URL = `${environment.apiUrl}/books`;

  constructor(private http: HttpClient) { }

  getBooks(title?: string) {
    const params = title ? new HttpParams().set('title', title) : new HttpParams();
    return this.http.get<BookResponse>(this.API_URL, { params, withCredentials: true });
  }

  postBooks(authors?: string, isbn?: number, numberOfPages?: number, title?: string) {
    const body = {
      "authors": authors,
      "isbn": isbn,
      "number_of_pages": numberOfPages,
      "title": title
    }

    return this.http.post<Book>(this.API_URL, body, { withCredentials: true });
  }

}
