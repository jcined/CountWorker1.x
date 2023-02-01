<template>
    <v-layout>
        <v-app-bar color="primary" density="compact" height="80" position="fixed">
            <v-app-bar-title>{{ State.Name }}</v-app-bar-title>

            <v-menu>
                <template v-slot:activator="{ props }">
                    <v-btn icon="mdi-dots-vertical" dark v-bind="props"></v-btn>
                </template>

                <v-list>
                    <v-list-item @click="config" :disabled="State.isLoding || sData.exchanges.length == 0">
                        <v-list-item-title>{{ State.state ? "停止" : "启动" }}</v-list-item-title>
                    </v-list-item>
                </v-list>
            </v-menu>

        </v-app-bar>
        <v-bottom-navigation grow>
            <v-btn value="panel" :active="route.name == 'chart'" @click="toPage(`/live/chart/${ProjectId}`)">
                <v-icon>mdi-history</v-icon>
                图表
            </v-btn>

            <v-btn value="log" :active="route.name == 'logs'" @click="toPage(`/live/logs/${ProjectId}`)">
                <v-badge v-if="State.toBeVlog > 0" max="99" :content="State.toBeVlog" color="error">
                    <v-icon icon="mdi-post"></v-icon>
                </v-badge>
                <v-icon v-else="" icon="mdi-post"></v-icon>
                日志
            </v-btn>

            <v-btn value="config" :active="route.name == 'setting'" @click="toPage(`/live/setting/${ProjectId}`)">
                <v-icon>mdi-cog</v-icon>
                设置
            </v-btn>
        </v-bottom-navigation>
    </v-layout>
</template>

<script setup lang="ts">
import { state, strategyData } from '../store/store'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'

const ProjectId = window.location.href.split('/').pop()

const router = useRouter()
const route = useRoute()

const toPage = (url: string) => {
    router.push(url)
}

const State = state()
const sData = strategyData()

const config = () => {
    State.isLoding = true
    if (!State.state) {
        axios.get("/api/start?id="+ProjectId)
        .then((response) => {
            State.state = true
        })
        .catch((error) => {

        })
        .finally(() => {
            State.isLoding = false
        })
    } else {
        axios.get("/api/stop?id="+ProjectId)
        .then(() => {
            State.state = false
        })
        .catch((error) => {
            
        })
        .finally(() => {
            State.isLoding = false
        })
    }
}
</script>

<style scoped lang="less">

</style>