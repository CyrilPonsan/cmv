<script setup lang="ts">
/**
 * @file ListPatients.vue
 * @description Component for displaying the list of patients
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

// Import des composants et utilitaires nécessaires
import { useI18n } from 'vue-i18n'
import Column from 'primevue/column'
import InputText from 'primevue/inputtext'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import Button from 'primevue/button'
import DeletePatientDialog from '@/components/DeletePatientDialog.vue'
import type { DataTableFilterMeta } from 'primevue/datatable'
import { patientsListColumns } from '@/libs/columns/patients-list'
import useListPatients from '@/composables/useListPatients'
import { onMounted, ref } from 'vue'
import DataTable from 'primevue/datatable'

// Définition des props et des types
// Colonnes à afficher dans le tableau
const columns = patientsListColumns
// Filtres pour le tableau
const filters = ref<DataTableFilterMeta>({})

// Composables
// Récupération des fonctions de traduction et de formatage de dates
const { t, d } = useI18n()
// Récupération des fonctionnalités de gestion de la liste des patients
const {
  handlePage, // Gestion de la pagination
  handleSort, // Gestion du tri
  search, // Terme de recherche
  onResetFilter, // Réinitialisation des filtres
  result: patientsList, // Liste des patients
  totalRecords, // Nombre total d'enregistrements
  lazyState, // Mode lazy-loadin
  loading, // État de chargement
  isLoading, // État de chargement des requêtes HTTP
  getData, // Fonction de récupération des données
  showDeleteDialog, // Affichage de la boîte de dialogue de suppression
  onCancel, // Annulation de la suppression
  onConfirm, // Confirmation de la suppression
  selectedPatient, // Patient sélectionné pour la suppression
  dialogVisible // Visibilité de la boîte de dialogue
} = useListPatients()

// Chargement initial des données au montage du composant
onMounted(() => getData())
</script>

<template>
  <!-- Table principale des patients avec pagination et tri -->
  <DataTable
    v-model:filters="filters"
    :value="patientsList"
    :lazy="true"
    :total-records="totalRecords"
    :rows-per-page-options="[5, 10, 20, 50]"
    v-model:first="lazyState.first"
    v-model:rows="lazyState.rows"
    v-model:sort-field="lazyState.sortField"
    v-model:sort-order="lazyState.sortOrder"
    data-key="id_patient"
    :striped-rows="true"
    :paginator="true"
    table-style="min-width: 50rem"
    paginator-template="RowsPerPageDropdown FirstPageLink PrevPageLink CurrentPageReport NextPageLink LastPageLink"
    :current-page-report-template="`${lazyState.first + 1} ${t('pagination.to')} ${lazyState.first + lazyState.rows} ${t('pagination.from')} ${totalRecords}`"
    class="shadow-md min-w-full"
    @page="handlePage"
    @sort="handleSort"
  >
    <!-- En-tête avec barre de recherche -->
    <template #header>
      <div class="flex items-center gap-x-4 rounded-tl-lg rounded-tr-lg">
        <div class="w-full flex items-center justify-between gap-x-4">
          <!-- Bouton d'ajout d'un nouveau patient -->
          <Button as="router-link" to="/add-patient" icon="pi pi-plus" label="Ajouter un patient" />
          <!-- Barre de recherche -->
          <IconField class="flex items-center gap-x-4">
            <!-- Icône de recherche -->
            <InputIcon>
              <i class="pi pi-search opacity-20" />
            </InputIcon>
            <!-- Champ de recherche -->
            <InputText
              class="focus:!ring-0 focus:!ring-offset-0"
              v-model="search"
              :placeholder="t('patients.home.placeholder.search')"
            />
            <!-- Icônes d'état (effacer/chargement) -->
            <InputIcon>
              <i
                v-if="search && !loading"
                class="pi pi-times-circle cursor-pointer"
                @click="onResetFilter"
              />
              <i
                v-else-if="loading && search"
                class="pi pi-spinner animate-spin text-primary-500"
              />
            </InputIcon>
          </IconField>
        </div>
      </div>
    </template>

    <!-- Information sur le nombre total de patients -->
    <template #paginatorstart>
      <span class="flex items-center gap-x-2 font-bold">
        {{ t('patients.home.total_patients', totalRecords) }}
      </span>
    </template>

    <!-- Colonnes dynamiques générées à partir de la configuration -->
    <Column
      v-for="col of columns"
      :key="col.field"
      :field="col.field"
      :header="t(`columns.patientsList.${col.header}`)"
      :sortable="col.sortable"
    >
      <!-- Rendu personnalisé pour chaque cellule -->
      <template #body="slotProps">
        <div :key="slotProps.data.id_patient">
          <!-- Formatage spécial pour la date de naissance -->
          <template v-if="col.field === 'date_de_naissance'">
            {{ d(new Date(slotProps.data[col.field]), 'short') }}
          </template>
          <!-- Rendu standard pour les autres champs -->
          <template v-else>
            <span :class="{ capitalize: col.field !== 'email' }">
              {{ slotProps.data[col.field] }}
            </span>
          </template>
        </div>
      </template>
    </Column>

    <!-- Colonne des actions (détails et suppression) -->
    <Column :header="t('columns.patientsList.actions')" :exportable="false">
      <template #body="slotProps">
        <span class="flex items-center gap-x-4">
          <!-- Bouton de navigation vers les détails -->
          <Button
            as="router-link"
            :to="`/patient/${slotProps.data.id_patient}`"
            icon="pi pi-info-circle"
            rounded
            variant="outlined"
            text
            aria-label="Détails du dossier administratif"
            v-tooltip.bottom="t('patients.home.tooltip.navigate')"
          />
          <!-- Bouton de suppression -->
          <Button
            :disabled="isLoading"
            :icon="isLoading ? 'pi pi-spinner animate-spin text-primary-500' : 'pi pi-trash'"
            severity="danger"
            rounded
            variant="outlined"
            text
            aria-label="Supprimer"
            v-tooltip.bottom="t('patients.home.tooltip.delete')"
            @click="showDeleteDialog(slotProps.data)"
          />
        </span>
      </template>
    </Column>

    <!-- Message affiché lorsque le tableau est vide -->
    <template #empty>
      <div class="text-center p-4">
        <i class="pi pi-info-circle text-warn text-xl mb-2"></i>
        <p>{{ t('patients.home.placeholder.empty') }}</p>
      </div>
    </template>
  </DataTable>

  <!-- Dialogue de confirmation de suppression -->
  <DeletePatientDialog
    v-if="selectedPatient"
    :patient="selectedPatient"
    :visible="dialogVisible"
    @confirm="onConfirm"
    @cancel="onCancel"
  />
</template>
