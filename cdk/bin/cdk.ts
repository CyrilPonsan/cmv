#!/usr/bin/env node
require("dotenv").config()
import * as cdk from 'aws-cdk-lib';
import { CmvInfrastructureStack } from '../lib/cmv-infrastructure-stack';
import { createDefaultServicesConfig, createDatabaseConfigFromEnv } from '../lib/services-config';

const app = new cdk.App();


console.log("HELLO WORLD!");

console.log("REGION",process.env.CDK_DEFAULT_REGION)

const stack = new CmvInfrastructureStack(app, 'CmvInfrastructureStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
  },
});

// Load service and database configurations
const servicesConfig = createDefaultServicesConfig();
const databaseConfig = createDatabaseConfigFromEnv();

// Deploy all CMV services from the configuration array
stack.deployServices(servicesConfig, databaseConfig);
