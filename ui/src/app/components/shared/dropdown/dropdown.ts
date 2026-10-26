import { Component, ElementRef, input, model, signal } from '@angular/core';
import { Icon } from '../icon/icon';

@Component({
  selector: 'app-dropdown',
  imports: [Icon],
  host: {
    class: 'relative inline-block',
    '(document:click)': 'onDocumentClick($event)',
    '(document:keydown.escape)': 'open.set(false)'
  },
  templateUrl: './dropdown.html',
})
export class Dropdown<T extends string> {
  label = input.required<string>();
  options = input.required<readonly T[]>();
  value = model.required<T>();
  open = signal(false);

  constructor(private el: ElementRef<HTMLElement>) { }

  onDocumentClick(event: Event) {
    if (!this.el.nativeElement.contains(event.target as Node)) this.open.set(false);
  }

  select(option: T) {
    this.value.set(option);
    this.open.set(false);
  }
}
