#!/usr/bin/env node
import * as dotenv from 'dotenv';
import * as path from 'path';
import * as cdk from 'aws-cdk-lib';
import { CdkEc2Stack } from '../lib/cdk-ec2-stack';

dotenv.config({ path: path.resolve(__dirname, '../.env') });

const requiredVars = ['CDK_DEFAULT_ACCOUNT', 'CDK_DEFAULT_REGION', 'DOMAIN'];
for (const varName of requiredVars) {
  if (!process.env[varName]) {
    throw new Error(`Variable d'environnement manquante : ${varName}`);
  }
}

const app = new cdk.App();
new CdkEc2Stack(app, 'CdkEc2Stack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
  },
});
