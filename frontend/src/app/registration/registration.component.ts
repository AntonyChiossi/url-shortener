import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { NgbModal, NgbModalRef } from '@ng-bootstrap/ng-bootstrap';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-registration',
  templateUrl: './registration.component.html',
  styleUrls: ['./registration.component.scss'],
})
export class RegistrationComponent implements OnInit {
  public passwordMismatch: boolean;
  public modal: NgbModalRef;
  public email: string;
  public password: string;
  public password2: string;

  constructor(
    private fb: FormBuilder,
    private modalService: NgbModal,
    private authService: AuthService
  ) {}

  ngOnInit(): void {}

  checkPasswords({
    password,
    confirmPassword,
  }: {
    password: string;
    confirmPassword: string;
  }) {
    this.passwordMismatch = password !== confirmPassword;
    console.log({
      password,
      confirmPassword,
    });
    return password === confirmPassword ? null : { notSame: true };
  }

  open(content: any) {
    this.modal = this.modalService.open(content, {
      ariaLabelledBy: 'modal-basic-title',
    });
  }

  register() {
    // this.authService.login(this.registrationForm.value, this.password).subscribe((e) => {
    //   console.log({ e });
    //   this.modal.close();
    // });
    console.log({
      email: this.email,
      pass1: this.password,
      pass2: this.password2,
    });
    this.authService.register(this.email, this.password).subscribe((e) => {
      console.log({ e });
      this.authService
        .login(this.email, this.password)
        .subscribe((e) => this.modal.close());
    });
  }
}
