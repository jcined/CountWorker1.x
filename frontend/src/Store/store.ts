import { defineStore } from 'pinia'
import { Datas } from './index'

type Data = {
    projects: {
        name: string
        time: string
        id: string
        files: {
            name: string
            path: string
        }[]
    }[]
    lives: {
        name: string
        time: string
        id: string
        state: boolean
        projectId: {
            name: string
            id: string
        }
    }[]
}

export const Data = defineStore(Datas.Basic, {
    state: () => {
        return <{
            data: Data
        }>
            {
                data: {
                    projects: [],
                    lives: [],
                }
            }
    },
})

export const Url = defineStore(Datas.Basic, {
    state: () => {
        return {
            isInit: false,
            ip: "",
            login: "/api/login",
            init: "/api/data",
            newproject: "/api/newproject",
            newfile: "/api/newfile",
            upload: "/api/upload",
            uploadFile: "/api/uploadfile",
            rename: "/api/rename",
            delete: "/api/delete",
            download: "/api/download",
            newlive: "/api/newlive",
        }
    },
})