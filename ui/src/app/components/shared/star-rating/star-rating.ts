import { Component, signal } from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';

@Component({
  selector: 'app-star-rating',
  providers: [{ provide: NG_VALUE_ACCESSOR, useExisting: StarRating, multi: true }],
  templateUrl: './star-rating.html',
})
export class StarRating implements ControlValueAccessor {

  steps = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
  value = signal<number | null>(null);
  hover = signal<number | null>(null);

  private onChange = (_: number | null) => { };
  private onTouched = () => { };

  set(value: number | null) {
    this.value.set(value);
    this.onChange(value);
    this.onTouched();
  }

  writeValue(value: number | null) { this.value.set(value); }
  registerOnChange(fn: (value: number | null) => void) { this.onChange = fn; }
  registerOnTouched(fn: () => void) { this.onTouched = fn; }
}
