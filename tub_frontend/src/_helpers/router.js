import Vue from 'vue'
import Router from 'vue-router'


Vue.use(Router);

export const router = new Router({
    mode: 'history',
    routes: [
        { path: '/percursos/:ID', component: () => import('../components/RoutePage')},
        { path: '*', redirect: '/percursos/2'}
    ]
})