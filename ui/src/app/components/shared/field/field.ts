import { Component, inject, input } from '@angular/core';
import { ControlContainer, ReactiveFormsModule } from '@angular/forms';
import { StarRating } from '../star-rating/star-rating';

export interface Option {
  value: unknown;
  label: string;
}

@Component({
  selector: 'app-field',
  imports: [ReactiveFormsModule, StarRating],
  host: { class: 'block' },
  viewProviders: [{ provide: ControlContainer, useFactory: () => inject(ControlContainer, { skipSelf: true, optional: true }) }],
  templateUrl: './field.html',
})
export class Field {
  label = input.required<string>();
  name = input<string>();
  type = input<'text' | 'number' | 'password' | 'textarea' | 'checkbox' | 'select' | 'rating'>('text');
  options = input<Option[]>([]);
  placeholder = input('');
  rows = input(3);
  min = input<number>();
  maxlength = input<number>();
}
