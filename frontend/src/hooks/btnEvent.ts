import axios from 'axios'
import { state } from '../store/store'
import { ElMessage } from 'element-plus'
const State = state()

// 按钮点击事件
export default function btnEvent(key: string | undefined) {
    if (!undefined) {
        if (State.state) {
            console.log(key)
            axios.get(`/api/active/button/${key}`)
            .then(()=>{
                console.log("程序已接收")
            })
            .catch(()=>{
                ElMessage.error('信号发送失败')
            })
            return
        }
        ElMessage.error('策略已停止')
    }
}