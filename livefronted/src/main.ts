/**
 * main.ts
 *
 * Bootstraps Vuetify and other plugins then mounts the App`
 */
// Components
import App from './App.vue'

// Composables
import { createApp } from 'vue'

// Pinia
import { createPinia } from 'pinia'

// Plugins
import { registerPlugins } from '@/plugins'

// Router
import router from './router'

//VuetifyIcon
import { createVuetify } from 'vuetify'
import { aliases, mdi } from 'vuetify/iconsets/mdi'

//ElementPlus
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

//Animate.css
import 'animate.css'

export default createVuetify({
    icons: {
        defaultSet: 'mdi',
        aliases,
        sets: {
            mdi,
        }
    },
})

const app = createApp(App)

const store = createPinia()

app.use(store)

app.use(ElementPlus)

registerPlugins(app)

app.use(router)



app.mount('#app')
