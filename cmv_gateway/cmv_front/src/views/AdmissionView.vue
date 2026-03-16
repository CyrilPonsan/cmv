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
import { Button, Checkbox, DatePicker, Message, Select, Slider, InputNumber, useToast } from 'primevue'
import { Field, Form } from 'vee-validate'
import { onBeforeMount, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

type ServicesList = {
  id_service: number
  nom: string
}

// Initialisation des composables
const { sendRequest, isLoading, error } = useHttp()
const toast = useToast()

const entreeLe = ref(new Date())
const sortiePrevueLe = ref(new Date())
const ambulatoire = ref<string>('Ambulatoire')
const options = ref(['Ambulatoire', 'Non ambulatoire'])
const servicesOptions = ref<string[]>([])
const servicesList = ref<ServicesList[]>([])
const service = ref<string>()
const predictionResult = ref<number | null>(null)

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

// Variables binaires (0 ou 1)
const booleanFeatures = ref([
  'gender',
  'dialysisrenalendstage',
  'asthma',
  'irondef',
  'pneum',
  'substancedependence',
  'psychologicaldisordermajor',
  'depress',
  'psychother',
  'fibrosisandother',
  'malnutrition',
  'hemo'
])

// Variables continues avec leurs limites
const continuousFeatures = ref([
  { id: 'hematocrit', label: 'Hématocrite', min: 0.1, max: 60.0, step: 0.1, default: 40.0 },
  { id: 'neutrophils', label: 'Neutrophiles', min: 0.1, max: 30.0, step: 0.1, default: 5.0 },
  { id: 'sodium', label: 'Sodium', min: 100.0, max: 160.0, step: 0.5, default: 140.0 },
  { id: 'glucose', label: 'Glucose', min: 50.0, max: 400.0, step: 1.0, default: 100.0 },
  { id: 'bloodureanitro', label: 'BUN (Urée)', min: 1.0, max: 100.0, step: 0.5, default: 15.0 },
  { id: 'creatinine', label: 'Créatinine', min: 0.1, max: 15.0, step: 0.1, default: 1.0 },
  { id: 'bmi', label: 'BMI', min: 10.0, max: 60.0, step: 0.1, default: 25.0 },
  { id: 'pulse', label: 'Pouls', min: 30, max: 200, step: 1, default: 75 },
  { id: 'respiration', label: 'Respiration', min: 5.0, max: 40.0, step: 0.5, default: 15.0 }
])

const propsFeatures = ref<Record<string, number | null>>({
  // Initialisation par défaut basée sur ton backend ml
  rcount: 0,
  secondarydiagnosisnonicd9: 0
})

// Initialisation des valurs par défaut pour les sliders/continus
onBeforeMount(() => {
  getServicesList()
  continuousFeatures.value.forEach((feature) => {
    propsFeatures.value[feature.id] = feature.default
  })
})

type PredictionResponse = {
  prediction_id: string
  predicted_length_of_stay: number
}

const postPrediction = () => {
  // Préparation des données en retirant d'éventuels null
  const cleanData = Object.fromEntries(
    Object.entries(propsFeatures.value).filter(([_, v]) => v != null)
  )

  const applyData = (data: PredictionResponse) => {
    const result = Math.ceil(data.predicted_length_of_stay)
    predictionResult.value = result
    toast.add({
      severity: 'success',
      summary: 'Prédiction réussie',
      detail: `Durée de séjour prédite : ${result} jours`,
      life: 3000
    })
  }
  sendRequest<PredictionResponse>(
    { path: '/ml/predictions/predict', method: 'POST', body: cleanData },
    applyData
  )
}

// Extraction de l'ID du patient depuis les paramètres de la route
const patientId = route.params.patientId

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

    <div class="w-full lg:w-[60rem] mt-8 bg-surface-50 dark:bg-surface-900 p-6 rounded-lg border border-surface-200 dark:border-surface-700">
      <h3 class="text-lg font-bold mb-4">Outil d'Aide à la Décision (IA)</h3>
      <p class="text-xs text-surface-500 mb-6">Prédiction de la durée du séjour basée sur le dossier du patient</p>
      
      <Form class="grid grid-cols-1 lg:grid-cols-2 gap-8 w-full">
        
        <!-- Colonne 1 : Antécédents (Booléens) -->
        <div class="flex flex-col gap-y-4 w-full">
          <h4 class="font-semibold text-primary">Antécédents / Pathologies</h4>
          <div class="grid grid-cols-2 gap-3">
            <div v-for="feature in booleanFeatures" :key="feature" class="flex items-center gap-x-2">
              <Checkbox
                :name="feature"
                :inputId="feature"
                :binary="true"
                v-model="propsFeatures[feature]"
                :trueValue="1"
                :falseValue="0"
              />
              <label :for="feature" class="cursor-pointer capitalize text-xs">
                 {{ feature === 'dialysisrenalendstage' ? 'Dialysis' : feature === 'psychologicaldisordermajor' ? 'Psychol. Disorder' : feature }}
              </label>
            </div>
          </div>

          <h4 class="font-semibold text-primary mt-4">Historique & Diagnostiques</h4>
          <div class="flex flex-col gap-x-4">
            <div class="flex flex-col gap-y-2 flex-1">
              <label for="rcount" class="text-xs">Nombre de visites prec.</label>
              <InputNumber v-model="propsFeatures['rcount']" inputId="rcount" :min="0" :max="50" class="w-full" showButtons />
            </div>
            <div class="flex flex-col gap-y-2 flex-1">
              <label for="secondarydiagnose" class="text-xs">Diagnostiques second.</label>
              <InputNumber v-model="propsFeatures['secondarydiagnosisnonicd9']" inputId="secondarydiagnose" :min="0" :max="20" class="w-full" showButtons />
            </div>  
          </div>
        </div>

        <!-- Colonne 2 : Variables Continues (Sliders) -->
        <div class="flex flex-col gap-y-6">
          <h4 class="font-semibold text-primary">Constantes Sanguines & Vitales</h4>
          <div class="grid grid-cols-1 gap-y-5 w-full">
            <div v-for="cf in continuousFeatures" :key="cf.id" class="flex flex-col gap-y-4">
              <div class="flex justify-between max-w-72 items-center text-xs">
                <label :for="cf.id" class="font-medium">{{ cf.label }}</label>
           
                <InputNumber v-model="propsFeatures[cf.id]" :inputId="cf.id" :min="cf.min" :max="cf.max" :step="cf.step" class="max-w-8" inputClass="!text-right !text-xs !p-1" :minFractionDigits="cf.step < 1 ? 1 : 0" />
              </div>
              <Slider :modelValue="propsFeatures[cf.id] as number" @update:modelValue="propsFeatures[cf.id] = $event as number" :min="cf.min" :max="cf.max" :step="cf.step" class="w-full" />
            </div>
          </div>
        </div>
      </Form>

      <!-- Actions de la prédiction -->
      <div class="flex items-center justify-between mt-8 border-t border-surface-200 dark:border-surface-700 pt-6">
        <Button
          label="Estimer la durée du séjour"
          @click="postPrediction"
          icon="pi pi-calculator"
          severity="help"
          :loading="isLoading"
          class="w-64"
        />

        <div v-if="predictionResult" class="flex items-center gap-x-6 bg-primary-50 dark:bg-primary-900/40 p-3 rounded-lg border border-primary-200 dark:border-primary-800">
          <div class="flex flex-col">
            <span class="text-xs text-surface-500">Durée estimée</span>
            <span class="text-2xl font-bold text-primary">{{ predictionResult }} jours</span>
          </div>
          <Button
            label="Appliquer l'estimation"
            icon="pi pi-check"
            @click="sortiePrevueLe = new Date(entreeLe.getTime() + predictionResult * 24 * 60 * 60 * 1000)"
            severity="success"
            outlined
          />
        </div>
      </div>
    </div>
  </main>
</template>
