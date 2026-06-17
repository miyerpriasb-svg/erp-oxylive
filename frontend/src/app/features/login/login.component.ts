import { HttpErrorResponse } from '@angular/common/http';
import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { finalize } from 'rxjs';
import { AuthService } from '../../core/auth/auth.service';

@Component({
  selector: 'app-login',
  imports: [ReactiveFormsModule],
  templateUrl: './login.component.html',
  styleUrl: './login.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LoginComponent {
  private readonly formBuilder = inject(FormBuilder);
  private readonly auth = inject(AuthService);

  protected readonly loading = signal(false);
  protected readonly errorMessage = signal('');
  protected readonly passwordVisible = signal(false);

  protected readonly form = this.formBuilder.nonNullable.group({
    usuario: ['', [Validators.required]],
    password: ['', [Validators.required]],
  });

  protected submit(): void {
    if (this.form.invalid || this.loading()) {
      this.form.markAllAsTouched();
      return;
    }

    this.errorMessage.set('');
    this.loading.set(true);

    this.auth.login(this.form.getRawValue()).pipe(
      finalize(() => this.loading.set(false)),
    ).subscribe({
      next: (session) => this.auth.openAssignedWorkspace(session),
      error: (error: HttpErrorResponse) => {
        const detail = typeof error.error?.detail === 'string' ? error.error.detail : '';
        this.errorMessage.set(detail || 'Usuario o contrasena incorrectos.');
      },
    });
  }

  protected togglePassword(): void {
    this.passwordVisible.update((visible) => !visible);
  }
}
