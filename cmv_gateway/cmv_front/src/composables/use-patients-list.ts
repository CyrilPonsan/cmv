/**
 * Ce composable gère la logique de l'affichage de la liste des
 * dossiers administratifs de la clinique Montvert.
 * Les données sont chargées en lazy-loading.
 */

import type PatientsListItem from '@/models/patients-list-item'
import { ref, type Ref } from 'vue'
import useHttp from './use-http'
import type ColumnItem from '@/models/column-item'
import { patientsListColumns } from '@/libs/columns/patients-list'

const columns: ColumnItem[] = patientsListColumns

type UsePatientsList = {
  columns: ColumnItem[]
  getPatientsList: (page: number, limit: number, sortField: string, sortOrder: string) => void
  loading: Ref<boolean>
  patientsList: Ref<PatientsListItem[]>
  totalPatients: Ref<number>
}

const usePatientsList = (): UsePatientsList => {
  const http = useHttp()
  const patientsList = ref<PatientsListItem[]>([])
  const totalPatients = ref<number>(0)

  /**
   * Retourne la liste des dossiers administratifs des patients de la clinique
   * Montvert.
   */
  const getPatientsList = (
    page: number = 1,
    limit: number = 10,
    sortField: string = 'nom',
    sortOrder: string = 'asc'
  ) => {
    const applyData = (data: { patients: PatientsListItem[]; total: number }) => {
      console.log({ data })
      patientsList.value = data.patients.map((patient) => ({
        ...patient,
        date_de_naissance: new Date(patient.date_de_naissance).toLocaleDateString()
      }))
      totalPatients.value = data.total
      console.log('result :', patientsList.value)
    }
    http.sendRequest(
      {
        path: `/patients/patients?page=${page}&limit=${limit}&field=${sortField}&order=${sortOrder}`
      },
      applyData
    )
  }

  return { columns, getPatientsList, loading: http.isLoading, patientsList, totalPatients }
}

export default usePatientsList
