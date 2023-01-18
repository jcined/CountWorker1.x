import { createRouter, createWebHistory, createWebHashHistory, createMemoryHistory, RouteRecordRaw } from 'vue-router'

const routes: Array<RouteRecordRaw> = [
    {
        path: '/chart',
        name: 'chart',
        component: () => import('../components/panel/index.vue'),
    },
    {
        path: '/logs',
        name: 'logs',
        component: () => import('../components/log/index.vue'),
    },
    {
        path: '/setting',
        name: 'setting',
        component: () => import('../components/setting/index.vue')
    },
    {
        path: '/login',
        name: 'login',
        component: () => import('../components/login/index.vue')
    }
]

const scrollBehavior = function scrollBehavior(to: any, from: any, savedPosition: any) {
    if (savedPosition) {
        return savedPosition;
    } else {
        return { x: 0, y: 0 }
    }
}

const router = createRouter({
    history: createWebHistory(),
    routes,
    scrollBehavior,
})

export default router