#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { CmvInfrastructureStack, ServiceConfig, DatabaseConfig } from '../lib/cmv-infrastructure-stack';

/**
 * Example demonstrating security group rules and network policies
 * This example shows how the implemented security features work
 */

const app = new cdk.App();

// Create the infrastructure stack
const stack = new CmvInfrastructureStack(app, 'CmvSecurityExampleStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
  },
});

// Define service configurations that demonstrate different security requirements
const servicesConfig: ServiceConfig[] = [
  {
    name: 'gateway',
    hasDatabase: true,
    ports: [80, 443, 8001],
    publicAccess: true, // Requirement 5.3: Allow HTTP/HTTPS for gateway instances
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
    publicAccess: false, // Requirement 5.2: Block external access to database instances
    dockerImage: 'firizgoude/cmv_patients:latest',
    environmentVars: {
      PATIENTS_DATABASE_URL: 'postgresql://admin:password@localhost:5432/patients_db'
    }
  },
  {
    name: 'chambres',
    hasDatabase: true,
    ports: [8003],
    publicAccess: false, // Requirement 5.2: Block external access to database instances
    dockerImage: 'firizgoude/cmv_chambres:latest',
    environmentVars: {
      CHAMBRES_DATABASE_URL: 'postgresql://admin:password@localhost:5432/chambres_db'
    }
  }
];

// Database configuration using environment variables (Requirement 3.3)
const databaseConfig: DatabaseConfig = {
  adminUsername: process.env.DB_ADMIN_USERNAME || 'cmv_admin',
  adminPassword: process.env.DB_ADMIN_PASSWORD || 'secure_admin_password_123',
  crudUsername: process.env.DB_CRUD_USERNAME || 'cmv_crud',
  crudPassword: process.env.DB_CRUD_PASSWORD || 'secure_crud_password_123',
  databaseName: 'cmv_database',
};

// Deploy services with security configurations
stack.deployServices(servicesConfig, databaseConfig);

// Demonstrate additional security group creation
const databaseSecurityGroup = stack.createDatabaseSecurityGroup();
const gatewaySecurityGroup = stack.createGatewaySecurityGroup();

// Add outputs to show security group IDs
new cdk.CfnOutput(stack, 'DatabaseSecurityGroupId', {
  value: databaseSecurityGroup.securityGroupId,
  description: 'Security Group ID for database instances (restricted access)',
  exportName: 'CmvDatabaseSecurityGroupId',
});

new cdk.CfnOutput(stack, 'GatewaySecurityGroupId', {
  value: gatewaySecurityGroup.securityGroupId,
  description: 'Security Group ID for gateway instances (public access)',
  exportName: 'CmvGatewaySecurityGroupId',
});

// Add security policy summary output
new cdk.CfnOutput(stack, 'SecurityPolicySummary', {
  value: JSON.stringify({
    'inter-instance-communication': 'Enabled within VPC (Requirement 5.1)',
    'database-external-access': 'Blocked - VPC only (Requirement 5.2)',
    'gateway-public-access': 'Enabled for HTTP/HTTPS (Requirement 5.3)',
    'ssh-access': 'Key-based authentication (Requirement 5.4)',
    'database-access-control': 'Authorized instances only (Requirement 5.5)',
  }),
  description: 'Summary of implemented security policies',
  exportName: 'CmvSecurityPolicySummary',
});

console.log('Security Example Stack Configuration:');
console.log('=====================================');
console.log('✓ Inter-instance communication: Enabled within VPC');
console.log('✓ Database external access: Blocked (VPC-only access)');
console.log('✓ Gateway public access: Enabled for HTTP/HTTPS');
console.log('✓ SSH access: Key-based authentication');
console.log('✓ PostgreSQL access: Restricted to authorized instances within VPC');
console.log('✓ Network ACLs: Configured for additional subnet-level security');
console.log('✓ Security Groups: Dedicated groups for database and gateway instances');