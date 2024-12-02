<script setup lang="ts">
import { toTypedSchema } from '@vee-validate/zod'
import { Button, DatePicker, InputText, Message, Select, Textarea } from 'primevue'
import { Field, Form } from 'vee-validate'

const props = defineProps<{
  civilite: string
  civilites: string[]
  date_de_naissance: Date | Date[] | (Date | null)[] | null | undefined
  onSubmit: (data: Record<string, unknown>) => void
  schema: ReturnType<typeof toTypedSchema>
  isLoading: boolean
  updateCivilite: (value: string) => void
  updateDateDeNaissance: (value: Date | Date[] | (Date | null)[] | null | undefined) => void
}>()

const handleSubmit = (values: Record<string, unknown>) => {
  props.onSubmit(values)
}
</script>

<template>
  <Form
    class="flex flex-col gap-y-8 w-5/6 lg:w-[42rem]"
    :validation-schema="schema"
    @submit="handleSubmit"
  >
    <div class="w-full grid grid-cols-1 md:grid-cols-2 gap-4">
      <span class="flex flex-col gap-y-2">
        <label for="civilite">Civilité</label>
        <Select
          :value="civilite"
          label="civilite"
          placeholder="Sélectionner une civilité"
          name="civilite"
          :options="civilites"
          @update:modelValue="updateCivilite"
        />
      </span>
      <span class="flex flex-col gap-y-2">
        <label for="date_de_naissance">Date de naissance</label>
        <DatePicker
          showIcon
          fluid
          selectionMode="single"
          view="date"
          :showButtonBar="true"
          yearRange="1900:2024"
          locale="fr"
          iconDisplay="input"
          :value="props.date_de_naissance"
          :defaultDate="props.date_de_naissance"
          @update:modelValue="updateDateDeNaissance"
        />
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
      <Button type="submit" label="Enregistrer" :loading="isLoading" />
    </div>
  </Form>
</template>
