<template>
    <Bar></Bar>
    <div v-if="sData.exchanges.length == 0" style="display: flex;justify-content: center;align-items: center;height: 100vh;">
        <el-empty description="还没有策略" />
    </div>
    <div v-else id="panel">
        <exchanges></exchanges>
        <div class="Chart">
            <chart></chart>
        </div>
        <sysState v-if="ctData.sysData.switch"></sysState>
        <chartCustom></chartCustom>
        <stateCustom></stateCustom>
    </div>
</template>

<script setup lang="ts">
import chart from './chart.vue'
import exchanges from './exchanges.vue'
import sysState from './sysState.vue'
import chartCustom from './ChartCustom.vue'
import stateCustom from './stateCustom.vue'
import Bar from '../appBars.vue'
import { chartData, strategyData } from '../../store/store'
import Sinit from '../../hooks/Sinit'

Sinit()

const ctData = chartData()
const sData = strategyData()
</script>

<style scoped lang="less">
#panel {
    width: 100%;
    margin: 64px 0;

    @media screen and (min-width: 800px) {
        padding: 10px 25%;
    }

    @media screen and (max-width: 500px) {
        padding: 10px;
    }

    .Chart {
        margin-top: 10px;
        box-sizing: border-box;
    }
}
</style>