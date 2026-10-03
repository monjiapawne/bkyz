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
  type = input<'text' | 'number' | 'password' | 'textarea' | 'checkbox' | 'select' | 'rating' | 'date'>('text');
  options = input<Option[]>([]);
  placeholder = input('');
  rows = input(3);
  min = input<number>();
  maxlength = input<number>();

  private container = inject(ControlContainer);

  clear() {
    const control = this.container.control?.get(this.name()!);
    control?.setValue(null);
    control?.markAsDirty();
  }
}
