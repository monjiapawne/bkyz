import { inject } from '@angular/core';
import { CanActivateFn, Router, Routes } from '@angular/router';
import { catchError, map, of } from 'rxjs';
import { LoginPage } from './components/login-page/login-page';
import { RegisterPage } from './components/register-page/register-page';
import { HomePage } from './components/home-page/home-page';
import { Dashboard } from './components/dashboard/dashboard';
import { Auth } from './services/auth-service';

const guestOnly: CanActivateFn = () => {
    const router = inject(Router);
    return inject(Auth).getUser().pipe(
        map(() => router.parseUrl('/dashboard')),
        catchError(() => of(true))
    );
};

const authOnly: CanActivateFn = () => {
    const router = inject(Router);
    return inject(Auth).getUser().pipe(
        map(() => true),
        catchError(() => of(router.parseUrl('/login')))
    );
};

export const routes: Routes = [
    { path: '', component: HomePage, canActivate: [guestOnly] },
    { path: 'login', component: LoginPage, canActivate: [guestOnly] },
    { path: 'register', component: RegisterPage, canActivate: [guestOnly] },
    { path: 'dashboard', component: Dashboard, canActivate: [authOnly] },
    { path: 'playlists/:id', component: Dashboard, canActivate: [authOnly] }
];
