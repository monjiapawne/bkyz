import { Component, ElementRef, input, output, viewChild } from '@angular/core';
import { AbstractControl } from '@angular/forms';

@Component({
  selector: 'app-form-dialog',
  templateUrl: './form-dialog.html',
})
export class FormDialog {

  title = input.required<string>();
  form = input.required<AbstractControl>();
  submitLabel = input('Save');
  submitting = input(false);
  deletable = input(false);

  submitted = output<void>();
  deleted = output<void>();

  private modal = viewChild.required<ElementRef<HTMLDialogElement>>('modal');

  open() { this.modal().nativeElement.showModal(); }
  close() { this.modal().nativeElement.close(); }

  submit() {
    if (this.form().valid && !this.submitting()) this.submitted.emit();
  }
}
