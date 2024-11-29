<script setup lang="ts">
import PageHeader from '@/components/PageHeader.vue'
import useHttp from '@/composables/useHttp'
import { regexGeneric } from '@/libs/regex'
import { toTypedSchema } from '@vee-validate/zod'
import Button from 'primevue/button'
import DatePicker from 'primevue/datepicker'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import Select from 'primevue/select'
import Textarea from 'primevue/textarea'
import { Field, Form, type GenericObject, type SubmissionHandler } from 'vee-validate'
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { z } from 'zod'

/**
 * @file AddPatientView.vue
 * @description Add patient view
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

const { t } = useI18n()
const civilites = ref(['Monsieur', 'Madame', 'Mademoiselle', 'Autre', 'Roberto'])
const civilite = ref('Autre')
const date_de_naissance = ref<Date | null>(null)
const { sendRequest } = useHttp()

//console.log(date_de_naissance.value)

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

const handleSubmit: SubmissionHandler<GenericObject> = (values) => {
  const body = {
    ...values,
    civilite: civilite.value,
    date_de_naissance: date_de_naissance.value
  }

  const applyData = (data: any) => {
    console.log(data)
  }

  sendRequest({ path: '/patients/patients', method: 'POST', data: body }, applyData)
  applyData(body)
}
</script>

<template>
  <section class="mb-16">
    <PageHeader :title="t('patients.add.title')" :description="t('patients.add.description')" />
  </section>
  <div class="grid grid-cols-1 2xl:grid-cols-2 gap-16 mb-16">
    <section class="flex flex-col items-center gap-y-8">
      <Form
        class="flex flex-col gap-y-8 w-5/6 lg:w-[42rem]"
        :validation-schema="newPatientSchema"
        @submit="handleSubmit"
      >
        <div class="w-full grid grid-cols-1 md:grid-cols-2 gap-4">
          <span class="flex flex-col gap-y-2">
            <label for="civilite">Civilité</label>
            <Select
              v-model="civilite"
              label="civilite"
              placeholder="Sélectionner une civilité"
              name="civilite"
              :options="civilites"
            />
          </span>
          <span class="flex flex-col gap-y-2">
            <label for="date_de_naissance">Date de naissance</label>
            <DatePicker showIcon fluid iconDisplay="input" v-model="date_de_naissance" />
          </span>
        </div>
        <div class="w-full grid grid-cols-1 md:grid-cols-2 gap-4">
          <span class="flex flex-col gap-y-2">
            <Field v-slot="{ field, errorMessage }" name="nom">
              <label for="nom">Nom</label>
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
              <label for="prenom">Prénom</label>
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
        <div class="w-full flex flex-col gap-y-2">
          <Field v-slot="{ field, errorMessage }" name="adresse">
            <label for="adresse">Adresse</label>
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
        <div class="w-full grid grid-cols-1 md:grid-cols-2 gap-4">
          <span class="flex flex-col gap-y-2">
            <Field v-slot="{ field, errorMessage }" name="code_postal">
              <label for="code_postal">Code postal</label>
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
              <label for="ville">Ville</label>
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
        <div class="w-full grid grid-cols-1 md:grid-cols-2 gap-4">
          <span class="flex flex-col gap-y-2">
            <Field v-slot="{ field, errorMessage }" name="telephone">
              <label for="telephone">Téléphone</label>
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
              <label for="email">Email</label>
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
        <div class="flex justify-end">
          <Button type="submit" label="Enregistrer" />
        </div>
      </Form>
    </section>

    <section class="flex justify-center items-center">
      <div class="w-5/6 p-4 flex flex-col border border-neutral-200/50 rounded-lg">
        <h3 class="text-primary-500 font-bold mb-3">
          Engagement de confidentialité et protection des données
        </h3>

        <div class="surface-100 p-3 border-round mb-3">
          <h4 class="text-primary-500 font-bold mt-0">Contexte Légal</h4>
          <p>
            Conformément au Règlement Général sur la Protection des Données (RGPD), vous êtes tenu
            de respecter les principes suivants lors de la collecte et du traitement des données
            personnelles :
          </p>

          <ul class="pl-4">
            <li>- Collecter uniquement les données strictement nécessaires</li>
            <li>- Informer la personne concernée de l'usage de ses données</li>
            <li>- Obtenir son consentement explicite</li>
            <li>- Garantir la confidentialité et la sécurité des informations</li>
          </ul>
        </div>

        <div class="surface-100 p-3 border-round mb-3">
          <h4 class="text-primary-500 font-bold mt-0">Vos Responsabilités</h4>
          <p>En tant qu'employé, vous devez :</p>
          <ol class="pl-4">
            <li>- Expliquer au patient l'usage de ses données</li>
            <li>- Recueillir son consentement</li>
            <li>- Ne pas partager les informations en dehors du cadre professionnel</li>
            <li>- Détruire les documents physiques après numérisation</li>
            <li>- Signaler toute suspicion de violation de données</li>
          </ol>
        </div>
      </div>
    </section>
  </div>
</template>
