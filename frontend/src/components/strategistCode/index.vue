<template>
    <v-app-bar class="bar" :elevation="1">
        <el-breadcrumb :separator-icon="ArrowRight">
            <el-breadcrumb-item :to="{ path: '/' }">仓库</el-breadcrumb-item>
            <el-breadcrumb-item>{{ ProjectName }}</el-breadcrumb-item>
        </el-breadcrumb>
    </v-app-bar>
    <div style="padding: 0 20px;">
        <div class="sheader">
            <div class="sheader-left">
                <el-button @click="dialogUpload = true" :icon="Open">上传</el-button>
                <el-button @click="dialogNewProject = true" :icon="DocumentAdd">新建</el-button>
            </div>
        </div>
        <v-divider></v-divider>
        <el-table ref="multipleTableRef" :data="tableData" :table-layout="'fixed'" style="width: 100%;cursor:default;">
            <el-table-column label="名称">
                <template #default="scope">
                    <el-link :icon="chanceIcon(scope.row.name)" @click="OpenObject(scope.$index)">{{ scope.row.name }}</el-link>
                </template>
            </el-table-column>
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
                                    @click="handleDelete([scope.row])">删除</el-dropdown-item>
                                <el-dropdown-item :icon="EditPen" @click="rename(scope.row)">重命名</el-dropdown-item>
                                <el-dropdown-item :icon="Download" @click="download(scope.row)">下载</el-dropdown-item>
                            </el-dropdown-menu>
                        </template>
                    </el-dropdown>
                </template>
            </el-table-column>
        </el-table>
    </div>
    <!-- 上传 -->
    <el-dialog v-model="dialogUpload" title="上传">
        <el-form :model="Data_Upload" style="padding: 0 20px;">
            <el-upload ref="uploadRef" class="upload-demo" drag :auto-upload="false"
                :action="`${url.ip}${url.uploadFile}?id=${ProjectId}`" multiple>
                <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                <div class="el-upload__text">
                    Drop file here or <em>click to upload</em>
                </div>
            </el-upload>
        </el-form>
        <template #footer>
            <span class="dialog-footer">
                <el-button @click="dialogUpload = false">取消</el-button>
                <el-button type="primary" @click="uplodeFiles">
                    上传
                </el-button>
            </span>
        </template>
    </el-dialog>
    <!-- 新建 -->
    <el-dialog v-model="dialogNewProject" title="新建">
        <el-form :model="Data_NewProject">
            <el-form-item label="文件名称" :label-width="'100px'">
                <el-input v-model="Data_NewProject.name" autocomplete="off" />
            </el-form-item>
        </el-form>
        <template #footer>
            <span class="dialog-footer">
                <el-button @click="dialogNewProject = false">取消</el-button>
                <el-button type="primary" @click="NewProject">
                    确定
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
    <!-- 删除 -->
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
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElTable, UploadInstance, ElMessage } from 'element-plus'
import {
    Memo,
    DataLine,
    Document,
    Setting,
    ArrowDown,
    ArrowRight,
    Open,
    Delete,
    EditPen,
    Download,
    DocumentAdd,
} from '@element-plus/icons-vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { useRouter, useRoute } from 'vue-router'
import { Data, Url } from '../../Store/store'
import axios from 'axios'

const datas = Data()
const url = Url()

const router = useRouter()
const route = useRoute()

interface ProjectData {
    name: string
    path: string
}

const ProjectId = route.path.split('/').pop()
console.log(ProjectId)

let ProjectName = ref<string>('')
for (let i in datas.data.projects) {
    if (ProjectId == datas.data.projects[i].id) {
        ProjectName.value = datas.data.projects[i].name
        break
    }
}

let tableData: ProjectData[] = []

for (let i in datas.data.projects) {
    if (datas.data.projects[i].id == ProjectId) {
        tableData = datas.data.projects[i].files
    }
}

// 打开文件
const OpenObject = (index: number) => {
    console.log(route)
    router.push(`/code?path=${tableData[index].path}`)
}

// 删除
const dialogVisible = ref<boolean>(false)
const dialogText = ref<string>('')
let dialogDel = reactive<ProjectData[]>([])

const handleDelete = (indexs: ProjectData[]) => {
    let sumName = []
    for (let i in indexs) {
        sumName.push(indexs[i].name)
        dialogDel.push(indexs[i])
    }
    dialogText.value = `${sumName}`
    dialogVisible.value = true
}

const dialogTrue = (values: ProjectData[]) => {
    axios.get(`${url.ip}${url.delete}?id=${ProjectId}&file=${values[0].name}`)
        .then((res) => {
            ElMessage({
                message: '删除成功',
                type: 'success',
            })
            location.reload()
        })
        .catch((error) => {
            ElMessage.error('删除失败')
        })
}

//重命名
const rename = (value: ProjectData) => {
    console.log(value)
    Data_ReName.name = value.name
    dialogReName.value = true
    ReNameData = value
}
const dialogReName = ref<boolean>(false)
let ReNameData = reactive<ProjectData | any>({})
const Data_ReName = reactive({
    name: '',
})

const renameUpload = () => {
    if (Data_ReName.name != '') {
        axios.get(`${url.ip}${url.rename}?id=${ProjectId}&file=${ReNameData.name}&change=${Data_ReName.name}`)
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

// 新建
const dialogNewProject = ref(false)
const Data_NewProject = reactive({
    name: '',
})

const NewProject = () => {
    if (Data_NewProject.name != '') {
        axios.get(`${url.ip}${url.newfile}?id=${ProjectId}&name=${Data_NewProject.name}`)
            .then((res) => {
                ElMessage({
                    message: '新建成功',
                    type: 'success',
                })
                location.reload()
            })
            .catch((error) => {
                ElMessage.error('新建失败')
            })
    }
}

const dialogUpload = ref(false)
const Data_Upload = reactive({
    name: '',
})

const uploadRef = ref<UploadInstance>()
const uplodeFiles = () => {
    uploadRef.value!.submit()
}

const download = (values: ProjectData) => {
    axios({
        url: `${url.ip}${url.download}?id=${ProjectId}&file=${values.name}`,
        method: 'GET',
        responseType: 'blob',
    }).then(response => {
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', values.name)
        document.body.appendChild(link)
        link.click()
    })

}

const chanceIcon = (name: string)=> {
    if (name == 'main.py') {
        return Memo
    } else if (name == 'config.py') {
        return Setting
    } else if (name == 'chart.py') {
        return DataLine
    } else {
        return Document
    }
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
</style>