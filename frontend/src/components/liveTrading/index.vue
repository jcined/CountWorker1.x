<template>
    <v-app-bar class="bar" :elevation="1">
        <el-breadcrumb :separator-icon="ArrowRight">
            <el-breadcrumb-item :to="{ path: '/' }">实盘</el-breadcrumb-item>
        </el-breadcrumb>
    </v-app-bar>
    <div style="padding: 0 20px;">
        <div class="sheader">
            <div class="sheader-left">
                <el-button @click="dialogNewLive = true" :icon="Plus">创建实盘</el-button>
            </div>
        </div>
        <v-divider></v-divider>
        <el-table ref="multipleTableRef" :data="tableData" :table-layout="'fixed'" style="width: 100%;cursor:default;">
            <el-table-column label="名称">
                <template #default="scope">
                    <el-link @click="OpenObject(scope.row)">{{ scope.row.name }}</el-link>
                </template>
            </el-table-column>
            <el-table-column label="项目">
                <template #default="scope">
                    <el-link style="font-style:italic;" type="info" @click="OpenProject(scope.row)">{{
                        scope.row.projectId.name
                    }}</el-link>
                </template>
            </el-table-column>
            <el-table-column label="状态">
                <template #default="scope">
                    <v-icon :icon="scope.row.state ? icon.true.icon : icon.false.icon"
                        :color="scope.row.state ? icon.true.color : icon.false.color" size="20" />
                </template>
            </el-table-column>
            <el-table-column prop="time" label="创建时间" />
            <el-table-column label="操作项" width="110">
                <template #default="scope">
                    <el-dropdown trigger="click">
                        <el-button>
                            操作
                            <el-icon class="el-icon--right"><arrow-down /></el-icon>
                        </el-button>
                        <template #dropdown>
                            <el-dropdown-menu>
                                <el-dropdown-item :icon="Open" @click="OpenObject(scope.row)">打开</el-dropdown-item>
                                <el-dropdown-item :icon="Delete" @click="handleDelete(scope.row)">删除</el-dropdown-item>
                            </el-dropdown-menu>
                        </template>
                    </el-dropdown>
                </template>
            </el-table-column>
        </el-table>
    </div>
    <!-- 创建实盘 -->
    <el-dialog v-model="dialogNewLive" title="创建实盘">
        <el-form :model="Data_NewLive">
            <div style="padding:0 30px">
                <el-form-item label="策略名称">
                    <el-input v-model="Data_NewLive.name" autocomplete="off" />
                </el-form-item>
                <el-form-item label="选择策略">
                    <el-select v-model="Data_NewLive.project" class="m-2" placeholder="Select">
                        <el-option v-for="item in options" :key="item.value" :label="item.label" :value="item.value" />
                    </el-select>
                </el-form-item>
            </div>
        </el-form>
        <template #footer>
            <span class="dialog-footer">
                <el-button @click="dialogNewLive = false">取消</el-button>
                <el-button type="primary" @click="NewLive">
                    创建
                </el-button>
            </span>
        </template>
    </el-dialog>
    <el-dialog v-model="dialogVisible" title="确定提示" width="30%">
        <span>
            确定要删除实盘 <span style="font-weight: 700">{{ dialogText }}</span> 吗?
        </span>
        <template #footer>
            <span class="dialog-footer">
                <el-button @click="dialogVisible = false">取消</el-button>
                <el-button type="primary" @click="dialogTrue(dialogDel)">
                    确定
                </el-button>
            </span>
        </template>
    </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElTable, ElMessage } from 'element-plus'
import {
    ArrowDown,
    Open,
    Delete,
    ArrowRight,
    Plus,
} from '@element-plus/icons-vue'
import { Data, Url } from '../../Store/store'
import axios from 'axios'
import { useRouter } from 'vue-router'

interface liveData {
    name: string
    time: string
    state: boolean
    projectId: {
        name: string
        id: string
    }
    id: string
}

const router = useRouter()

const data = Data()
const url = Url()

const multipleTableRef = ref<InstanceType<typeof ElTable>>()

const tableData: liveData[] = data.data.lives

const OpenObject = (values: liveData) => {
    window.open(`/live/chart/${values.id}`)
}

const options: any = []
for (let i in data.data.projects) {
    options.push({
        value: data.data.projects[i].id,
        label: data.data.projects[i].name,
    })
}

type IconType = {
    true: Icon,
    false: Icon,
}
type Icon = {
    icon: string,
    color: string,
}
const icon = reactive<IconType>({
    true: {
        icon: "mdi-play",
        color: "#5CB85C",
    },
    false: {
        icon: "mdi-stop",
        color: "#777777",
    },
})

const dialogNewLive = ref<boolean>(false)
const Data_NewLive = reactive({
    name: '',
    project: options[0]?.value == undefined ? options[0]?.value : '',
})
const NewLive = () => {
    if (Data_NewLive.name != '') {
        let id = null
        for (let i in options) {
            console.log(options);
            console.log(Data_NewLive.project);
            if (options[i].value == Data_NewLive.project) {
                id = options[i].value
            }
        }
        axios.get(`${url.ip}${url.newlive}?id=${id}&name=${Data_NewLive.name}`)
            .then((res) => {
                ElMessage({
                    message: '创建成功',
                    type: 'success',
                })
                location.reload()
            })
            .catch(() => {
                ElMessage.error('创建失败')
            })
    }
}

const dialogVisible = ref<boolean>(false)
const dialogText = ref<string>('')
let dialogDel = ref<liveData | any>()

// 删除项目
const handleDelete = (indexs: liveData) => {
    dialogDel.value = indexs
    dialogText.value = `${indexs.name}`
    dialogVisible.value = true
}

const dialogTrue = (values: liveData) => {
    axios.get(`http://127.0.0.1:10010/api/delive?id=${values.id}`)
        .then((res) => {
            if (res.data.code == "10015") {
                ElMessage.error('实盘正在运行')
            } else {
                ElMessage({
                    message: '删除成功',
                    type: 'success',
                })
                location.reload()
            }
        })
        .catch((error) => {
            console.log(error)
            ElMessage.error('删除失败')
        })
}

// 打开项目
const OpenProject = (value: liveData) => {
    router.push(`/s/code/${value.projectId.id}`)
}

</script>

<style scoped lang="less">
.bar {
    padding: 0 15px;
}

.sheader {
    padding: 10px 0;
    display: flex;
    justify-content: space-between;
}

.icon {
    font-size: 20px;
    display: flex;
    justify-content: center;
}
</style>
