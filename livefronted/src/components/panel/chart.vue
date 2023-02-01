<template>
    <div id="chart"></div>
</template>

<script setup lang="ts">
import { reactive, onMounted, toRefs, watch } from 'vue'
import * as echarts from 'echarts'
import { chartData } from '../../store/store'

const cData = chartData()
const data = cData.profitData

onMounted(() => {
    const charts = echarts.init(document.querySelector('#chart') as HTMLElement)
    charts.setOption({
        tooltip: {
            trigger: 'axis',
            position: (pt: any) => {
                return [pt[0], '10%']
            }
        },
        title: {
            left: 'left',
            text: '收益曲线'
        },
        toolbox: {
            feature: {
                saveAsImage: {
                    title: "导出图片"
                }
            }
        },
        xAxis: {
            type: 'time',
            boundaryGap: false
        },
        yAxis: {
            type: 'value',
            boundaryGap: [0, '100%'],
            max: (value: any) => {
                return value.max * 1.2
            },
        },
        dataZoom: [
            {
                type: 'inside',
                start: 0,
                end: 100,
            },
            {
                start: 0,
                end: 20
            }
        ],
        series: [
            {
                name: '总收益',
                type: 'line',
                smooth: true,
                symbol: 'none',
                areaStyle: {},
                data: data
            }
        ]
    })

    watch(data, () => {
        charts.setOption({
            series: [
                {
                    data: data
                }
            ]
        })
    }, {
        immediate: false,
        deep: true,
    })
})
</script>

<style scoped lang="less">
#chart {
    width: 100%;
    height: 300px;
}
</style>