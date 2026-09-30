import { Component, inject, output, signal, ViewChild } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { finalize } from 'rxjs';
import { Field } from '../../shared/field/field';
import { FormDialog } from '../../shared/form-dialog/form-dialog';
import { Auth } from '../../../services/auth-service';
import { User } from '../../../interfaces/user';

@Component({
  selector: 'app-edit-user',
  imports: [ReactiveFormsModule, Field, FormDialog],
  templateUrl: './edit-user.html',
})
export class EditUser {

  @ViewChild('dialog') dialog!: FormDialog;
  saved = output<void>();

  isSubmitting = signal(false);
  private editing?: User;

  userForm = inject(FormBuilder).nonNullable.group({
    username: ['', Validators.required],
    is_admin: [false],
  });

  constructor(private auth: Auth) { }

  open(user: User) {
    this.editing = user;
    this.userForm.reset(user);
    this.dialog.open();
  }

  onSubmit() {
    this.isSubmitting.set(true);
    this.auth.patchUser(this.editing!.id, this.userForm.getRawValue())
      .pipe(finalize(() => this.isSubmitting.set(false)))
      .subscribe(() => {
        this.dialog.close();
        this.saved.emit();
      });
  }
}
