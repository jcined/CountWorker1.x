<template>
    <Bar></Bar>
    <div id="Setting">
        <setting></setting>
        <strategyConfig></strategyConfig>
    </div>
</template>

<script setup lang="ts">
import setting from './settingmain.vue'
import strategyConfig from './strategyConfig.vue'
import Bar from '../appBars.vue'
import Sinit from '../../hooks/Sinit'
Sinit()
</script>

<style scoped lang="less">
#Setting {
    @media screen and (min-width: 800px) {
        padding: 0 28%;
    }

    width: 100%;
    box-sizing: border-box;
    margin: 64px 0;

    .setting-save {
        margin-top: 20px;
        width: 100%;
        display: flex;
        justify-content: center;
    }

}
</style>