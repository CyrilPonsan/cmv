<!-- eslint-disable @typescript-eslint/no-unused-vars -->
<template>
  <Card class="w-96" style="overflow: hidden">
    <template #header>
      <div
        class="w-full h-48 bg-[url('../assets/images/witch.jpg')] bg-center-top bg-no-repeat bg-cover"
      ></div>
    </template>
    <template #title>Advanced Card</template>
    <template #subtitle>Card subtitle</template>
    <template #content>
      <p class="m-0">
        Lorem ipsum dolor sit amet, consectetur adipisicing elit. Inventore sed consequuntur error
        repudiandae numquam deserunt quisquam repellat libero asperiores earum nam nobis, culpa
        ratione quam perferendis esse, cupiditate neque quas!
      </p>
    </template>
    <template #footer>
      <div class="flex gap-4 mt-1">
        <Button label="Cancel" severity="secondary" outlined class="w-full" />
        <Button label="Save" class="w-full" />
      </div>
    </template>
  </Card>
</template>

<script setup lang="ts">
import Button from 'primevue/button'
import Card from 'primevue/card'

/* interface Props {
  chambre: Chambre
}

const props = defineProps<Props>()

const style = computed(() => {
  const baseStyle =
    'text-xl font-bold p-4 rounded-tl-xl rounded-tr-xl flex justify-between text-neutral-content w-full'
  switch (props.chambre.status) {
    case 'occupée':
      return baseStyle + ' bg-primary'
    default:
      return baseStyle + ' bg-secondary'
  }
}) */
</script>
