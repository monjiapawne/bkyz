import { Component, input } from '@angular/core';

@Component({
  selector: 'app-field',
  host: { class: 'block' },
  template: `<label class="block"><span class="form-label">{{ label() }}</span><ng-content /></label>`,
})
export class Field {
    label = input.required<string>();
}
