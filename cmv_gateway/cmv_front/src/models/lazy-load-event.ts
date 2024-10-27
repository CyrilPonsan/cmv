/**
 * Cette interface est utilisée pour la pagination
 * avec le composant graphique DataTable de PrimeVue.
 * Elle permet de typer l'évènement émis lorsque
 * l'utilisateur clique sur une colonne pour la trier
 * ou quand il change de page ou le nombre d'éléments
 * affichés par page.
 */

export default interface LazyLoadEvent {
  first: number
  rows: number
  sortField: string
  sortOrder: 1 | -1
}
