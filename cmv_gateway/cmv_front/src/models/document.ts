/**
 * @file document.ts
 * @description Document model
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

export default interface Document {
  id_document: number
  nom_fichier: string
  type_document: string
  created_at: string
}
