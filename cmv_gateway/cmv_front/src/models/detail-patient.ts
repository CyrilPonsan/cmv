/**
 * @file detail-patient.ts
 * @description Detail patient model
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

import type Admission from './admission'
import type Document from './document'

export interface CreatePatient {
  prenom: string
  nom: string
  civilite: string
  date_de_naissance: string
  adresse: string
  code_postal: string
  ville: string
  telephone: string
  email?: string
}

export default interface DetailPatient extends CreatePatient {
  id_patient: number
  documents: Document[]
  latest_admission: Admission
}
