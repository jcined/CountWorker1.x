import { io } from "socket.io-client"
import { chartData, state, strategyData, SYSData, upConfig } from '../store/store'
import { CusConfig } from '../components/setting/strategyConfig.vue'
import { ChartCus } from '../components/panel/ChartCustom.vue'
import { Data } from '../components/panel/stateCustom.vue'
import { Logs } from '../components/log/Logmain.vue'
import axios from 'axios'

const sData = strategyData()
const State = state()
const cData = chartData()
const upconfig = upConfig()

type InitStrategy = {
    Name: string
    config: Array<CusConfig>
    state: boolean
    exchanges: Array<Array<string>>
    profit: Array<Array<number>>
    sysData: SYSData
    chartCustom: Array<ChartCus>
    stateCustom: Array<Array<Data>>
    Logs: Array<Logs>
}
function initStrategy(data: InitStrategy) {
    //策略名称
    State.Name = data.Name
    upconfig.Name = data.Name
    //策略配置
    upconfig.CusConfig = data.config
    //策略状态
    State.state = data.state
    //交易池
    sData.setExchanges(data.exchanges)
    //初始化upconfig
    upconfig.Exchanges = data.exchanges
    //收益信息
    cData.profitData = data.profit
    //策略基本信息
    cData.sysData = data.sysData
    //自定义图表
    cData.chartCustom = data.chartCustom
    //自定义状态
    cData.stateCustom = data.stateCustom
    //日志
    State.Logs = data.Logs
    //日志是否全部加载
    State.isLogsAll = false
    //日志开始时间
    State.before_time = data.Logs[0]?.time
}

export default function Sinit() {
    if (State.isInit == false) {
        State.isInit = true
        //初始化
        axios.get('/api/init')
            .then((response) => {
                const data = response.data.data
                console.log(data)

                initStrategy(
                    {
                        Name: data.Name,
                        config: data.config,
                        state: data.state,
                        exchanges: data.exchanges,
                        profit: data.profit,
                        sysData: data.sysData,
                        chartCustom: data.chartCustom,
                        stateCustom: data.stateCustom,
                        Logs: data.Logs,
                    }
                )
            })
        //连接ws
        const socket = io(`ws://${document.location.hostname}:10010/api`, { transports: ['websocket'] })
        //日志
        socket.on("log", (socket: any) => {
            console.log(socket.data)
            State.Logs.unshift(socket.data)
        })
        //状态
        socket.on("state", (socket: any) => {
            console.log(socket.data.state)
            cData.stateCustom = socket.data.state
        })
        //图表
        socket.on("chart", (socket: any) => {
            console.log(socket.data)
            const value = socket.data.index
            const index = cData.chartCustom.findIndex(x => x["key"] === value)
            if (socket.data.type == "line") {
                console.log(cData.chartCustom[index].data)
                cData.chartCustom[index].data.push(socket.data.data)
            } else if (socket.data.type == "pie") {
                cData.chartCustom[index].data = socket.data.data
            }
        })
        //收益
        socket.on("profit", (socket: any) => {
            console.log(socket.data)
            cData.profitData.push([socket.data.time,socket.data.value])
        })
        //错误
        socket.on("error", (socket: any) => {
            State.state = false
        })
        //ping
        socket.on('ping', () => {
            console.log('Received ping')
            socket.emit('pong')
        })
        //重新连接
        socket.on("reconnect", () => {
            console.log("Reconnected to the server!")
        })
        socket.on("reconnect_error", () => {
            console.log("Failed to reconnect to the server!")
        })
        window.onbeforeunload = () => {
            console.log("Closing WebSocket connection...")
            socket.close()
        }
    }
}