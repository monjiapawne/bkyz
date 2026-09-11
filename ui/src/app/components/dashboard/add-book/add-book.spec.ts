import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AddBook } from './add-book';

describe('AddBook', () => {
  let component: AddBook;
  let fixture: ComponentFixture<AddBook>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AddBook]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AddBook);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
