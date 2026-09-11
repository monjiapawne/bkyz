import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AddPlaylist } from './add-playlist';

describe('AddPlaylist', () => {
  let component: AddPlaylist;
  let fixture: ComponentFixture<AddPlaylist>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AddPlaylist]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AddPlaylist);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
