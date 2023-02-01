<template>
    <!-- 自定义图表 -->
    <div v-for="(_, index) in cData.chartCustom" :id="'ChartCustom-' + index" style="width: 100%;height: 300px;">
    </div>
</template>
  
<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import * as echarts from 'echarts'
import { chartData } from '../../store/store'

//用户配置
export type PieChart = {
    value: number
    name: string
}

export type ChartCus = {
    type: string
    key: string
    title: string
    color?: string
    data: Array<PieChart | Array<number>>
}

const cData = chartData()

//饼图配置
const pieChartConfig = (data: ChartCus) => {
    return {
        title: {
            text: data.title,
            left: 'left'
        },
        tooltip: {
            trigger: 'item'
        },
        toolbox: {
            feature: {
                saveAsImage: {
                    title: "导出图片"
                }
            }
        },
        series: [
            {
                type: 'pie',
                radius: '50%',
                data: data.data,
                emphasis: {
                    itemStyle: {
                        shadowBlur: 10,
                        shadowOffsetX: 0,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }
        ]
    }
}

//折线图配置
const lineChartConfig = (data: ChartCus) => {
    return {
        title: {
            text: data.title
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                animation: false
            }
        },
        xAxis: {
            type: 'time',
            boundaryGap: false,
            splitLine: {
                show: false
            },
        },
        yAxis: {
            type: 'value',
            boundaryGap: [0, '100%'],
            max: (value: any) => {
                return value.max * 1.3
            },
            splitLine: {
                show: false
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
        toolbox: {
            feature: {
                saveAsImage: {
                    title: "导出图片"
                }
            }
        },
        series: [
            {
                type: 'line',
                color: data?.color,
                showSymbol: false,
                data: data.data,
            }
        ]
    }
}

//初始化eChart
const initeChart = (dom: string, setOption: any) => {
    const chartsCus = echarts.init(document.querySelector('#' + dom) as HTMLElement)
    chartsCus.setOption(setOption)
    return chartsCus
}
//初始化自定义图表
const initeChartCustom = (dom: string, data: ChartCus) => {
    if (data.type == "pie") {
        return initeChart(dom, pieChartConfig(data))
    }
    else if (data.type == "line") {
        return initeChart(dom, lineChartConfig(data))
    }
}

onMounted(() => {
    let chartCus = reactive<Array<echarts.ECharts | undefined>>([])
    cData.chartCustom.forEach((value: ChartCus, index: number) => {
        chartCus.push(initeChartCustom("ChartCustom-" + index, value))
    })
    console.log(cData.chartCustom)
    //更新图表
    watch(cData.chartCustom, () => {
        chartCus.forEach((el: any, index: number) => {
            el?.setOption({
                series: [
                    {
                        data: cData.chartCustom[index].data
                    }
                ]
            })
        })
    }, {
        immediate: false,
        deep: true,
    })
})

</script>
  
<style scoped lang="less">

</style>