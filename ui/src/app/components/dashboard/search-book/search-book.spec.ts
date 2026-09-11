import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SearchBook } from './search-book';

describe('SearchBook', () => {
  let component: SearchBook;
  let fixture: ComponentFixture<SearchBook>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SearchBook]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SearchBook);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
