<template>
    <!-- 自定义状态 -->
    <div id="stateCustom">
        <div :key="custom" v-for="(stateCus,custom) in cData.stateCustom">
            <v-card v-if="isTables(stateCus)">
                <v-tabs v-model="tab[custom]">
                    <v-tab :key="index" v-for="(item, index) in stateCus" :value="index">
                        {{ item.title }}
                    </v-tab>
                </v-tabs>

                <v-card-text>
                    <v-window v-model="tab[custom]">
                        <v-window-item :key="index" v-for="(_, index) in stateCus" :value="index">
                            <Table :data="stateCus[index]?.tables"></Table>
                            <div>{{ stateCus[index]?.tables?.text }}</div>
                        </v-window-item>
                    </v-window>
                </v-card-text>
            </v-card>
            <div v-else-if="stateCus[0]?.text != undefined">
                {{ stateCus[0]?.text }}
            </div>
            <el-button v-else :type="(stateCus[0].button?.style as any)" :disabled="(stateCus[0].button?.disabled)"
                @click="emitButton(stateCus[0].button?.key)">{{
                    stateCus[0]?.button?.btn
                }}</el-button>
        </div>
    </div>
    <el-dialog v-model="centerDialogVisible" :title="`发送交互请求${ButtonKeyView}?`" width="80%" align-center>
        <template #footer>
            <span class="dialog-footer">
                <el-button @click="centerDialogVisible = false">取消</el-button>
                <el-button type="primary" @click="isemitButton">
                    发送
                </el-button>
            </span>
        </template>
    </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import Table from './Table/index.vue'
import btnEvent from '../../hooks/btnEvent'
import { chartData } from '../../store/store'

export type Button = {
    btn: string
    key: string
    style?: string
    disabled?: boolean
}
export type Data = {
    title?: string,
    tables?: {
        cols?: Array<string>
        rows?: Array<Array<number | string | Button>>
        text?: string
    },
    text?: string,
    button?: Button
}

const cData = chartData()
const centerDialogVisible = ref<boolean>(false)
const ButtonKeyView = ref<string>('')

//发送按钮
const emitButton = (key: any) => {
    ButtonKeyView.value = key
    centerDialogVisible.value = true
}

//确认发送
const isemitButton = () => {
    btnEvent(ButtonKeyView.value)
    centerDialogVisible.value = false
}

//是否存在tables
const isTables = (stateCus: Array<Data>) => {
    for (let i in stateCus) {
        if (stateCus[i]?.tables?.cols != undefined) {
            return true
        }
    }
    return false
}

//初始化Tab键
const initTab = (data: Array<Array<Data>>) => {
    let Cus: Array<number> = []
    for (let _ in data) {
        Cus.push(0)
    }
    return Cus
}

//自定义tab value管理
const tab = reactive(initTab(cData.stateCustom))

</script>

<style scoped lang="less">
#stateCustom {
    div {
        margin-bottom: 5px;

        .v-card {
            .v-card-text {
                padding: 5px;
            }
        }
    }
}
</style>