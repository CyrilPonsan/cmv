/**
 * @file service.ts
 * @description Service model
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

import type Chambre from './chambre'

export interface ServiceListItem {
  id_service: number
  nom: string
}

export default interface Service extends ServiceListItem {
  chambres: Chambre[]
}
