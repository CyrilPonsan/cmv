/**
 * @file patients-list-item.ts
 * @description Patients list item model
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

export default interface PatientsListItem {
  id_patient: number
  prenom: string
  nom: string
  date_de_naissance: string
  telephone: string
  email?: string
}
