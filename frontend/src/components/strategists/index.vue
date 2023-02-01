<template>
    <v-app-bar class="bar" :elevation="1">
        <el-breadcrumb :separator-icon="ArrowRight">
            <el-breadcrumb-item :to="{ path: '/' }">仓库</el-breadcrumb-item>
        </el-breadcrumb>
    </v-app-bar>
    <div class="sheader">
        <div class="sheader-left">
            <el-button @click="dialogNewProject = true" :icon="DocumentAdd">新建</el-button>
        </div>
        <div class="sheader-right" v-show="multipleSelection.length">
            <el-button-group class="ml-4">
                <el-button @click="handleDelete(multipleSelection)" :icon="Delete" />
            </el-button-group>
        </div>
    </div>
    <div style="padding: 0 20px;">
        <v-divider></v-divider>
    </div>
    <div class="sapp">
        <el-table ref="multipleTableRef" :data="tableData" :table-layout="'fixed'" style="width: 100%;cursor:default;"
            @selection-change="handleSelectionChange">
            <el-table-column type="selection" width="55" />
            <el-table-column label="名称">
                <template #default="scope">
                    <el-link @click="OpenObject(scope.$index)">{{ scope.row.name }}</el-link>
                </template>
            </el-table-column>
            <el-table-column property="time" label="创建时间" />
            <el-table-column label="操作项" width="110">
                <template #default="scope">
                    <el-dropdown trigger="click">
                        <el-button>
                            操作
                            <el-icon class="el-icon--right"><arrow-down /></el-icon>
                        </el-button>
                        <template #dropdown>
                            <el-dropdown-menu>
                                <el-dropdown-item :icon="Open" @click="OpenObject(scope.$index)">打开</el-dropdown-item>
                                <el-dropdown-item :icon="Delete"
                                    @click="handleDelete([tableData[scope.$index]])">删除</el-dropdown-item>
                                <el-dropdown-item :icon="EditPen" @click="rename(scope.row)">重命名</el-dropdown-item>
                            </el-dropdown-menu>
                        </template>
                    </el-dropdown>
                </template>
            </el-table-column>
        </el-table>
    </div>
    <el-dialog v-model="dialogVisible" title="确定提示" width="30%">
        <span>
            确定要删除 <span style="font-weight: 700">{{ dialogText }}</span> 吗?
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
    <!-- 新建 -->
    <el-dialog v-model="dialogNewProject" title="新建">
        <el-form :model="Data_NewProject">
            <el-form-item label="策略名称" :label-width="'100px'">
                <el-input v-model="Data_NewProject.name" autocomplete="off" />
            </el-form-item>
        </el-form>
        <template #footer>
            <span class="dialog-footer">
                <el-button @click="dialogNewProject = false">取消</el-button>
                <el-button type="primary" @click="NewProject">
                    新建
                </el-button>
            </span>
        </template>
    </el-dialog>
    <!-- 重命名 -->
    <el-dialog v-model="dialogReName" :title="`重命名`">
        <el-form :model="Data_ReName">
            <el-form-item label="名称" :label-width="'100px'">
                <el-input v-model="Data_ReName.name" autocomplete="off" />
            </el-form-item>
        </el-form>
        <template #footer>
            <span class="dialog-footer">
                <el-button @click="dialogReName = false">取消</el-button>
                <el-button type="primary" @click="renameUpload">
                    修改
                </el-button>
            </span>
        </template>
    </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElTable, ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { Data, Url } from '../../Store/store'
import {
    ArrowDown,
    ArrowRight,
    Open,
    Delete,
    EditPen,
    DocumentAdd,
} from '@element-plus/icons-vue'
import axios from 'axios'

interface Projects {
    name: string
    time: string
    id: string
    files: {
        name: string
        path: string
    }[]
}

const data = Data()
const url = Url()

const router = useRouter()

const tableData: Projects[] = data.data.projects

// 打开项目
const OpenObject = (index: number) => {
    router.push(`/s/code/${tableData[index].id}`)
}

// 删除项目
const handleDelete = (indexs: Projects[]) => {
    let sumName = []
    for (let i in indexs) {
        sumName.push(indexs[i].name)
        dialogDel.push(indexs[i])
    }
    dialogText.value = `${sumName}`
    dialogVisible.value = true
}

const dialogTrue = (values: Projects[]) => {
    let list = []
    for (let i in values) {
        list.push(values[i].id)
    }
    axios.get(`${url.ip}${url.delete}?id=${list.join(",")}&file=null`)
        .then((res) => {
            console.log(res.data);

            if (res.data.code == "10016") {
                ElMessage.error('有实盘存在')
                dialogVisible.value = false
            } else {
                ElMessage({
                    message: '删除成功',
                    type: 'success',
                })
                location.reload()
            }
        })
        .catch((error) => {
            ElMessage.error('删除失败')
            dialogVisible.value = false
        })
}

const dialogReName = ref<boolean>(false)
let ReNameData = reactive<Projects | any>({})
const Data_ReName = reactive({
    name: '',
})
//重命名
const rename = (value: Projects) => {
    console.log(value)
    Data_ReName.name = value.name
    dialogReName.value = true
    ReNameData = value
}
const renameUpload = () => {
    if (Data_ReName.name != '') {
        axios.get(`${url.ip}${url.rename}?id=${ReNameData.id}&file=null&change=${Data_ReName.name}`)
            .then((res) => {
                ElMessage({
                    message: '重命名成功',
                    type: 'success',
                })
                location.reload()
            })
            .catch((error) => {
                ElMessage.error('重命名失败')
            })
    } else {

    }
}

const multipleTableRef = ref<InstanceType<typeof ElTable>>()
const multipleSelection = ref<Projects[]>([])
const handleSelectionChange = (val: Projects[]) => {
    multipleSelection.value = val
}

const dialogVisible = ref<boolean>(false)
const dialogText = ref<string>('')
let dialogDel = reactive<Projects[]>([])

const dialogNewProject = ref(false)
const Data_NewProject = reactive({
    name: '',
})

const NewProject = () => {
    if (Data_NewProject.name != '') {
        axios.get(`${url.ip}${url.newproject}?name=${Data_NewProject.name}`)
            .then((res) => {
                ElMessage({
                    message: '新建成功',
                    type: 'success',
                })
                location.reload()
            })
            .catch((errot) => {
                ElMessage.error('新建失败')
            })
    } else {

    }
}

</script>

<style scoped lang="less">
.bar {
    padding: 0 15px;
}

.sheader {
    padding: 10px 20px;
    display: flex;
    justify-content: space-between;
}

.sapp {
    padding: 0 20px;
}

.block-col-2 .demonstration {
    display: block;
    color: var(--el-text-color-secondary);
    font-size: 14px;
    margin-bottom: 20px;
}
</style>
