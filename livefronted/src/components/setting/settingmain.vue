<template>
    <v-list lines="three">
        <v-list-subheader>系统</v-list-subheader>
        <div class="sys">
            <div class="setting-config" style="margin-bottom: 10px;font-size: 14px;color: #ccc;">版本号: v1.2</div>
        </div>
        <v-divider></v-divider>
    </v-list>
</template>

<script setup lang="ts">
import { upConfig } from '../../store/store'
const upconfig = upConfig()

</script>

<style scoped lang="less">
.setting-file,
.setting-config {
    padding: 0 15px;
}
</style>