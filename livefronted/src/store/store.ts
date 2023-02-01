import { defineStore } from 'pinia'
import { Names } from './index'
import { ChartCus } from '../components/panel/ChartCustom.vue'
import { Data } from '../components/panel/stateCustom.vue'
import { Logs } from '../components/log/Logmain.vue'
import { CusConfig } from '../components/setting/strategyConfig.vue'

//策略配置
export const strategyData = defineStore(Names.strategyData, {
    state: () => {
        return <{
            exchanges: Array<{ name: string }>,
            config: Array<any>,
        }>{
            exchanges: [] as any,
            config: [],
        }
    },
    actions: {
        setExchanges(data: Array<Array<string>>) {
            let sData: any = []
            data.forEach((el) => {
                sData.push({
                    name: el.join(" / ")
                })
            })
            this.exchanges = sData
        },
    }
})

export type SYSData = {
    switch: boolean
    startTime: string
    runTime: string
    startAmount: number
    nowAmount: number
    totolProfit: number
}
//图表信息
export const chartData = defineStore(Names.chartData, {
    state: () => {
        return <{
            profitData: Array<Array<number>>,   //收益信息
            sysData: SYSData,   //策略基本信息
            chartCustom: Array<ChartCus>,   //自定义图表
            stateCustom: Array<Array<Data>>     //自定义状态
        }>{
            profitData: [] as any,
            sysData: {
                switch: false,
                startTime: '',
                runTime: '',
                startAmount: 0,
                nowAmount: 0,
                totolProfit: 0
            },
            chartCustom: [],
            stateCustom: [],
        }
    },
    actions: {

    }
})

//策略运行状态 | 测试加载状态 | 日志信息 | 未查看日志数量 | Tab记录 | 日志是否全部加载 | 是否初始化
//日志查看页数 | 初始化日志时间
export const state = defineStore(Names.state, {
    state: () => {
        return <{
            Name: string
            AltExchanges: Array<string>,
            state: boolean,
            isLoding: boolean,
            Logs: Array<Logs>,
            toBeVlog: number,
            isLogsAll: boolean,
            isInit: boolean,
            logspage: number,
            before_time: number | null,
        }>{
            AltExchanges: ["binance","okx"],
            isInit: false,
            Name: '',
            state: false,
            Logs: [] as any,
            toBeVlog: 0,
            logspage: 1,
            before_time: null,
        }
    },
    actions: {
        addLog(log: Logs) {
            this.Logs.splice(0, 0, log)
        },
        addLogs(logs: Array<Logs>) {
            this.Logs.push(...logs)
        },
    }
})

//策略配置  上传格式
export type upConFig = {
    Name: string,
    Exchanges: Array<Array<string>>,
    CusConfig: Array<CusConfig>,
    Files: {
        main: any,
        config: any,
        chart: any,
        other?: any,
        exchanges?: any,
    }
}
//策略配置
export const upConfig = defineStore(Names.upConfig, {
    state: () => {
        return <upConFig>{
            Files: {
                main: null,
                config: null,
                chart: null,
                other: [],
                exchanges: [],
            }
        }
    },
})