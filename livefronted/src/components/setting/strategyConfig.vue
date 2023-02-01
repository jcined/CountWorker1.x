<template>
    <v-list lines="two" subheader>
        <v-list-subheader>基础</v-list-subheader>
        <div class="default-config">
            <v-responsive class="mx-auto">
                <v-text-field v-model="upconfig.Name" clearable hide-details="auto" label="策略名称"
                    variant="underlined"></v-text-field>
            </v-responsive>
            <div class="sConfig-exchange">
                <v-responsive class="mx-auto">
                    <v-text-field v-model="strategyConfig.nowExhangesData.exchange" clearable hide-details="auto"
                        label="交易所" variant="underlined"></v-text-field>
                </v-responsive>
                <v-responsive class="mx-auto">
                    <v-text-field v-model="strategyConfig.nowExhangesData.chip" clearable hide-details="auto"
                        label="交易对" variant="underlined"></v-text-field>
                </v-responsive>
                <v-btn
                    @click="addExchange(strategyConfig.nowExhangesData.exchange, strategyConfig.nowExhangesData.chip)"
                    icon="mdi-plus-thick" color="primary" size="42" />
            </div>
            <div class="Exchanges">
                <v-chip v-for="(name, index) in upconfig.Exchanges" @click="closeChip(index)" variant="elevated"
                    class="Exchanges-chips">
                    {{ name.join(' / ') }}
                </v-chip>
            </div>
        </div>
        <v-divider></v-divider>
        <v-list-subheader>高级</v-list-subheader>
        <div class="senior-config">
            <div :key="index" v-for="(i, index) in upconfig.CusConfig" style="margin-bottom: 10px;">
                <v-responsive v-if="i.type == 'number'" class="mx-auto">
                    <v-text-field v-model="i.default" clearable hide-details="auto" :label="i.name" :hint="i.remarks"
                        placeholder="number类型" variant="underlined"></v-text-field>
                </v-responsive>
                <v-responsive v-else-if="i.type == 'string'" class="mx-auto">
                    <v-text-field v-model="i.default" clearable hide-details="auto" :label="i.name" :hint="i.remarks"
                        placeholder="string类型" variant="underlined"></v-text-field>
                </v-responsive>
                <v-select v-else-if="i.type == 'select'" v-model="i.default" :label="i.name" :items="i.items"
                    variant="underlined" :hint="i.remarks"></v-select>
                <div v-else-if="i.type == 'switch'" class="senior-config-switch">
                    <div class="sencon-switch-name">
                        <div class="swn-name">{{ i.name }}</div>
                        <div class="swn-remarks">{{ i.remarks }}</div>
                    </div>
                    <v-switch color="primary" v-model="i.default" hide-details
                        style="display: flex;justify-content: right;"></v-switch>
                </div>
                <div v-else-if="i.type == 'slider'">
                    <div class="text-caption" style="color: #909090;">{{ i.name }}</div>
                    <v-slider color="primary" v-model="i.default" class="align-center" :max="i?.max" :min="i?.min"
                        :step="i?.step" :show-ticks="i?.step == undefined ? undefined : 'always'" hide-details>
                        <template v-slot:append>
                            <v-text-field v-model="i.default" hide-details single-line density="compact" type="number"
                                style="width: 70px"></v-text-field>
                        </template>
                    </v-slider>
                    <div class="text-caption" style="color: #ccc;">{{ i.remarks }}</div>
                </div>
            </div>
        </div>
        <v-divider></v-divider>
        <div class="setting-save">
            <v-btn @click="saveConfig" :disabled="false" :loading="loading" color="primary"
                style="width:280px;height: 46px;">
                更新
            </v-btn>
        </div>
    </v-list>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { upConfig, state } from '../../store/store'
import { ElMessage } from 'element-plus'
import axios from 'axios'

export type CusConfig = {
    var: string,
    name: string,
    type: string,
    remarks?: string,
    default?: any,
    min?: number,
    max?: number,
    step?: number,
    items?: Array<string>
}

const dialog = ref(false)
const upconfig = upConfig()
const State = state()

const ProjectId = window.location.href.split('/').pop()

type StrategyDefaultConfig = {
    nowExhangesData: {
        exchange: string | null,
        chip: string | null
    }
}
const strategyConfig = reactive<StrategyDefaultConfig>({
    nowExhangesData: {
        exchange: null,
        chip: null,
    }
})

//删除chips
const closeChip = (index: number) => {
    upconfig.Exchanges.splice(index, 1)
}

//添加交易对
const addExchange = (exchange: string | null, chip: string | null) => {
    if (exchange && chip) {
        //查重
        for (let el in upconfig.Exchanges) {
            if (upconfig.Exchanges[el][0] == exchange && upconfig.Exchanges[el][1] == chip) return
        }
        upconfig.Exchanges.push([exchange, chip])
        strategyConfig.nowExhangesData.exchange = null
        strategyConfig.nowExhangesData.chip = null
    }
}

const loading = ref(false)
const error = (message: string) => {
    ElMessage.error(message)
    loading.value = false
}
//保存参数
const saveConfig = () => {
    loading.value = true
    //校验数据
    if (State.state) {
        error("策略正在运行")
        return
    }
    let is = true
    upconfig.CusConfig.forEach((el) => {
        if (el.default?.toString() == "" || el.default == undefined || el.default == null) {
            is = false
        }
    })
    if (!is || upconfig.Name == '' ||
        upconfig.Name == undefined ||
        upconfig.Exchanges.length == 0) {
        error("请上传完整配置参数")
        return
    }
    axios.post('/api/update?id='+ProjectId, {
        Name: upconfig.Name,
        config: upconfig.CusConfig,
        exchanges: upconfig.Exchanges,
    })
        .then((response) => {
            console.log(response)
            loading.value = false
            ElMessage({
                message: '保存成功',
                type: 'success',
            })
        })
        .catch((error) => {
            console.log(error)
            loading.value = false
            ElMessage.error("保存失败")
        })
}

</script>

<style scoped lang="less">
.v-overlay {
    z-index: 2000 !important;
}
.v-list {
    margin-bottom: 40px;
}
.default-config {
    width: 100%;
    padding: 0 15px;
    .sConfig-exchange {
        display: flex;
        margin-top: 10px;
        width: 100%;
        margin-bottom: 10px;
    }
    .Exchanges {
        margin-bottom: 5px;
        max-height: 500px;
        .Exchanges-chips {
            margin-right: 5px;
            margin-bottom: 5px;
        }
    }
}
.senior-config {
    width: 100%;
    padding: 0 30px;
    .senior-config-switch {
        margin-top: -10px;
        width: 100%;
        display: flex;
        align-items: center;
        .sencon-switch-name {
            display: flex;
            flex-direction: column;
            .swn-name {
                font-size: 15px;
                color: #909090;
            }
            .swn-remarks {
                font-size: 10px;
                color: #ccc;
            }
        }
    }
}
.setting-save {
    width: 100%;
    display: flex;
    justify-content: center;
    margin-top: 20px;
}
</style>