import { Component, inject, input } from '@angular/core';
import { ControlContainer, ReactiveFormsModule } from '@angular/forms';

export interface Option {
  value: unknown;
  label: string;
}

@Component({
  selector: 'app-field',
  imports: [ReactiveFormsModule],
  host: { class: 'block' },
  viewProviders: [{ provide: ControlContainer, useFactory: () => inject(ControlContainer, { skipSelf: true, optional: true }) }],
  templateUrl: './field.html',
})
export class Field {
  label = input.required<string>();
  name = input<string>();
  type = input<'text' | 'number' | 'password' | 'textarea' | 'checkbox' | 'select'>('text');
  options = input<Option[]>([]);
  placeholder = input('');
  rows = input(3);
  min = input<number>();
  maxlength = input<number>();
}
