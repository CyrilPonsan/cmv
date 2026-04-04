<script setup lang="ts">
/**
 * @file AdmissionView.vue
 * @description Vue permettant de créer une nouvelle admission pour un patient
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

// Import des composables et composants nécessaires
import PageHeader from '@/components/PageHeader.vue'
import useHttp from '@/composables/useHttp'
import { z } from 'zod'
import type Admission from '@/models/admission'
import { toTypedSchema } from '@vee-validate/zod'
import {
  Button,
  Checkbox,
  DatePicker,
  Message,
  Select,
  Slider,
  InputNumber,
  useToast
} from 'primevue'
import { Field, Form } from 'vee-validate'
import { onBeforeMount, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useServices } from '@/stores/services'
import { storeToRefs } from 'pinia'

type ServicesList = {
  id_service: number
  nom: string
}

// Initialisation des composables
const { sendRequest, isLoading, error } = useHttp()
const toast = useToast()
const store = useServices()

const entreeLe = ref(new Date())
const sortiePrevueLe = ref(new Date())
const ambulatoire = ref<string>('Ambulatoire')
const options = ref(['Ambulatoire', 'Non ambulatoire'])
const { servicesList, servicesOptions } = storeToRefs(store)

const service = ref<string>()
const predictionResult = ref<number | null>(null)
const today = ref(new Date())

const schemaAdmission = toTypedSchema(
  z.object({
    ambulatoire: z.enum(['Ambulatoire', 'Non ambulatoire']),
    entree_le: z.date(),
    sortie_prevue_le: z.date(),
    services: z.string().optional()
  })
)

/**
 * Crée une nouvelle admission pour le patient
 * Envoie une requête POST au serveur avec les données de l'admission
 */
const postAdmission = (values: Record<string, unknown>) => {
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
        ambulatoire: values.ambulatoire === 'Ambulatoire',
        entree_le: values.entree_le,
        sortie_prevue_le: values.sortie_prevue_le,
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
  { id: 'hematocrit', label: 'Hématocrite', min: 0.0, max: 60.0, step: 0.1, default: 0.0 },
  { id: 'neutrophils', label: 'Neutrophiles', min: 0.0, max: 30.0, step: 0.1, default: 0.0 },
  { id: 'sodium', label: 'Sodium', min: 0.0, max: 160.0, step: 0.5, default: 0.0 },
  { id: 'glucose', label: 'Glucose', min: 0.0, max: 400.0, step: 1.0, default: 0.0 },
  { id: 'bloodureanitro', label: 'BUN (Urée)', min: 0.0, max: 100.0, step: 0.5, default: 0.0 },
  { id: 'creatinine', label: 'Créatinine', min: 0.0, max: 15.0, step: 0.1, default: 0.0 },
  { id: 'bmi', label: 'BMI', min: 0.0, max: 60.0, step: 0.1, default: 0.0 },
  { id: 'pulse', label: 'Pouls', min: 0, max: 200, step: 1, default: 0 },
  { id: 'respiration', label: 'Respiration', min: 0.0, max: 40.0, step: 0.5, default: 0.0 }
])

const propsFeatures = ref<Record<string, number | null>>({
  // Initialisation par défaut basée sur ton backend ml
  rcount: 0,
  secondarydiagnosisnonicd9: 0
})

type PredictionResponse = {
  prediction_id: string
  predicted_length_of_stay: number
}

const postPrediction = () => {
  // Préparation des données: toutes les valeurs continues laissées à 0 par défaut
  // deviennent 'null' pour que XGBoost utilise sa branche par défaut pour les NaN.
  // Exception : rcount et secondarydiagnosisnonicd9 peuvent rester à 0.
  const cleanData = Object.fromEntries(
    Object.entries(propsFeatures.value)
      .map(([key, v]) => {
        // Si la clé est une variable continue et la valeur est 0, on met null
        const isContinuous = continuousFeatures.value.some((f) => f.id === key)
        if (isContinuous && v === 0) {
          return [key, null]
        }
        return [key, v]
      })
      .filter(([_, v]) => v !== undefined) // On garde null mais on vire undefined au cas où
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

// Réf vers le haut du formulaire pour l'autoscroll
const formTopRef = ref<any>(null)

const applyPrediction = () => {
  if (predictionResult.value) {
    // 1. Mettre à jour la date de sortie
    sortiePrevueLe.value = new Date(
      entreeLe.value.getTime() + predictionResult.value * 24 * 60 * 60 * 1000
    )
    // 2. Basculer sur 'Non ambulatoire' (puisqu'il y a un séjour calculé)
    ambulatoire.value = 'Non ambulatoire'
    // 3. Scroller de manière douce vers le haut du formulaire
    if (formTopRef.value) {
      console.log('bingo', formTopRef.value)
      if (formTopRef.value.$el) {
        formTopRef.value.$el.scrollIntoView({ behavior: 'smooth', block: 'start' })
      } else {
        formTopRef.value.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
    }
  }
}

// Initialisation des valurs par défaut pour les sliders/continus
onBeforeMount(() => {
  continuousFeatures.value.forEach((feature) => {
    propsFeatures.value[feature.id] = feature.default
  })
})

const handleSubmit = (values: Record<string, unknown>) => {
  postAdmission(values)
}
</script>

<template>
  <main ref="formTopRef" class="min-w-screen flex flex-col gap-y-8 text-xs p-2">
    <PageHeader title="Espace Administratif" description="Créer une admission pour un patient" />
    <Form
      class="flex flex-col gap-y-8 w-5/6 lg:w-[42rem]"
      :validationSchema="schemaAdmission"
      :initialValues="{
        ambulatoire,
        entree_le: today,
        sortie_prevue_le: today
      }"
      @submit="handleSubmit"
    >
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <span class="flex flex-col gap-y-2">
          <Field v-slot="{ field, errorMessage }" name="entree_le">
            <label for="entree_le">Date d'entrée</label>
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
              id="entree_le"
              name="entree_le"
              aria-label="date d'entrée de l'admission"
            />
            <Message v-show="errorMessage" class="text-xs text-error" severity="error">
              {{ errorMessage }}
            </Message>
          </Field>
        </span>
        <span class="flex flex-col gap-y-2">
          <Field v-slot="{ field, errorMessage }" name="sortie_prevue_le">
            <label for="sortie_prevue_le">Sortie prévue le</label>
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
              id="sortie_prevue_le"
              name="sortie_prevue_le"
              aria-label="date de sortie prévue de l'admission"
            />
            <Message v-show="errorMessage" class="text-xs text-error" severity="error">
              {{ errorMessage }}
            </Message>
          </Field>
        </span>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <span class="flex flex-col gap-y-2">
          <Field v-slot="{ value, handleChange, errorMessage }" name="ambulatoire">
            <label for="ambulatoire">Ambulatoire</label>
            <Select
              :modelValue="value"
              @update:modelValue="handleChange"
              label="Type d'admission"
              placeholder="Ambulatoire"
              name="ambulatoire"
              :options="options"
              id="ambulatoire"
              aria-label="ambulatoire"
            />
            <Message v-show="errorMessage" class="text-xs text-error" severity="error">
              {{ errorMessage }}
            </Message>
          </Field>
        </span>
        <span class="flex flex-col gap-y-2">
          <Field v-slot="{ value, handleChange, errorMessage }" name="services">
            <label for="services">Services</label>
            <Select
              :modelValue="value"
              @update:modelValue="handleChange"
              label="Services"
              placeholder="Services"
              name="services"
              :options="servicesOptions"
              id="services"
              aria-label="services"
            />
            <Message v-show="errorMessage" class="text-xs text-error" severity="error">
              {{ errorMessage }}
            </Message>
          </Field>
        </span>
      </div>
      <span class="w-full flex items-center gap-x-4">
        <Button fluid label="Annuler" @click="router.back()" severity="warn" />
        <Button fluid label="Créer une admission" type="submit" severity="success" />
      </span>
    </Form>

    <div
      class="w-full lg:w-[60rem] mt-8 bg-surface-50 dark:bg-surface-900 p-6 rounded-lg border border-surface-200 dark:border-surface-700"
    >
      <h3 class="text-lg font-bold mb-4">Outil d'Aide à la Décision (IA)</h3>
      <p class="text-xs text-surface-500 mb-6">
        Prédiction de la durée du séjour basée sur le dossier du patient
      </p>

      <Form class="grid grid-cols-1 lg:grid-cols-2 gap-8 w-full">
        <!-- Colonne 1 : Antécédents (Booléens) -->
        <div class="flex flex-col gap-y-4 w-full">
          <h4 class="font-semibold text-primary">Antécédents / Pathologies</h4>
          <div class="grid grid-cols-2 gap-3">
            <div
              v-for="feature in booleanFeatures"
              :key="feature"
              class="flex items-center gap-x-2"
            >
              <Checkbox
                :name="feature"
                :inputId="feature"
                :binary="true"
                v-model="propsFeatures[feature]"
                :trueValue="1"
                :falseValue="0"
              />
              <label :for="feature" class="cursor-pointer capitalize text-xs">
                {{
                  feature === 'dialysisrenalendstage'
                    ? 'Dialysis'
                    : feature === 'psychologicaldisordermajor'
                      ? 'Psychol. Disorder'
                      : feature
                }}
              </label>
            </div>
          </div>

          <h4 class="font-semibold text-primary mt-4">Historique & Diagnostiques</h4>
          <div class="flex flex-col gap-x-4">
            <div class="flex flex-col gap-y-2 flex-1">
              <label for="rcount" class="text-xs">Nombre de visites prec.</label>
              <InputNumber
                v-model="propsFeatures['rcount']"
                inputId="rcount"
                :min="0"
                :max="50"
                class="w-full"
                showButtons
              />
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

                <InputNumber
                  v-model="propsFeatures[cf.id]"
                  :inputId="cf.id"
                  :min="cf.min"
                  :max="cf.max"
                  :step="cf.step"
                  class="max-w-8"
                  inputClass="!text-right !text-xs !p-1"
                  :minFractionDigits="cf.step < 1 ? 1 : 0"
                />
              </div>
              <Slider
                :modelValue="propsFeatures[cf.id] as number"
                @update:modelValue="propsFeatures[cf.id] = $event as number"
                :min="cf.min"
                :max="cf.max"
                :step="cf.step"
                class="w-full"
              />
            </div>
          </div>
        </div>
      </Form>

      <!-- Actions de la prédiction -->
      <div
        class="flex items-center justify-between mt-8 border-t border-surface-200 dark:border-surface-700 pt-6"
      >
        <Button
          label="Estimer la durée du séjour"
          @click="postPrediction"
          icon="pi pi-calculator"
          severity="help"
          :loading="isLoading"
          class="w-64"
        />

        <div
          v-if="predictionResult"
          class="flex items-center gap-x-6 bg-primary-50 dark:bg-primary-900/40 p-3 rounded-lg border border-primary-200 dark:border-primary-800"
        >
          <div class="flex flex-col">
            <span class="text-xs text-surface-500">Durée estimée</span>
            <span class="text-2xl font-bold text-primary">{{ predictionResult }} jours</span>
          </div>
          <Button
            label="Appliquer l'estimation"
            icon="pi pi-check"
            @click="applyPrediction"
            severity="success"
            outlined
          />
        </div>
      </div>
    </div>
  </main>
</template>
