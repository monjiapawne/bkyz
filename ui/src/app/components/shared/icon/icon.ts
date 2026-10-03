import { Component, input } from '@angular/core';

@Component({
  selector: 'app-icon',
  host: { class: 'block' },
  templateUrl: './icon.html',
})
export class Icon {
  name = input.required<'sidebar' | 'edit' | 'history' | 'check' | 'close'>();
}
