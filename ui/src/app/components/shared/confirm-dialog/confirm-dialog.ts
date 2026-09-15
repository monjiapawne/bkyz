import { Component, ElementRef, input, viewChild, output } from '@angular/core';

@Component({
  selector: 'app-confirm-dialog',
  imports: [],
  templateUrl: './confirm-dialog.html',
})
export class ConfirmDialog {
    resourceName = input<string>()
    dialog = viewChild.required<ElementRef<HTMLDialogElement>>('modal');
    confirmed = output<void>();

    open() { this.dialog().nativeElement.showModal(); }
}
