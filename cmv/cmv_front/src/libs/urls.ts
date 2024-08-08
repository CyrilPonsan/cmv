const VITE_BACKEND = import.meta.env.VITE_BACKEND

console.log({ VITE_BACKEND })

export const AUTH = VITE_BACKEND || '/api'
