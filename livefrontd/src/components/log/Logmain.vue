<template>
    <div v-if="State.Logs.length == 0" style="position: absolute;top: 50%;left: 50%;transform: translate(-50%, -50%);">
        <el-empty description="还没有日志" />
    </div>
    <div v-else id="log-Log">
        <transition-group
            :enter-active-class="isLoding ? undefined : 'animate__animated animate__fadeInLeft animate__faster'">
            <div class="Log-info" v-for="item in State.Logs" :key="item.time">
                <div class="info-header">
                    <div class="ih-time">{{ toFormat(item.time) }}</div>
                    <el-button v-if="item.type == 'buy'" type="primary" plain>买入</el-button>
                    <el-button v-else-if="item.type == 'sell'" type="success" plain>卖出</el-button>
                    <el-button v-else-if="item.type == 'info'" type="warning" plain>信息</el-button>
                    <el-button v-else-if="item.type == 'profit'" type="danger" plain>收益</el-button>
                    <el-button v-else-if="item.type == 'cancel'" type="info" plain>撤销</el-button>
                    <el-button v-else-if="item.type == 'error'" type="info">错误</el-button>
                    <el-button v-else-if="item.type == 'start'" type="warning">启动</el-button>
                </div>
                <div v-if="item.type != 'start'" class="info-body">
                    <div class="ib-data">{{ item.info }}</div>
                </div>
                <v-divider v-else style="margin-top: 10px;"></v-divider>
            </div>
        </transition-group>
        <div class="log-Loding" v-show="isLoding">
            <v-progress-circular v-if="!State.isLogsAll" indeterminate color="primary" :width="5"
                :size="24"></v-progress-circular>
            <div v-else>加载完成</div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { state } from '../../store/store'
import { useRoute } from 'vue-router'
import axios from 'axios'

export type Logs = {
    time: number,
    type: string,
    info: string
}

const ProjectId = window.location.href.split('/').pop()

const route = useRoute()
const State = state()

//Logs加载更多
const isLoding = ref<boolean>(false)

const toFormat = (timestamp: number) => {
    const date = new Date(timestamp)
    return date.toISOString().slice(0, 10) + " " + date.toTimeString().slice(0, 8)
}

//当滚动到底部
const rollPage = () => {
    if (route.name == "logs") {
        const scrollY =
            window.pageYOffset !== undefined
                ? window.pageYOffset
                : document.documentElement.scrollTop

        const innerHeight =
            window.innerHeight !== undefined
                ? window.innerHeight
                : document.documentElement.clientHeight

        const bodyHeight =
            document.body.offsetHeight !== undefined
                ? document.body.offsetHeight
                : document.body.scrollHeight
        // 判断是否滑到底部
        if (scrollY + innerHeight + 10 >= bodyHeight) {
            if (!State.isLogsAll) {
                let page = State.logspage
                page += 1
                console.log(page)
                axios.get(`/api/get-logs?id=${ProjectId}`, {
                    params: {
                        page: page,
                        before_time: State.before_time,
                    }
                })
                    .then((response) => {
                        isLoding.value = true
                        if (response.data.data.length > 0) {
                            State.logspage++
                            console.log("response", response.data)
                            State.addLogs(response.data.data)
                        } else {
                            State.isLogsAll = true
                        }
                    })
            } else {
                window.removeEventListener("scroll", rollPage)
            }
        } else {
            isLoding.value = false
        }
    }
}

onMounted(() => {
    window.addEventListener("scroll", rollPage)
})
</script>

<style scoped lang="less">
#log-Log {
    width: 100%;

    .Log-info {
        margin-bottom: 10px;

        .info-header {
            display: flex;
            align-items: center;

            .ih-time {
                font-size: 16px;
                font-weight: 700;
                margin-right: 5px;
            }

            .el-button {
                padding: 0 8px;
                height: 26px;
            }
        }

        .info-body {
            padding-left: 30px;
            box-sizing: border-box;

            .ib-data {
                padding: 5px 0;
                font-size: 18px;
                border-left: 1px #ccc solid;
                padding-left: 10px;
                word-wrap: break-word;
            }
        }
    }

    .log-Loding {
        color: #ccc;
        width: 100%;
        display: flex;
        justify-content: center;
    }
}
</style>