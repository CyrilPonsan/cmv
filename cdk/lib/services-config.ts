import { ServiceConfig, DatabaseConfig, EnvironmentConfig } from './cmv-infrastructure-stack';

/**
 * Default service configurations for the CMV application.
 * Each entry in this array drives the creation of one EC2 instance.
 *
 * Requirements: 1.1 (configuration-driven instance creation)
 * Requirements: 1.4 (conditional PostgreSQL installation via hasDatabase)
 */

/**
 * Creates the default CMV service configuration array.
 * Database URLs use placeholder credentials — actual values are injected
 * via environment variables and AWS Secrets Manager at deploy time.
 */
export function createDefaultServicesConfig(): ServiceConfig[] {
  return [
    {
      name: 'gateway',
      hasDatabase: true,
      ports: [80, 443, 8001],
      publicAccess: true,
      dockerImage: 'firizgoude/cmv_gateway:latest',
      environmentVars: {
        NODE_ENV: 'production',
        GATEWAY_DATABASE_URL: 'postgresql://crud_user:password@localhost:5432/cmv_gateway',
        SECRET_KEY: process.env.SECRET_KEY || 'change-me',
        ALGORITHM: process.env.ALGORITHM || 'HS256',
        ACCESS_MAX_AGE: process.env.ACCESS_MAX_AGE || '30',
        REFRESH_MAX_AGE: process.env.REFRESH_MAX_AGE || '1440',
        PATIENTS_SERVICE: process.env.PATIENTS_SERVICE || 'http://localhost:8002/api',
        CHAMBRES_SERVICE: process.env.CHAMBRES_SERVICE || 'http://localhost:8003/api',
      },
    },
    {
      name: 'patients',
      hasDatabase: true,
      ports: [8002],
      publicAccess: false,
      dockerImage: 'firizgoude/cmv_patients:latest',
      environmentVars: {
        PATIENTS_DATABASE_URL: 'postgresql://crud_user:password@localhost:5432/cmv_patients',
        AWS_BUCKET_NAME: process.env.AWS_BUCKET_NAME || '',
        AWS_ACCESS_KEY_ID: process.env.AWS_ACCESS_KEY_ID || '',
        AWS_SECRET_ACCESS_KEY: process.env.AWS_SECRET_ACCESS_KEY || '',
        AWS_REGION: process.env.AWS_REGION || 'eu-west-1',
      },
    },
    {
      name: 'chambres',
      hasDatabase: true,
      ports: [8003],
      publicAccess: false,
      dockerImage: 'firizgoude/cmv_chambres:latest',
      environmentVars: {
        CHAMBRES_DATABASE_URL: 'postgresql://crud_user:password@localhost:5432/cmv_chambres',
        SECRET_KEY: process.env.SECRET_KEY || 'change-me',
        ALGORITHM: process.env.ALGORITHM || 'HS256',
      },
    },
  ];
}

/**
 * Creates a DatabaseConfig from environment variables with sensible defaults.
 * In production, credentials should come from environment variables or a secrets manager.
 */
export function createDatabaseConfigFromEnv(): DatabaseConfig {
  return {
    adminUsername: process.env.DB_ADMIN_USERNAME || 'admin_user',
    adminPassword: process.env.DB_ADMIN_PASSWORD || 'secure_admin_password_123',
    crudUsername: process.env.DB_CRUD_USERNAME || 'crud_user',
    crudPassword: process.env.DB_CRUD_PASSWORD || 'secure_crud_password_456',
    databaseName: process.env.DB_NAME || 'cmv_db',
  };
}

/**
 * Environment variable template documenting all variables consumed by the CDK stack.
 * Use this as a reference when setting up .env files or CI/CD secrets.
 */
export const ENVIRONMENT_TEMPLATE: Record<string, string> = {
  // Database Admin Credentials
  DB_ADMIN_USERNAME: '',
  DB_ADMIN_PASSWORD: '',

  // Database CRUD User Credentials
  DB_CRUD_USERNAME: '',
  DB_CRUD_PASSWORD: '',

  // Database name
  DB_NAME: '',

  // AWS Configuration
  AWS_REGION: '',
  CDK_DEFAULT_ACCOUNT: '',
  CDK_DEFAULT_REGION: '',

  // Application Secrets
  SECRET_KEY: '',
  ALGORITHM: '',

  // Token Configuration
  ACCESS_MAX_AGE: '',
  REFRESH_MAX_AGE: '',

  // Inter-service URLs (used by gateway)
  PATIENTS_SERVICE: '',
  CHAMBRES_SERVICE: '',

  // AWS S3 Configuration (patients service)
  AWS_BUCKET_NAME: '',
  AWS_ACCESS_KEY_ID: '',
  AWS_SECRET_ACCESS_KEY: '',
};
