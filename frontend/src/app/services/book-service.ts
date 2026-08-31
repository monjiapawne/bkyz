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

  getBook(id: number) {
    return this.http.get<Book>(`${this.API_URL}/${id}`, { withCredentials: true });
  }

  getBooks() {
    return this.http.get<BookResponse>(this.API_URL, { withCredentials: true });
  }

  getBookCover(id: number) {
    return this.http.get(`${this.API_URL}/${id}/cover`, { responseType: 'blob', withCredentials: true });
  }

  postBooks(authors: string, isbn: number, numberOfPages: number, title: string) {
    const body = {
      "authors": authors,
      "isbn": isbn,
      "numberOfPages": numberOfPages,
      "title": title
    }

    return this.http.post<Book>(this.API_URL, body, { withCredentials: true });
  }

  patchBook(authors: string, isbn: number, numberOfPages: number, title: string, id: number) {
    const body = {
      "authors": authors,
      "isbn": isbn,
      "numberOfPages": numberOfPages,
      "title": title
    }

    return this.http.patch<Book>(`${this.API_URL}/${id}`, body, { withCredentials: true });
  }

  deleteBook(id: number) {
    return this.http.delete<Book>(`${this.API_URL}/${id}`, { withCredentials: true });
  }

}
