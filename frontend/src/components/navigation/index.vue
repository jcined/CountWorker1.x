<template>
    <div class="header">
        <img class="h-logo" src="../../assets/logo.png" />
        <div class="h-name">CountWorker</div>
    </div>
    <v-layout>
        <v-navigation-drawer floating permanent color="primary">
            <v-list density="compact">
                <v-list-item @click="toPage('/')" :active="route.name == '/'" prepend-icon="mdi-home" title="仓库"
                    value="project"></v-list-item>
                <v-list-item @click="toPage('/live')" :active="route.name == '/live'" prepend-icon="mdi-database"
                    title="实盘" value="live"></v-list-item>
            </v-list>
        </v-navigation-drawer>
        <v-main style="height: 550px"></v-main>
    </v-layout>
</template>

<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const toPage = (url: string) => {
    router.push(url)
}
</script>

<style lang="less">
.header {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;

    .h-logo {
        width: 60px;
    }

    .h-name {
        font-weight: 700;
    }
}
</style>
