import type PatientsListItem from '@/models/patients-list-item'
import { ref, type Ref } from 'vue'
import useHttp from './use-http'
import type ColumnItem from '@/models/column-item'
import { patientsListColumns } from '@/libs/columns/patients-list'

const columns: ColumnItem[] = patientsListColumns

type UsePatientsList = {
  patientsList: Ref<PatientsListItem[]>
  columns: ColumnItem[]
  getPatientsList: () => void
}

const usePatientList = (): UsePatientsList => {
  const http = useHttp()
  const patientsList = ref<PatientsListItem[]>([])

  const getPatientsList = () => {
    const applyData = (data: PatientsListItem[]) => {
      patientsList.value = data.map((patient) => ({
        ...patient,
        date_de_naissance: new Date(patient.date_de_naissance).toLocaleDateString()
      }))
    }
    http.sendRequest({ path: '/patients/patients' }, applyData)
  }
  return { columns, patientsList, getPatientsList }
}

export default usePatientList
