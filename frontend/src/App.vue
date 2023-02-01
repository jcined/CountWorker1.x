<template>
    <v-app>
        <v-navigation-drawer v-if="ProjectId!='login'" :elevation="0" color="primary">
            <navigation></navigation>
        </v-navigation-drawer>
        <v-main>
            <router-view/>
        </v-main>
    </v-app>
</template>

<script setup lang="ts">
import navigation from './components/navigation/index.vue'
import { Url, Data } from './Store/store'
import axios from 'axios'

const url = Url()
const data = Data()

const ProjectId = window.location.href.split('/').pop()

axios.get(`${url.ip}${url.init}`)
    .then((response) => {
        data.data = response.data.data
        console.log("success")
    })
    .catch((error) => {

    })

</script>

<style lang="less">

</style>
