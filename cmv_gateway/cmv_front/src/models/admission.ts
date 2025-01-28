/**
 * Interface représentant une admission d'un patient
 */
export default interface Admission {
  /** Identifiant unique de l'admission */
  id_admission: number
  /** Date d'entrée du patient */
  entree_le: string
  /** Indique si l'admission est en ambulatoire */
  ambulatoire: boolean
  /** Date de sortie effective du patient (null si pas encore sorti) */
  sorti_le: string | null
  /** Date de sortie prévue du patient (null si non définie) */
  sortie_prevue_le: string | null
  /** Référence de la chambre attribuée */
  ref_chambre: string
  /** Nom de la chambre attribuée (null si non défini) */
  nom_chambre: string | null
}
