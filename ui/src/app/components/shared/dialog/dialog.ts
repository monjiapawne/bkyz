import { Component, ElementRef, input, viewChild } from '@angular/core';

@Component({
  selector: 'app-dialog',
  templateUrl: './dialog.html',
})
export class Dialog {
  heading = input.required<string>();
  private modal = viewChild.required<ElementRef<HTMLDialogElement>>('modal');

  open() { this.modal().nativeElement.showModal(); }
  close() { this.modal().nativeElement.close(); }
}
