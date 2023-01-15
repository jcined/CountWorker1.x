<template>
    <v-list lines="three">
        <v-list-subheader>系统</v-list-subheader>
        <div class="sys">
            <div class="setting-config" style="margin-bottom: 10px;font-size: 14px;color: #ccc;">版本号: v1.1</div>
        </div>
        <v-divider></v-divider>
        <v-list-subheader>文件</v-list-subheader>
        <div class="setting-file">
            <v-file-input :rules="rules('main.py')" label="main.py *" variant="filled"
                prepend-icon="mdi-file-code"></v-file-input>
            <v-file-input :rules="rules('config.py')" label="config.py *" variant="filled"
                prepend-icon="mdi-cog-box"></v-file-input>
            <v-file-input :rules="rules('chart.py')" label="chart.py" variant="filled"
                prepend-icon="mdi-chart-areaspline"></v-file-input>
            <v-file-input multiple :rules="rules('o')" label="other Python files" variant="filled"
                prepend-icon="mdi-file-plus"></v-file-input>
            <v-file-input multiple label="Exchange package" variant="filled" :rules="rules('e')"
                prepend-icon="mdi-puzzle"></v-file-input>
        </div>
        <v-divider></v-divider>
        <v-list-subheader>配置</v-list-subheader>
        <div class="setting-config">
        </div>
    </v-list>
</template>

<script setup lang="ts">
import { upConfig } from '../../store/store'
const upconfig = upConfig()

const readPython = (value: any, func: Function) => {
    const reader = new FileReader()
    reader.readAsDataURL(value)
    reader.addEventListener('load', (e) => {
        func(e)
    })
}

const rules = (name: string) => {
    return [
        (value: any) => {
            if (name == 'o' || name == 'e') {                             
                let r = true
                for (let i in value) {
                    if (!value[i].name.includes(".py")) {
                        r = false
                        break
                    }
                }
                if (r) {
                    for (let i in value) {
                        readPython(value[i], (e: ProgressEvent<FileReader>) => {
                            let result = e.target?.result
                            console.log(result)
                            const transmit = {
                                "fileName": value[i].name,
                                "data": result,
                            }
                            if (name == 'o') {
                                upconfig.Files.other.push(transmit)
                            } else {
                                upconfig.Files.exchanges.push(transmit)
                            }
                        })
                    }
                }
                return !value || r || `文件须为python类型`
            }
            let ispy = (value[0].name == name)
            if (ispy) {                
                readPython(value[0], (e: ProgressEvent<FileReader>) => {
                    let result = e.target?.result
                    console.log(result)
                    if (name == "main.py") {
                        upconfig.Files.main = result
                    } else if (name == "config.py") {
                        upconfig.Files.config = result
                    } else if (name == "chart.py") {
                        upconfig.Files.chart = result
                    }
                })
            }
            return !value || ispy || `文件名须为'${name}''`
        }
    ]
}

</script>

<style scoped lang="less">
.setting-file,
.setting-config {
    padding: 0 15px;
}
</style>