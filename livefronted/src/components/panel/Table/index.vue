<template>
    <!-- 创建Table组件 -->
    <v-table density="compact" scrollable>
        <thead>
            <tr>
                <th class="text-left" nowrap="nowrap" v-for="(i, key) in data?.cols" :key="key">{{ i }}</th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="item in data?.rows">
                <td nowrap="nowrap" v-for="(i, key) in item" :key="key">
                    <div v-if="i?.btn == undefined">
                        {{ i }}
                    </div>
                    <div v-else class="button">
                        <el-button :type="i?.style" :disabled="i?.disabled" @click="btnEvent(i?.key)">{{ i?.btn
                            }}</el-button>
                    </div>

                </td>
            </tr>
        </tbody>
    </v-table>
</template>

<script setup lang="ts">
import btnEvent from '../../../hooks/btnEvent'
type Data = {
    cols?: Array<string>
    rows?: Array<Array<any>>
    text?: string
}
defineProps<{
    data?: Data
}>()

</script>

<style scoped lang="less">
.v-table {
    max-height: 300px;
    overflow-y: auto;

    .button {
        padding: 8% 0;
        box-sizing: border-box;
    }
}
</style>