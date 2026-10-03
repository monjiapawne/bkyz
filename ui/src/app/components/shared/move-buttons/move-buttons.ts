import { Component, output } from '@angular/core';

@Component({
  selector: 'app-move-buttons',
  template: `
    <span class="form-label">Order</span>
    <div class="flex gap-2">
      <button type="button" class="btn-neutral" (click)="move.emit('up')" aria-label="Move up">↑</button>
      <button type="button" class="btn-neutral" (click)="move.emit('down')" aria-label="Move down">↓</button>
    </div>
  `,
})
export class MoveButtons {
  move = output<'up' | 'down'>();
}
