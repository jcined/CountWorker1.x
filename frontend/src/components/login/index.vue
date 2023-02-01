<template>
    <div id="Login">
        <transition enter-active-class="animate__animated animate__fadeIn" appear>
            <v-card class="mx-auto px-6 py-8" max-width="344" style="width: 100%;">
                <div class="header">
                    <img src="../../assets/logo.png">
                    <div>CountWorker</div>
                </div>

                <v-form v-model="form" @submit.prevent="onSubmit">
                    <v-text-field v-model="account" variant="underlined" :readonly="loading" :rules="[required]"
                        class="mb-2" clearable label="账号"></v-text-field>

                    <v-text-field type="password" v-model="password" variant="underlined" :readonly="loading" :rules="[required]"
                        clearable label="密码"></v-text-field>

                    <br>

                    <v-btn :disabled="!form" :loading="loading" block color="primary" size="large" type="submit"
                        variant="elevated">
                        登录
                    </v-btn>
                </v-form>
            </v-card>
        </transition>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import {Url} from '../../Store/store'
import axios from 'axios'

const form = ref(false)
const account = ref()
const password = ref()
const loading = ref()

const url = Url()

const router = useRouter()

const onSubmit = () => {
    if (!form.value) return
    loading.value = true
    axios.post(`${url.ip}${url.login}`, {
        "account": account,
        "password": password,
    })
        .then((response) => {
            console.log(response)
            ElMessage({
                message: '登录成功',
                type: 'success',
            })
            location.replace("/")
        })
        .catch((error) => {
            console.log(error)
            ElMessage.error('登录失败,账号或密码错误')
            loading.value = false
        })
}

const required = (v: any) => {
    return !!v || '内容不能为空'
}

</script>

<style scoped lang="less">
#Login {
    .header {
        font-size: 30px;
        font-weight: 700;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 100%;
        margin-bottom: 20px;

        img {
            height: 100px;
        }
    }

    height: 100vh;
    display: flex;
    align-items: center;
}
</style>