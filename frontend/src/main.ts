/**
 * main.ts
 *
 * Bootstraps Vuetify and other plugins then mounts the App`
 */

// Components
import App from './App.vue'

// Composables
import { createApp } from 'vue'

// pinia
import {createPinia} from 'pinia'

// Plugins
import { registerPlugins } from '@/plugins'

// router
import router from './router'

// element-plus
import ElementPlus from 'element-plus'

import 'element-plus/dist/index.css'

const app = createApp(App)

const store = createPinia()

app.use(store)

app.use(router)

app.use(ElementPlus)

registerPlugins(app)

app.mount('#app')
