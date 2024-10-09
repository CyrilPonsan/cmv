export interface ValidationErrorWithType<T> {
  type: string;
  message: string;
  status?: number;
  data?: T;
}

export default interface ValidationError {
  type: string;
  message: string;
  status?: number;
  data?: any;
}
