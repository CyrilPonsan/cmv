/**
 * @file progress-bar.ts
 * @description Progress bar setup
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

import NProgress from 'nprogress'

export default (router: any) => {
  router.beforeEach((to: any, from: any, next: any) => {
    NProgress.start()
    next()
  })

  router.afterEach(NProgress.done)
}
