/**
 * @file chambre.ts
 * @description Chambre model
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

interface Patient {
  id_patient: number
  ref_patient: number
  full_name: string
}

interface Reservation {
  id_reservation: number
  entree_prevue: string
  sortie_prevue: string
  patient: Patient
}

export default interface Chambre {
  id_chambre: number
  numero: number
  status: string
  dernier_nettoyage: string
  reservation: Reservation[]
}
