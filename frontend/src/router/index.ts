//引入路由对象
import { createRouter, createWebHistory, createWebHashHistory, createMemoryHistory, RouteRecordRaw } from 'vue-router'

const routes: Array<RouteRecordRaw> = [
    {
        path: '/',
        name: '/',
        component: () => import('../components/strategists/index.vue'),
    },
    {
        path: '/live',
        name: '/live',
        component: () => import('../components/liveTrading/index.vue')
    },
    {
        path: "/s/code/:id",
        name: "strategistCode",
        component: () => import('../components/strategistCode/index.vue'),
    },
    {
        path: "/code",
        name: "code",
        component: () => import('../components/code/index.vue'),
    },
    {
        path: "/login",
        name: "login",
        component: () => import('../components/login/index.vue'),
    }
]


const router = createRouter({
    history: createWebHistory(),
    routes
})

router.beforeEach((to, from, next) => {
    console.log("要切换路由了")
    to.meta.keepAlive = false
    next()
})

export default router