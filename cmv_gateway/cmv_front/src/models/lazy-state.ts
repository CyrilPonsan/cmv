/**
 * @file lazy-state.ts
 * @description Lazy state model
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

export default interface LazyState {
  first: number
  rows: number
  sortField: string
  sortOrder: 1 | -1
}
