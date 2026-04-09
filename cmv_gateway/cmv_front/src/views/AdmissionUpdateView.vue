<script setup lang="ts">
import PageHeader from '@/components/PageHeader.vue'
import useHttp from '@/composables/useHttp'
import type Admission from '@/models/admission'
import { Button, DatePicker, Message } from 'primevue'
import { Field, useForm } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import { z } from 'zod'
import { onBeforeMount, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

const router = useRouter()
const route = useRoute()
const http = useHttp()
const { t } = useI18n()

const admission = ref<Admission | null>(null)

const schema = toTypedSchema(
  z
    .object({
      date_entree: z.date({ required_error: t('validation.required') }),
      date_sortie_prevue: z.date({ required_error: t('validation.required') }),
      date_sortie: z.date({ required_error: t('validation.required') }),
    })
    .refine((data) => data.date_sortie_prevue >= data.date_entree, {
      message: t('validation.date_sortie_prevue_after_entree', 'La date de sortie prévue doit être après la date d\'entrée'),
      path: ['date_sortie_prevue'],
    })
    .refine((data) => data.date_sortie >= data.date_entree, {
      message: t('validation.date_sortie_after_entree', 'La date de sortie doit être après la date d\'entrée'),
      path: ['date_sortie'],
    })
)

const { handleSubmit, setFieldValue, values } = useForm({
  validationSchema: schema,
  initialValues: {
    date_entree: new Date(),
    date_sortie_prevue: new Date(),
    date_sortie: new Date(),
  },
})

const getAdmission = () => {
  const applyData = (data: Admission) => {
    setFieldValue('date_entree', new Date(data.entree_le))
    setFieldValue('date_sortie_prevue', new Date(data.sortie_prevue_le!))
    setFieldValue('date_sortie', new Date(data.sorti_le ?? Date.now()))
    admission.value = data
  }
  http.sendRequest({ path: `/patients/admissions/${route.params.admissionId}` }, applyData)
}

const closeAdmission = handleSubmit(() => {
  const applyData = () => {
    router.push('/')
  }
  http.sendRequest(
    {
      path: `/patients/admissions/closure`,
      method: 'PUT',
      body: { data: { ...admission.value, sorti_le: values.date_sortie } },
    },
    applyData,
  )
})

const deleteAdmission = () => {
  http.sendRequest(
    {
      path: `/patients/admissions/${route.params.admissionId}`,
      method: 'DELETE',
    },
    () => {
      router.push('/')
    },
  )
}

onBeforeMount(() => {
  getAdmission()
})
</script>

<template>
  <main class="min-w-screen flex flex-col gap-y-8 text-xs p-2">
    <PageHeader
      title="Espace Administratif"
      description="Mettre à jour une admission pour un patient"
    />
    <form class="flex flex-col gap-y-8 w-5/6 lg:w-[42rem]" @submit.prevent="closeAdmission">
      <div v-if="values.date_entree" class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <span class="flex flex-col gap-y-2">
          <Field v-slot="{ field, errorMessage }" name="date_entree">
            <label for="date_entree">Date d'entrée</label>
            <DatePicker
              showIcon
              fluid
              selectionMode="single"
              view="date"
              :showButtonBar="true"
              yearRange="1900:2050"
              locale="fr"
              iconDisplay="input"
              v-bind="field"
              id="date_entree"
              name="date_entree"
              aria-label="date d'entrée de l'admission"
              :modelValue="values.date_entree"
              @update:modelValue="setFieldValue('date_entree', $event as Date | undefined)"
            />
            <Message v-show="errorMessage" class="text-xs" severity="error">
              {{ errorMessage }}
            </Message>
          </Field>
        </span>
        <span class="flex flex-col gap-y-2">
          <Field v-slot="{ field, errorMessage }" name="date_sortie_prevue">
            <label for="date_sortie_prevue">Sortie prévue le</label>
            <DatePicker
              showIcon
              fluid
              selectionMode="single"
              view="date"
              :showButtonBar="true"
              yearRange="1900:2050"
              locale="fr"
              iconDisplay="input"
              v-bind="field"
              id="date_sortie_prevue"
              name="date_sortie_prevue"
              aria-label="date de sortie prévue de l'admission"
              :modelValue="values.date_sortie_prevue"
              @update:modelValue="setFieldValue('date_sortie_prevue', $event as Date | undefined)"
            />
            <Message v-show="errorMessage" class="text-xs" severity="error">
              {{ errorMessage }}
            </Message>
          </Field>
        </span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <span class="flex flex-col gap-y-2">
          <Field v-slot="{ field, errorMessage }" name="date_sortie">
            <label for="date_sortie">Date de sortie</label>
            <DatePicker
              showIcon
              fluid
              selectionMode="single"
              view="date"
              :showButtonBar="true"
              yearRange="1900:2050"
              locale="fr"
              iconDisplay="input"
              v-bind="field"
              id="date_sortie"
              name="date_sortie"
              aria-label="date de sortie de l'admission"
              :modelValue="values.date_sortie"
              @update:modelValue="setFieldValue('date_sortie', $event as Date | undefined)"
            />
            <Message v-show="errorMessage" class="text-xs" severity="error">
              {{ errorMessage }}
            </Message>
          </Field>
        </span>
      </div>

      <span class="w-full flex items-center gap-x-4">
        <Button fluid label="Supprimer" type="button" @click="deleteAdmission" />
        <Button fluid label="Annuler" type="button" @click="router.back()" severity="warn" />
        <Button
          fluid
          label="Clôturer l'admission"
          type="submit"
          :loading="http.isLoading.value"
          severity="error"
        />
      </span>
    </form>
  </main>
</template>
