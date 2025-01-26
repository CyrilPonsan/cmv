export default interface Admission {
  id_admission: number
  entree_le: string
  ambulatoire: boolean
  sorti_le: string | null
  sortie_prevue_le: string | null
  ref_chambre: number | null
  nom_chambre: string
}
