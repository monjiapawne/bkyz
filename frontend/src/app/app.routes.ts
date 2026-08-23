import { Routes } from '@angular/router';
import { LoginPage } from './components/login-page/login-page';
import { RegisterPage } from './components/register-page/register-page';
import { HomePage } from './components/home-page/home-page';
import { Dashboard } from './components/dashboard/dashboard';


export const routes: Routes = [
    { path: '', component: HomePage },
    { path: 'login', component: LoginPage },
    { path: 'register', component: RegisterPage },
    { path: 'dashboard', component: Dashboard },
    { path: 'playlists/:id', component: Dashboard }
];
