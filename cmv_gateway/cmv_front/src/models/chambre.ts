/**
 * @file chambre.ts
 * @description Chambre model
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

export default interface Chambre {
  id: number
  numero: number
  status: string
  last_freed: string
  last_occuped: string
  last_cleanup: string
}
