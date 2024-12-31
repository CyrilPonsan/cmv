<script setup lang="ts">
/**
 * @file PatientForm.vue
 * @description Formulaire de création/modification d'un patient
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

// Import des dépendances nécessaires
import type DetailPatient from '@/models/detail-patient'
import { toTypedSchema } from '@vee-validate/zod'
import Button from 'primevue/button'
import DatePicker from 'primevue/datepicker'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import Select from 'primevue/select'
import Textarea from 'primevue/textarea'
import { Field, Form } from 'vee-validate'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

// Définition des props du composant
const props = defineProps<{
  patientDetail?: DetailPatient
  civilites: string[]
  onSubmit: (data: Record<string, unknown>) => void
  schema: ReturnType<typeof toTypedSchema>
  isLoading: boolean
}>()

const { t } = useI18n()

// Gestion de la soumission du formulaire
const handleSubmit = (values: Record<string, unknown>) => {
  if (props.patientDetail?.id_patient) {
    props.onSubmit({ ...values, id_patient: props.patientDetail.id_patient })
  } else {
    props.onSubmit(values)
  }
}

const date = computed(() =>
  props.patientDetail?.date_de_naissance ? new Date(props.patientDetail.date_de_naissance) : null
)
</script>

<template>
  <!-- Formulaire principal -->
  <Form
    class="flex flex-col gap-y-8 w-5/6 lg:w-[42rem]"
    :validation-schema="schema"
    :initial-values="patientDetail ?? {}"
    @submit="handleSubmit"
  >
    <!-- Section civilité et date de naissance -->
    <div class="w-full grid grid-cols-1 md:grid-cols-2 gap-4">
      <span class="flex flex-col gap-y-2">
        <Field v-slot="{ field, errorMessage }" name="civilite">
          <label for="civilite">{{ t('components.patientForm.civilite') }}</label>
          <Select
            v-bind="field"
            :label="t('components.patientForm.civilite')"
            :placeholder="t('components.patientForm.select_placeholder')"
            name="civilite"
            :options="civilites"
            id="civilite"
            aria-label="civilité"
            :modelValue="patientDetail?.civilite"
          />
          <Message v-show="errorMessage" class="text-xs text-error" severity="error">
            {{ errorMessage }}
          </Message>
        </Field>
      </span>
      <span class="flex flex-col gap-y-2">
        <Field v-slot="{ field, errorMessage }" name="date_de_naissance">
          <label for="date_de_naissance">{{ t('components.patientForm.date_de_naissance') }}</label>
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
            id="date_de_naissance"
            name="date_de_naissance"
            aria-label="date de naissance"
            :modelValue="date ?? null"
          />
          <Message v-show="errorMessage" class="text-xs text-error" severity="error">
            {{ errorMessage }}
          </Message>
        </Field>
      </span>
    </div>

    <!-- Section nom et prénom -->
    <div class="w-full grid grid-cols-1 md:grid-cols-2 gap-4">
      <span class="flex flex-col gap-y-2">
        <Field v-slot="{ field, errorMessage }" name="nom">
          <label for="nom">{{ t('components.patientForm.lastname') }}</label>
          <InputText
            fluid
            id="nom"
            type="text"
            v-bind="field"
            name="nom"
            aria-label="nom"
            placeholder="Dupont"
            :invalid="!!errorMessage"
          />
          <Message v-show="errorMessage" class="text-xs text-error" severity="error">
            {{ errorMessage }}
          </Message>
        </Field>
      </span>
      <span class="flex flex-col gap-y-2">
        <Field v-slot="{ field, errorMessage }" name="prenom">
          <label for="prenom">{{ t('components.patientForm.firstname') }}</label>
          <InputText
            fluid
            id="prenom"
            type="text"
            v-bind="field"
            name="prenom"
            aria-label="prénom"
            placeholder="Jean"
            :invalid="!!errorMessage"
          />
          <Message class="text-xs text-error" severity="error" v-show="errorMessage">
            {{ errorMessage }}
          </Message>
        </Field>
      </span>
    </div>

    <!-- Section adresse -->
    <div class="w-full flex flex-col gap-y-2">
      <Field v-slot="{ field, errorMessage }" name="adresse">
        <label for="adresse">{{ t('components.patientForm.address') }}</label>
        <Textarea
          fluid
          id="adresse"
          v-bind="field"
          aria-label="adresse"
          placeholder="34 rue Machin"
          name="adresse"
          :invalid="!!errorMessage"
        />
        <Message class="text-xs text-error" severity="error" v-show="errorMessage">
          {{ errorMessage }}
        </Message>
      </Field>
    </div>

    <!-- Section code postal et ville -->
    <div class="w-full grid grid-cols-1 md:grid-cols-2 gap-4">
      <span class="flex flex-col gap-y-2">
        <Field v-slot="{ field, errorMessage }" name="code_postal">
          <label for="code_postal">{{ t('components.patientForm.zip_code') }}</label>
          <InputText
            fluid
            id="code_postal"
            v-bind="field"
            name="code_postal"
            aria-label="code postal"
            placeholder="75000"
            :invalid="!!errorMessage"
          />
          <Message class="text-xs text-error" severity="error" v-show="errorMessage">
            {{ errorMessage }}
          </Message>
        </Field>
      </span>
      <span class="flex flex-col gap-y-2">
        <Field v-slot="{ field, errorMessage }" name="ville">
          <label for="ville">{{ t('components.patientForm.city') }}</label>
          <InputText
            fluid
            id="ville"
            v-bind="field"
            name="ville"
            aria-label="ville"
            placeholder="Paris"
            :invalid="!!errorMessage"
          />
          <Message class="text-xs text-error" severity="error" v-show="errorMessage">
            {{ errorMessage }}
          </Message>
        </Field>
      </span>
    </div>

    <!-- Section téléphone et email -->
    <div class="w-full grid grid-cols-1 md:grid-cols-2 gap-4">
      <span class="flex flex-col gap-y-2">
        <Field v-slot="{ field, errorMessage }" name="telephone">
          <label for="telephone">{{ t('components.patientForm.phone_number') }}</label>
          <InputText
            fluid
            id="telephone"
            v-bind="field"
            name="telephone"
            aria-label="téléphone"
            placeholder="06 00 00 00 00"
            :invalid="!!errorMessage"
          />
          <Message class="text-xs text-error" severity="error" v-show="errorMessage">
            {{ errorMessage }}
          </Message>
        </Field>
      </span>
      <span class="flex flex-col gap-y-2">
        <Field v-slot="{ field, errorMessage }" name="email">
          <label for="email">{{ t('components.patientForm.email') }}</label>
          <InputText
            fluid
            id="email"
            v-bind="field"
            name="email"
            aria-label="email"
            placeholder="jean.dupont@email.fr"
            :invalid="!!errorMessage"
          />
          <Message class="text-xs text-error" severity="error" v-show="errorMessage">
            {{ errorMessage }}
          </Message>
        </Field>
      </span>
    </div>

    <!-- Bouton de soumission -->
    <div class="flex justify-end">
      <Button type="submit" :label="t('components.patientForm.submit')" :loading="isLoading" />
    </div>
  </Form>
</template>
