/**
 * @file service.ts
 * @description Service model
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

import type Chambre from './chambre'

export default interface Service {
  id_service: number
  nom: string
  chambres: Chambre[]
}
