#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { CmvInfrastructureStack, ServiceConfig, DatabaseConfig } from '../lib/cmv-infrastructure-stack';

/**
 * Example demonstrating how to use the CmvInfrastructureStack with service configuration arrays
 */

const app = new cdk.App();

// Create the main infrastructure stack
const stack = new CmvInfrastructureStack(app, 'ExampleStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
  },
});

// Example service configurations array
const servicesConfig: ServiceConfig[] = [
  {
    name: 'gateway',
    hasDatabase: true,
    ports: [80, 443, 8001],
    publicAccess: true,
    dockerImage: 'firizgoude/cmv_gateway:latest',
    environmentVars: {
      NODE_ENV: 'production',
      GATEWAY_DATABASE_URL: 'postgresql://admin:password@localhost:5432/gateway_db'
    }
  },
  {
    name: 'patients',
    hasDatabase: true,
    ports: [8002],
    publicAccess: false,
    dockerImage: 'firizgoude/cmv_patients:latest',
    environmentVars: {
      PATIENTS_DATABASE_URL: 'postgresql://admin:password@localhost:5432/patients_db'
    }
  },
  {
    name: 'chambres',
    hasDatabase: true,
    ports: [8003],
    publicAccess: false,
    dockerImage: 'firizgoude/cmv_chambres:latest',
    environmentVars: {
      CHAMBRES_DATABASE_URL: 'postgresql://admin:password@localhost:5432/chambres_db'
    }
  }
];

// Database configuration (would typically come from environment variables)
const databaseConfig: DatabaseConfig = {
  adminUsername: process.env.DB_ADMIN_USERNAME || 'admin_user',
  adminPassword: process.env.DB_ADMIN_PASSWORD || 'secure_admin_password_123',
  crudUsername: process.env.DB_CRUD_USERNAME || 'crud_user',
  crudPassword: process.env.DB_CRUD_PASSWORD || 'secure_crud_password_456',
  databaseName: process.env.DB_NAME || 'cmv_db'
};

// Deploy all services using the configuration array
stack.deployServices(servicesConfig, databaseConfig);

// Example of accessing deployed service instances
const gatewayInstance = stack.getServiceInstance('gateway');
const patientsInstance = stack.getServiceInstance('patients');
const chambresInstance = stack.getServiceInstance('chambres');

// Add additional outputs for demonstration
if (gatewayInstance) {
  new cdk.CfnOutput(stack, 'GatewayPublicIP', {
    value: gatewayInstance.publicIp || 'N/A',
    description: 'Public IP address of the Gateway service',
  });
}

if (patientsInstance) {
  new cdk.CfnOutput(stack, 'PatientsPrivateIP', {
    value: patientsInstance.privateIp,
    description: 'Private IP address of the Patients service',
  });
}

if (chambresInstance) {
  new cdk.CfnOutput(stack, 'ChambresPrivateIP', {
    value: chambresInstance.privateIp,
    description: 'Private IP address of the Chambres service',
  });
}

// Example of how to add a new service to the configuration
const additionalService: ServiceConfig = {
  name: 'monitoring',
  hasDatabase: false,
  ports: [3000],
  publicAccess: true,
  dockerImage: 'grafana/grafana:latest',
  environmentVars: {
    GF_SECURITY_ADMIN_PASSWORD: 'admin123'
  }
};

// You can deploy additional services by calling deployServices again
// stack.deployServices([additionalService]);

app.synth();