/**
 * Interface pour type l'état des valeurs
 * de la pagination.
 */

export default interface LazyState {
  first: number
  rows: number
  sortField: string
  sortOrder: 1 | -1
}
