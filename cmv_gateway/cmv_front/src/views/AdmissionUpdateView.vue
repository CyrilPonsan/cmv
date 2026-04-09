<script setup lang="ts">
import PageHeader from '@/components/PageHeader.vue'
import useHttp from '@/composables/useHttp'
import type Admission from '@/models/admission'
import { Button, DatePicker, Message } from 'primevue'
import { Field, Form } from 'vee-validate'
import { onBeforeMount, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const router = useRouter()
const route = useRoute()
const http = useHttp()

const entreeLe = ref<Date | null>(null)
const sortiePrevueLe = ref<Date | null>(null)
const ambulatoire = ref<boolean>(true)
const service = ref<string | null>(null)
const sortiLe = ref<Date>(new Date())

const getAdmission = () => {
  const applyData = (data: Admission) => {
    entreeLe.value = new Date(data.entree_le)
    sortiePrevueLe.value = new Date(data.sortie_prevue_le!)
    ambulatoire.value = data.ambulatoire
    service.value = data.ref_chambre
    sortiLe.value = new Date(data.sorti_le ?? Date.now())
  }
  http.sendRequest({ path: `/patients/admissions/${route.params.admissionId}` }, applyData)
}

const closeAdmission = () => {
  const applyData = (data: any) => {
    console.log({ data })
    router.push(`/patients/${route.params.patientId}/close`)
  }
  http.sendRequest(
    {
      path: `/ml/predict/${route.params.admissionId}`,
      method: 'PUT',
      body: { sorti_le: sortiLe.value }
    },
    applyData
  )
}

const delteAdmission = () => {
  const applyData = (data: { message: string }) => {
    console.log(data.message)
    router.push(`/patients/${route.params.patientId}/admissions`)
  }
  http.sendRequest(
    {
      path: `/patients/admissions/${route.params.admissionId}`,
      method: 'DELETE'
    },
    applyData
  )
}

onBeforeMount(() => {
  getAdmission()
})
</script>

<template>
  <main ref="formTopRef" class="min-w-screen flex flex-col gap-y-8 text-xs p-2">
    <PageHeader
      title="Espace Administratif"
      description="Mettre à jour une admission pour un patient"
    />
    <Form class="flex flex-col gap-y-8 w-5/6 lg:w-[42rem]">
      <div v-if="entreeLe" class="grid grid-cols-1 md:grid-cols-2 gap-4">
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
              v-model="entreeLe"
            />
            <Message v-show="errorMessage" class="text-xs text-error" severity="error">
              {{ errorMessage }}
            </Message>
          </Field>
        </span>
        <span class="flex flex-col gap-y-2">
          <Field v-slot="{ field, errorMessage }" name="date_sortie">
            <label for="date_sortie">Sortie prévue le</label>
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
              aria-label="date de sortie prévue de l'admission"
              v-model="sortiePrevueLe"
            />
            <Message v-show="errorMessage" class="text-xs text-error" severity="error">
              {{ errorMessage }}
            </Message>
          </Field>
        </span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <span class="flex flex-col gap-y-2">
          <Field v-slot="{ field, errorMessage }" name="date_sortie">
            <label for="date_entree">Date de sortie</label>
            <DatePicker
              showIcon
              fluid
              selectionMode="single"
              view="date"
              :showButtonBar="true"
              yearRange="1900:2024"
              locale="fr"
              iconDisplay="input"
              v-bind="field"
              id="date_sortie"
              name="date_sortie"
              aria-label="date de sortie de l'admission"
              v-model="sortiLe"
            />
            <Message v-show="errorMessage" class="text-xs text-error" severity="error">
              {{ errorMessage }}
            </Message>
          </Field>
        </span>
      </div>
      <span class="w-full flex items-center gap-x-4">
        <Button fluid label="Supprimer" @click="delteAdmission" />
        <Button fluid label="Annuler" @click="router.back()" severity="warn" />
        <Button
          fluid
          label="Clôturer l' admission"
          @click="closeAdmission"
          :load="http.isLoading"
          severity="success"
        />
      </span>
    </Form>
  </main>
</template>
