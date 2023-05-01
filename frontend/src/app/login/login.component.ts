import { Component, OnInit } from '@angular/core';
import {
  NgbModal,
  ModalDismissReasons,
  NgbModalRef,
} from '@ng-bootstrap/ng-bootstrap';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss'],
})
export class LoginComponent implements OnInit {
  public closeResult = '';
  public email = '';
  public password = '';
  public modal: NgbModalRef;
  constructor(
    private modalService: NgbModal,
    private authService: AuthService
  ) {}

  ngOnInit(): void {}

  open(content: any) {
    this.modal = this.modalService.open(content, {
      ariaLabelledBy: 'modal-basic-title',
    });
  }

  login() {
    this.authService.login(this.email, this.password).subscribe((e) => {
      console.log({ e });
      this.modal.close();
    });
  }
}
