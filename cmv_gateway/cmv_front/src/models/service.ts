import type Chambre from './chambre'

export default interface Service {
  id: number
  nom: string
  chambres: Chambre[]
}
