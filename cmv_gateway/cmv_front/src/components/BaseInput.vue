<script setup lang="ts">
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'

type Props = {
  type?: 'text' | 'number'
  modelValue: string
  invalid: boolean
  placeholder?: string
  name: string
  label?: string
  error?: string
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  placeholder: '',
  label: '',
  error: ''
})
</script>

<template>
  <div class="w-full flex flex-col gap-y-2">
    <label :for="props.name" v-if="props.label">{{ props.label }}</label>
    <span class="flex items-center gap-x-2" v-if="props.error">
      <Message severity="error" icon="pi pi-times-circle" :aria-label="`erreur ${props.name}`" />
      <Message class="text-xs" severity="error">{{ props.error }}</Message>
    </span>
    <InputText
      :type="props.type"
      :id="props.name"
      :name="props.name"
      :model-value="props.modelValue"
      :invalid="props.invalid"
      :placeholder="props.placeholder"
      :aria-label="props.name"
      @update:model-value="$emit('update:modelValue', $event)"
      v-bind="$attrs"
    />
  </div>
</template>
