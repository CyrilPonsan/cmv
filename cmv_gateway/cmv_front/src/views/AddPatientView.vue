<script setup lang="ts">
import PageHeader from '@/components/PageHeader.vue'
import { regexGeneric } from '@/libs/regex'
import { toTypedSchema } from '@vee-validate/zod'
import Button from 'primevue/button'
import DatePicker from 'primevue/datepicker'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import Select from 'primevue/select'
import Textarea from 'primevue/textarea'
import { Field, Form } from 'vee-validate'
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { z } from 'zod'

/**
 * @file AddPatientView.vue
 * @description Add patient view
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

const { t } = useI18n()
const civilites = ref(['Monsieur', 'Madame', 'Mademoiselle'])

const newPatientSchema = toTypedSchema(
  z.object({
    prenom: z
      .string({ required_error: t('error.no_firstname') })
      .regex(regexGeneric, { message: t('error.not_valid_firstname') }),
    nom: z
      .string({ required_error: t('error.no_lastname') })
      .regex(regexGeneric, { message: t('error.not_valid_lastname') }),
    adresse: z.string({ required_error: t('error.no_address') }).regex(regexGeneric, {
      message: t('error.not_valid_address')
    }),
    code_postal: z.string({ required_error: t('error.no_zipcode') }).regex(regexGeneric, {
      message: t('error.not_valid_zipcode')
    }),
    ville: z.string({ required_error: t('error.no_city') }).regex(regexGeneric, {
      message: t('error.not_valid_city')
    }),
    telephone: z.string({ required_error: t('error.no_phone') }).regex(regexGeneric, {
      message: t('error.not_valid_phone')
    }),
    email: z
      .string({ required_error: t('error.no_email') })
      .email({ message: t('error.not_valid_email') })
  })
)
</script>

<template>
  <div class="flex flex-col gap-y-8">
    <section>
      <PageHeader :title="t('patients.add.title')" :description="t('patients.add.description')" />
    </section>
    <section class="grid grid-cols-1 gap-x-4 lg:grid-cols-3">
      <Form class="flex flex-col gap-y-8" :validation-schema="newPatientSchema">
        <div class="grid grid-cols-2 gap-x-4">
          <span class="flex flex-col gap-y-2">
            <label for="civilite">Civilité</label>
            <Select
              label="civilite"
              placeholder="Sélectionner une civilité"
              name="civilite"
              :options="civilites"
            />
          </span>
          <span class="flex flex-col gap-y-2">
            <label for="date_de_naissance">Date de naissance</label>
            <DatePicker showIcon fluid iconDisplay="input" />
          </span>
        </div>
        <div class="grid grid-cols-2 gap-x-4">
          <span class="flex flex-col gap-y-2">
            <Field v-slot="{ field, errorMessage }" name="nom">
              <Message v-if="errorMessage" class="text-xs text-error" severity="error">
                {{ errorMessage }}
              </Message>
              <label v-else for="nom">Nom</label>
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
            </Field>
          </span>
          <span class="flex flex-col gap-y-2">
            <Field v-slot="{ field, errorMessage }" name="prenom">
              <label for="prenom">Prénom</label>
              <Message class="text-xs text-error" severity="error" v-show="errorMessage">
                {{ errorMessage }}
              </Message>
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
            </Field>
          </span>
        </div>
        <div class="flex flex-col gap-y-2">
          <label for="adresse">Adresse</label>
          <Textarea name="adresse" />
        </div>
        <div class="grid grid-cols-2 gap-x-4">
          <span class="flex flex-col gap-y-2">
            <label for="code_postal">Code postal</label>
            <InputText name="code_postal" />
          </span>
          <span class="flex flex-col gap-y-2">
            <label for="ville">Ville</label>
            <InputText name="ville" />
          </span>
        </div>
        <div class="grid grid-cols-2 gap-x-4">
          <span class="flex flex-col gap-y-2">
            <label for="telephone">Téléphone</label>
            <InputText name="telephone" />
          </span>
          <span class="flex flex-col gap-y-2">
            <label for="email">Email</label>
            <InputText name="email" />
          </span>
        </div>
        <div class="flex justify-end">
          <Button type="submit" label="Enregistrer" />
        </div>
      </Form>
    </section>
  </div>
</template>
