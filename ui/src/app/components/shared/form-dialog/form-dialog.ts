import { Component, inject, input, output, signal, viewChild } from '@angular/core';
import { FormGroupDirective } from '@angular/forms';
import { finalize, Observable } from 'rxjs';
import { NotificationService } from '../../../services/notification-service';
import { Dialog } from '../dialog/dialog';

@Component({
  selector: 'app-form-dialog',
  imports: [Dialog],
  templateUrl: './form-dialog.html',
})
export class FormDialog {

  title = input.required<string>();
  save = input.required<() => Observable<any>>();
  submitLabel = input('Save');
  deletable = input(false);
  savedMessage = input('Saved');

  saved = output<any>();
  deleted = output<void>();

  submitting = signal(false);
  private formGroup = inject(FormGroupDirective, { self: true });
  private notifications = inject(NotificationService);
  private dialog = viewChild.required(Dialog);

  get form() { return this.formGroup.form; }

  open() { this.dialog().open(); }
  close() { this.dialog().close(); }

  submit() {
    if (this.form.invalid || this.submitting()) return;
    this.submitting.set(true);
    this.save()()
      .pipe(finalize(() => this.submitting.set(false)))
      .subscribe(result => {
        this.close();
        this.notifications.show(this.savedMessage(), 'info', 'short');
        this.saved.emit(result);
      });
  }
}
