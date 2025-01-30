<script setup lang="ts">
/**
 * @file AdmissionView.vue
 * @description Vue permettant de créer une nouvelle admission pour un patient
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

// Import des composables et composants nécessaires
import PageHeader from '@/components/PageHeader.vue'
import useHttp from '@/composables/useHttp'
import type Admission from '@/models/admission'
import { Button, DatePicker, Message, Select, useToast } from 'primevue'
import { Field, Form } from 'vee-validate'
import { onBeforeMount, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

type ServicesList = {
  id_service: number
  nom: string
}

// Initialisation des composables
const { sendRequest, error } = useHttp()
const toast = useToast()

const entreeLe = ref(new Date())
const sortiePrevueLe = ref(new Date())
const ambulatoire = ref<string>('Ambulatoire')
const options = ref(['Ambulatoire', 'Non ambulatoire'])
const servicesOptions = ref<string[]>([])
const servicesList = ref<ServicesList[]>([])
const service = ref<string>()

/**
 * Crée une nouvelle admission pour le patient
 * Envoie une requête POST au serveur avec les données de l'admission
 */
const postAdmission = () => {
  const applyData = (data: Admission) => {
    toast.add({
      severity: 'success',
      summary: 'Admission créée avec succès',
      detail: `${!data.ambulatoire ? 'Chambre : ' + data.nom_chambre : 'Ambulatoire'}`,
      life: 3000
    })
    router.push(`/patient/${patientId}`)
  }
  sendRequest(
    {
      path: '/patients/admissions',
      method: 'POST',
      body: {
        patient_id: patientId,
        ambulatoire: ambulatoire.value === 'Ambulatoire',
        entree_le: entreeLe.value,
        sortie_prevue_le: sortiePrevueLe.value,
        service_id: servicesList.value.find((item) => item.nom === service.value)?.id_service
      }
    },
    applyData
  )
}

// Surveillance des erreurs pour afficher les notifications
watch(error, (newError) => {
  if (newError && newError.length > 0) {
    toast.add({
      severity: 'error',
      detail: newError,
      life: 3000
    })
  }
})

const getServicesList = () => {
  const applyData = (data: ServicesList[]) => {
    servicesList.value = data
    servicesOptions.value = data.map((service) => service.nom)
  }
  sendRequest<ServicesList[]>(
    {
      path: '/chambres/services/simple',
      method: 'GET'
    },
    applyData
  )
}

// Récupération des paramètres de la route
const route = useRoute()
const router = useRouter()

// Extraction de l'ID du patient depuis les paramètres de la route
const patientId = route.params.patientId

onBeforeMount(() => {
  getServicesList()
})
</script>

<template>
  <main class="min-w-screen flex flex-col gap-y-8 text-xs p-2">
    <PageHeader title="Espace Administratif" description="Créer une admission pour un patient" />
    <Form class="flex flex-col gap-y-8 w-5/6 lg:w-[42rem]">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <span class="flex flex-col gap-y-2">
          <Field v-slot="{ field, errorMessage }" name="date_entree">
            <label for="date_entree">Date d'entrée</label>
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
              yearRange="1900:2024"
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
          <Field v-slot="{ field, errorMessage }" name="ambulatoire">
            <label for="ambulatoire">Ambulatoire</label>
            <Select
              v-bind="field"
              label="Type d'admission"
              placeholder="Ambulatoire"
              name="civilite"
              :options="options"
              id="ambulatoire"
              aria-label="ambulatoire"
              v-model="ambulatoire"
            />
            <Message v-show="errorMessage" class="text-xs text-error" severity="error">
              {{ errorMessage }}
            </Message>
          </Field>
        </span>
        <span class="flex flex-col gap-y-2">
          <Field v-slot="{ field, errorMessage }" name="services">
            <label for="services">Services</label>
            <Select
              v-bind="field"
              label="Services"
              placeholder="Services"
              name="services"
              :options="servicesOptions"
              id="services"
              aria-label="services"
              v-model="service"
            />
            <Message v-show="errorMessage" class="text-xs text-error" severity="error">
              {{ errorMessage }}
            </Message>
          </Field>
        </span>
      </div>
      <span class="w-full flex items-center gap-x-4">
        <Button fluid label="Annuler" @click="router.back()" severity="warn" />
        <Button fluid label="Créer une admission" @click="postAdmission" severity="success" />
      </span>
    </Form>
  </main>
</template>
