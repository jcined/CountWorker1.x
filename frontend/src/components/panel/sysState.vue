<template>
    <!-- 系统状态 -->
    <div id="sysState">
        <v-divider></v-divider>
        <Table :data="desserts"></Table>
        <v-divider></v-divider>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import Table from './Table/index.vue'
import { strategyData, chartData } from '../../store/store'

const ctData = chartData()

const desserts = reactive({
    cols: ["初始时间", "运行时间", "初始金额", "当前金额", "总收益"],
    rows: [
        [ctData.sysData.startTime, ctData.sysData.runTime, ctData.sysData.startAmount, ctData.sysData.nowAmount, ctData.sysData.totolProfit]
    ]
})

</script>

<style scoped lang="less">
#sysState {
    margin: 10px 0;
}
</style>