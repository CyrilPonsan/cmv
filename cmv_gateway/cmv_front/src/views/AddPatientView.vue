<script setup lang="ts">
import CreatePatientForm from '@/components/CreatePatientForm.vue'
import PageHeader from '@/components/PageHeader.vue'
import useHttp from '@/composables/useHttp'
import { regexGeneric } from '@/libs/regex'
import { toTypedSchema } from '@vee-validate/zod'
import { useToast } from 'primevue/usetoast'
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { z } from 'zod'

/**
 * @file AddPatientView.vue
 * @description Add patient view
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

const { t } = useI18n()
const civilite = ref('Autre')
const date_de_naissance = ref<Date | Date[] | (Date | null)[] | null | undefined>(
  new Date(1974, 3, 14)
)
const { error, isLoading, sendRequest } = useHttp()
const toast = useToast()

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

watch(error, (value) => {
  if (value && value.length > 0) {
    toast.add({
      summary: 'Erreur',
      detail: value,
      severity: 'error',
      closable: true,
      life: 5000
    })
  }
})
</script>

<template>
  <section class="mb-16">
    <PageHeader :title="t('patients.add.title')" :description="t('patients.add.description')" />
  </section>
  <div class="grid grid-cols-1 2xl:grid-cols-2 gap-16 mb-16">
    <section class="flex justify-center items-start">
      <CreatePatientForm
        :schema="newPatientSchema"
        :civilite="civilite"
        :date_de_naissance="date_de_naissance"
        @update:date_de_naissance="date_de_naissance = $event"
      />
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
