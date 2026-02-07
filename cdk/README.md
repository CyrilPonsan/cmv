# CMV Infrastructure CDK Project

This CDK TypeScript project deploys the infrastructure for the CMV application using AWS CDK.

## Architecture

The project creates a multi-instance architecture where each microservice runs on its own EC2 instance:
- Gateway service (with frontend)
- Patients service (with PostgreSQL)
- Chambres service (with PostgreSQL)

## Project Structure

- `bin/cdk.ts` - CDK app entry point
- `lib/cmv-infrastructure-stack.ts` - Main infrastructure stack
- `test/` - Test files using Jest and fast-check

## Prerequisites

- Node.js 18+ 
- AWS CLI configured
- AWS CDK CLI installed globally

## Installation

```bash
npm install
```

## Available Commands

- `npm run build` - Compile TypeScript to JavaScript
- `npm run watch` - Watch for changes and compile
- `npm run test` - Run Jest unit tests
- `npm run test:coverage` - Run tests with coverage report
- `npm run synth` - Synthesize CloudFormation template
- `npm run deploy` - Deploy the stack to AWS
- `npm run diff` - Compare deployed stack with current state
- `npm run destroy` - Destroy the deployed stack

## Configuration

The stack uses TypeScript interfaces to define service configurations:

- `ServiceConfig` - Defines individual service properties
- `DatabaseConfig` - PostgreSQL database configuration
- `EnvironmentConfig` - Environment variables and secrets

## Testing

The project uses:
- **Jest** for unit testing
- **fast-check** for property-based testing
- **AWS CDK assertions** for infrastructure testing

Run tests with:
```bash
npm test
```

## Deployment

1. Configure your AWS credentials
2. Bootstrap CDK (first time only):
   ```bash
   npx cdk bootstrap
   ```
3. Deploy the stack:
   ```bash
   npm run deploy
   ```

## Security

- All instances are deployed in a private VPC
- Security groups control network access
- Database instances are not accessible from the internet
- SSH access uses key-based authentication only
