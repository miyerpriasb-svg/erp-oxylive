export interface LoginCredentials {
  usuario: string;
  password: string;
}

export interface UserSession {
  id: number;
  nombre: string;
  usuario: string;
  rol: string;
  roles: string[];
  redirect: '/admin' | '/operativo' | string;
}
