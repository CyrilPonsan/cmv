<template>Page Detail</template>

<script setup lang="ts">
import useHttp from '@/composables/use-http'
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const http = useHttp()

const id = route.params.chambreId
const chambre = ref({})

const getDetail = () => {
  const applyData = (data: any) => {
    chambre.value = data
  }
  http.sendRequest({ path: `/home/chambres/${id}` }, applyData)
}

onMounted(() => getDetail())
</script>
