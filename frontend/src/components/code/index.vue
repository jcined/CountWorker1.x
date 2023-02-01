<template>
    <div class="code-menu-header">
        <el-menu :default-active="activeIndex" class="el-menu-demo" mode="horizontal" @select="handleSelect">
            <el-menu-item index="1">编辑</el-menu-item>
        </el-menu>
    </div>
    <el-input v-model="Sname" disabled placeholder="Please input"
        style="padding: 10px 20px;height: 60px;margin-bottom: 10px;">
        <template #prepend>名称</template>
    </el-input>
    <div id="container" style="height: 100%"></div>
    <v-divider></v-divider>
    <div class="bottom-dom">
        <el-button @click="Save" type="primary" plain style="width: 80px;height: 35px;">保存</el-button>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as monaco from 'monaco-editor/esm/vs/editor/editor.api.js'
import 'monaco-editor/esm/vs/basic-languages/python/python.contribution'
import { useRoute } from 'vue-router'
import { Url } from '../../Store/store'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { debounce } from '../../hook/debounce'

const route = useRoute()

const url = Url()

const value = ref('')
let editor: any

const getUrlParam = (name: string) => {
    let url = window.location.search.substring(1)
    let params = url.split('&')
    for (let i = 0; i < params.length; i++) {
        let pair = params[i].split('=')
        if (pair[0] == name) {
            return pair[1]
        }
    }
    return null
}

const pam = getUrlParam("path")
const Sname = pam?.split("/").slice(-1)[0]
const ID = pam?.split("/").slice(0)[0]

axios.get(`${url.ip}/api${route.fullPath}`)
    .then((response) => {
        value.value = response.data.data
    })

watch(value, () => {
    console.log("change")
    editor.setValue(value.value)
})

const keydownEvent = (event: any) => {
    if (event.code === 'KeyS' && (event.ctrlKey || event.metaKey)) {
        event.preventDefault()
        Save()
    }
}
document.addEventListener('keydown', keydownEvent)

onMounted(() => {
    editor = monaco.editor.create(document.getElementById("container") as HTMLElement, {
        value: value.value,
        // theme: "vs-dark",
        language: "python"
    })
})

onUnmounted(() => {
    console.log("卸载组件了");
    document.removeEventListener('keydown', keydownEvent)
})

const activeIndex = ref('1')
const handleSelect = (key: string, keyPath: string[]) => {
    console.log(key, keyPath)
}

const Save = () => {
    const code = editor.getValue()
    console.log(code)
    const debouncedRequest = debounce(() => {
        axios.post(`${url.ip}${url.upload}?id=${ID}`, {
            "Files": {
                "main": null,
                "config": null,
                "other": [{
                    "fileName": Sname,
                    "data": code,
                }],
                "exchanges": null,
            }
        })
            .then((response) => {
                ElMessage({
                    message: '保存成功',
                    type: 'success',
                })
            })
            .catch((error) => {
                ElMessage.error('保存失败')
            })
    }, 1000)

    debouncedRequest()
}

</script>

<style scoped lang="less">
.code-menu-header {
    padding: 0 20px;
}

.bottom-dom {
    padding: 10px 20px;
    display: flex;
    justify-content: space-between;
}
</style>
