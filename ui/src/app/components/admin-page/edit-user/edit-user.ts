import { Component, inject, output, ViewChild } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
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

  private editing?: User;

  userForm = inject(FormBuilder).nonNullable.group({
    username: ['', Validators.required],
    is_admin: [false],
    password: [''],
  });

  constructor(private auth: Auth) { }

  open(user: User) {
    this.editing = user;
    this.userForm.reset({ ...user, password: '' });
    this.dialog.open();
  }

  save = () => {
    const { password, ...changes } = this.userForm.getRawValue();
    return this.auth.patchUser(this.editing!.id, password ? { ...changes, password } : changes);
  };
}
