import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AddTrack } from './add-track';

describe('AddTrack', () => {
  let component: AddTrack;
  let fixture: ComponentFixture<AddTrack>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AddTrack]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AddTrack);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
