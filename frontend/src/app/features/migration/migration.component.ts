import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { AuthService } from '../../core/auth/auth.service';

@Component({
  selector: 'app-migration',
  template: `
    <main class="migration-view">
      <section>
        <p class="eyebrow">Migracion Angular</p>
        <h1>Sesion conectada</h1>
        <p>{{ auth.session()?.nombre }}</p>
        <button type="button" (click)="openWorkspace()">Abrir espacio asignado</button>
      </section>
    </main>
  `,
  styles: `
    .migration-view { min-height: 100vh; display: grid; place-items: center; padding: 24px; background: #eef3f3; }
    section { width: min(520px, 100%); border: 1px solid #c8d5d6; background: white; padding: 32px; }
    .eyebrow { color: #087f78; font-weight: 700; text-transform: uppercase; font-size: 12px; }
    h1 { margin: 8px 0; }
    button { border: 0; background: #102b36; color: white; padding: 12px 18px; cursor: pointer; }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MigrationComponent {
  protected readonly auth = inject(AuthService);

  protected openWorkspace(): void {
    const session = this.auth.session();
    if (session) this.auth.openAssignedWorkspace(session);
  }
}
