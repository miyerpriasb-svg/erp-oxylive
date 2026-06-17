import { HttpClient } from '@angular/common/http';
import { Injectable, computed, inject, signal } from '@angular/core';
import { Observable, tap } from 'rxjs';
import { LoginCredentials, UserSession } from './auth.models';

const SESSION_KEY = 'oxyliveSession';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly sessionState = signal<UserSession | null>(this.readSession());

  readonly session = this.sessionState.asReadonly();
  readonly isAuthenticated = computed(() => this.sessionState() !== null);

  login(credentials: LoginCredentials): Observable<UserSession> {
    return this.http.post<UserSession>('/auth/login', credentials).pipe(
      tap((session) => {
        localStorage.setItem(SESSION_KEY, JSON.stringify(session));
        this.sessionState.set(session);
      }),
    );
  }

  logout(): void {
    localStorage.removeItem(SESSION_KEY);
    this.sessionState.set(null);
  }

  openAssignedWorkspace(session: UserSession): void {
    window.location.assign(session.redirect || '/admin');
  }

  hasAnyRole(roles: readonly string[]): boolean {
    const currentRoles = this.sessionState()?.roles ?? [];
    return roles.some((role) => currentRoles.includes(role));
  }

  private readSession(): UserSession | null {
    try {
      const rawSession = localStorage.getItem(SESSION_KEY);
      return rawSession ? (JSON.parse(rawSession) as UserSession) : null;
    } catch {
      localStorage.removeItem(SESSION_KEY);
      return null;
    }
  }
}
