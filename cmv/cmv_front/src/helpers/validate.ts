import type ValidationError from '@/models/validation-error'

export function validationErrors(error: any) {
  let validationErrors = Array<ValidationError>()
  for (const item of error.issues) {
    const customError: ValidationError = {
      type: item.path[0] as string,
      message: item.message
    }
    validationErrors = [...validationErrors, customError]
  }

  return validationErrors
}
