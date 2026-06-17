import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { AuthService } from '../../core/auth/auth.service';

@Component({
  selector: 'app-migration',
  template: `
    <main class="migration-view">
      <section>
        <img src="/assets/oxylive-logo.png" alt="Oxylive">
        <p class="eyebrow">Migracion Angular</p>
        <h1>Sesion conectada</h1>
        <p>{{ auth.session()?.nombre }}</p>
        <button type="button" (click)="openWorkspace()">Abrir espacio asignado</button>
      </section>
    </main>
  `,
  styles: `
    .migration-view { min-height: 100vh; display: grid; place-items: center; padding: 24px; background: radial-gradient(circle at 15% 15%, rgba(79,194,62,.16), transparent 30%), linear-gradient(135deg, #123f71, #1f6fa8 58%, #278878); }
    section { width: min(520px, 100%); border: 1px solid #d8e4e9; border-radius: 16px; background: white; padding: 32px; box-shadow: 0 24px 65px rgba(20,58,88,.28); }
    img { width: 104px; height: 72px; object-fit: contain; margin-bottom: 20px; }
    .eyebrow { color: #1f6fa8; font-weight: 700; text-transform: uppercase; font-size: 12px; }
    h1 { margin: 8px 0; }
    button { border: 0; border-radius: 9px; background: linear-gradient(110deg, #185d93, #1f6fa8 70%, #278878); color: white; padding: 12px 18px; cursor: pointer; }
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
