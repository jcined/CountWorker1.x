<template>
    <Bar></Bar>
    <div id="Setting">
        <keep-alive>
            <setting></setting>
        </keep-alive>
        <keep-alive>
            <strategyConfig></strategyConfig>
        </keep-alive>
        <div class="setting-save">
            <v-btn @click="save" :disabled="false" :loading="loading" color="primary" style="width:280px;height: 46px;">
                上传
            </v-btn>
        </div>
    </div>
</template>

<script setup lang="ts">
import setting from './settingmain.vue'
import strategyConfig from './strategyConfig.vue'
import Bar from '../appBars.vue'
import { ref } from 'vue'
import axios from 'axios'
import { upConfig, state, strategyData } from '../../store/store'
import { ElMessage } from 'element-plus'
import Sinit from '../../hooks/Sinit'
Sinit()
const sData = strategyData()
const upcnfig = upConfig()
const State = state()
const loading = ref(false)
const error = (message: string) => {
    ElMessage.error(message)
    loading.value = false
}
//上传文件
const save = () => {
    loading.value = true
    //校验数据
    if (State.state) {
        error("策略正在运行")
        return
    }
    if (
        upcnfig.Files.main == null ||
        upcnfig.Files.config == null
    ) {
        error("请上传完整数据")
        return
    }
    //上传配置
    console.log({
        Files: upcnfig.Files,
    })
    axios.post('/api/upload', {
        Files: upcnfig.Files
    })
        .then((response) => {
            console.log(response)
            loading.value = false
            // 更新配置
            const result = response.data?.data
            State.Name = result.Name
            upcnfig.Name = result.Name
            State.AltExchanges = result.exchanges
            upcnfig.CusConfig = result.config
            sData.setExchanges(result.exchanges)
            upcnfig.Exchanges = result.exchanges
            ElMessage({
                message: '文件上传成功',
                type: 'success',
            })
        })
        .catch((error) => {
            console.log(error)
            error("上传失败,请检查网络或文件内容")
            loading.value = false
        })
}
</script>

<style scoped lang="less">
#Setting {
    @media screen and (min-width: 800px) {
        padding: 0 28%;
    }

    width: 100%;
    box-sizing: border-box;
    margin: 64px 0;

    .setting-save {
        margin-top: 20px;
        width: 100%;
        display: flex;
        justify-content: center;
    }

}
</style>