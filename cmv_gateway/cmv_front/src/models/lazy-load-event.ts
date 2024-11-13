/**
 * @file lazy-load-event.ts
 * @description Lazy load event model
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

export default interface LazyLoadEvent {
  first: number
  rows: number
  sortField: string
  sortOrder: 1 | -1
}
