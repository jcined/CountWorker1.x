<template>
    <div id="Exchanges">
        <v-expansion-panels>
            <v-expansion-panel>
                <v-expansion-panel-title>
                    <v-progress-circular :size="20" :width="3" color="primary" indeterminate
                        v-if="State.isLoding"></v-progress-circular>
                    <v-icon v-else :icon="State.state ? icon.true.icon : icon.false.icon"
                        :color="State.state ? icon.true.color : icon.false.color" size="28" />
                    <div v-if="State.isLoding" class="exchanges-state">{{ State.state ? "正在停止..." : "正在启动..." }}</div>
                    <div v-else class="exchanges-state">{{ State.state ? "运行中" : "已停止" }}</div>
                </v-expansion-panel-title>
                <v-expansion-panel-text>
                    <div class="chips">
                        <v-chip variant="elevated" :key="index" v-for="(items, index) in sData.exchanges">{{ items.name }}</v-chip>
                    </div>
                </v-expansion-panel-text>
            </v-expansion-panel>
        </v-expansion-panels>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { state,strategyData } from '../../store/store'
const sData = strategyData()
const State = state()

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
</script>

<style scoped lang="less">
#Exchanges {
    width: 100%;

    .exchanges-state {
        padding: 10px 0;
        margin-left: 5px;
        font-size: 16px;
    }

    .chips {
        display: flex;
        flex-wrap: wrap;

        .v-chip {
            margin-bottom: 5px;
        }
    }
}
</style>