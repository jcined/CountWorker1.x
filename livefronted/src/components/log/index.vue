<template>
    <Bar></Bar>
    <div id="Log">
        <Select></Select>
        <log_Log></log_Log>
    </div>
</template>

<script setup lang="ts">
import log_Log from './Logmain.vue'
import Select from './Select.vue'
import Bar from '../appBars.vue'
import Sinit from '../../hooks/Sinit'

Sinit()

</script>

<style scoped lang="less">
#Log {
    @media screen and (min-width: 800px) {
        padding: 10px 28%;
    }

    @media screen and (max-width: 800px) {
        padding: 10px;
    }

    width: 100%;
    box-sizing: border-box;
    margin: 64px 0;
}
</style>