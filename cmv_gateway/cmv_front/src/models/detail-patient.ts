export default interface DetailPatient {
  id_patient: number
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
