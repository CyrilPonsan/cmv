# CMV Infrastructure CDK Project

AWS CDK (TypeScript) project that deploys the CMV application on a multi-instance EC2 architecture. Each microservice gets its own Debian t2.micro instance inside a shared VPC, with optional PostgreSQL and Docker-based deployments.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        AWS VPC                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐│
│  │   Gateway EC2   │  │  Patients EC2   │  │ Chambres EC2 ││
│  │   + Docker      │  │  + PostgreSQL   │  │ + PostgreSQL ││
│  │   Ports 80/443  │  │  Port 8002      │  │ Port 8003    ││
│  └─────────────────┘  └─────────────────┘  └──────────────┘│
│           │                     │                   │       │
│  ┌─────────────────────────────────────────────────────────┐│
│  │              Security Group Rules                      ││
│  │  • Inter-instance communication allowed                ││
│  │  • SSH access (key-based only)                         ││
│  │  • HTTP/HTTPS for gateway only                         ││
│  │  • PostgreSQL ports internal only                      ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### Default Services

| Service   | Ports      | Database   | Public | Docker Image                        |
|-----------|------------|------------|--------|-------------------------------------|
| gateway   | 80, 443, 8001 | Yes     | Yes    | `firizgoude/cmv_gateway:latest`     |
| patients  | 8002       | Yes        | No     | `firizgoude/cmv_patients:latest`    |
| chambres  | 8003       | Yes        | No     | `firizgoude/cmv_chambres:latest`    |

## Project Structure

```
cdk/
├── bin/cdk.ts                        # CDK app entry point
├── lib/
│   ├── cmv-infrastructure-stack.ts   # Main stack (VPC, SG, orchestration)
│   ├── service-instance.ts           # Reusable EC2 instance construct
│   ├── postgresql-setup.ts           # PostgreSQL setup construct
│   └── services-config.ts            # Default service & DB configurations
├── test/                             # Jest + fast-check tests
├── examples/                         # Usage examples
├── deploy.sh                         # Automated deployment script
├── .env.example                      # Environment variable template
└── package.json
```

## Prerequisites

- **Node.js** 18+
- **AWS CLI** configured with valid credentials
- **AWS CDK CLI** (`npm install -g aws-cdk`) — or the script will fall back to `npx cdk`

## Quick Start

### 1. Install dependencies

```bash
cd cdk
npm install
```

### 2. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in **all** required values. See [Environment Variables](#environment-variables) below.

### 3. Deploy

The easiest way is the deployment script, which validates everything before deploying:

```bash
./deploy.sh
```

Or deploy manually:

```bash
npm run build
npx cdk bootstrap   # first time only
npm run deploy
```

## Environment Variables

Copy `.env.example` to `.env` and configure the values. The deployment script validates that all required variables are present before deploying.

### Required Variables

| Variable              | Description                                  | Example               |
|-----------------------|----------------------------------------------|-----------------------|
| `CDK_DEFAULT_ACCOUNT` | 12-digit AWS account ID                     | `123456789012`        |
| `CDK_DEFAULT_REGION`  | AWS region for deployment                    | `eu-west-1`           |
| `DB_ADMIN_USERNAME`   | PostgreSQL admin role username               | `admin_user`          |
| `DB_ADMIN_PASSWORD`   | PostgreSQL admin role password               | *(strong password)*   |
| `DB_CRUD_USERNAME`    | PostgreSQL CRUD role username                | `crud_user`           |
| `DB_CRUD_PASSWORD`    | PostgreSQL CRUD role password                | *(strong password)*   |
| `DB_NAME`             | Default database name                        | `cmv_db`              |
| `SECRET_KEY`          | Application secret key (JWT signing)         | *(random string)*     |

### Optional Variables

| Variable              | Description                                  | Default               |
|-----------------------|----------------------------------------------|-----------------------|
| `ALGORITHM`           | JWT algorithm                                | `HS256`               |
| `ACCESS_MAX_AGE`      | Access token lifetime (minutes)              | `30`                  |
| `REFRESH_MAX_AGE`     | Refresh token lifetime (minutes)             | `1440`                |
| `PATIENTS_SERVICE`    | Patients service URL (used by gateway)       | `http://localhost:8002/api` |
| `CHAMBRES_SERVICE`    | Chambres service URL (used by gateway)       | `http://localhost:8003/api` |
| `AWS_BUCKET_NAME`     | S3 bucket for patients service               | —                     |
| `AWS_ACCESS_KEY_ID`   | AWS access key for S3                        | —                     |
| `AWS_SECRET_ACCESS_KEY`| AWS secret key for S3                       | —                     |
| `AWS_REGION`          | AWS region for S3                            | `eu-west-1`           |

## Available Commands

| Command                | Description                                    |
|------------------------|------------------------------------------------|
| `npm run build`        | Compile TypeScript to JavaScript               |
| `npm run test`         | Run Jest unit tests                            |
| `npm run test:coverage`| Run tests with coverage report                 |
| `npm run synth`        | Synthesize CloudFormation template             |
| `npm run deploy`       | Deploy the stack to AWS                        |
| `npm run diff`         | Compare deployed stack with current state      |
| `npm run destroy`      | Destroy the deployed stack                     |
| `./deploy.sh`          | Full validated deployment (recommended)        |

## Usage Examples

### Adding a New Service

Add an entry to the services array in `lib/services-config.ts`:

```typescript
// Inside createDefaultServicesConfig()
{
  name: 'billing',
  hasDatabase: true,
  ports: [8004],
  publicAccess: false,
  dockerImage: 'your-registry/cmv_billing:latest',
  environmentVars: {
    BILLING_DATABASE_URL: 'postgresql://crud_user:password@localhost:5432/cmv_billing',
  },
}
```

Then redeploy — CDK will create a new EC2 instance automatically.

### Deploying a Service Without a Database

Set `hasDatabase: false` to skip PostgreSQL installation:

```typescript
{
  name: 'notifications',
  hasDatabase: false,
  ports: [8005],
  publicAccess: false,
  dockerImage: 'your-registry/cmv_notifications:latest',
  environmentVars: {
    REDIS_URL: 'redis://your-redis-host:6379',
  },
}
```

### Customizing Database Credentials

Override defaults via environment variables in `.env`:

```bash
DB_ADMIN_USERNAME=my_admin
DB_ADMIN_PASSWORD=super_secret_admin_pw
DB_CRUD_USERNAME=app_user
DB_CRUD_PASSWORD=super_secret_crud_pw
DB_NAME=my_database
```

### Previewing Changes Before Deploying

```bash
npm run diff
```

This shows what CloudFormation changes will be applied without actually deploying.

### Destroying the Stack

```bash
npm run destroy
```

Or with the CDK CLI directly:

```bash
npx cdk destroy
```

## Testing

The project uses **Jest** for unit tests and **fast-check** for property-based testing.

```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run a specific test file
npx jest test/cdk.test.ts
```

## Security Considerations

- **VPC isolation** — All instances are deployed in a shared VPC. Database instances are not publicly accessible.
- **Security groups** — Ingress rules are scoped per service. Only the gateway allows HTTP/HTTPS from the internet.
- **SSH** — Key-based authentication only; no password-based SSH.
- **Database credentials** — Stored in AWS Secrets Manager and SSM Parameter Store. Admin credentials are never exposed in CloudFormation outputs.
- **CRUD role** — Limited to SELECT, INSERT, UPDATE, DELETE. No schema modification privileges.
- **Passwords** — The deploy script warns if placeholder passwords are detected.

## Troubleshooting

### `.env` file not found

```
[ERROR] .env file not found
```

Copy the example and fill in your values:

```bash
cp .env.example .env
```

### Missing required environment variables

```
[ERROR] Required environment variable DB_ADMIN_PASSWORD is not set or empty.
```

Open `.env` and make sure every required variable has a value. See the [Required Variables](#required-variables) table.

### Invalid AWS account ID

```
[ERROR] CDK_DEFAULT_ACCOUNT must be a 12-digit AWS account ID.
```

Your `CDK_DEFAULT_ACCOUNT` must be exactly 12 digits (e.g. `123456789012`). Check for typos or extra spaces.

### Invalid AWS region

```
[ERROR] CDK_DEFAULT_REGION must be a valid AWS region (e.g. eu-west-1).
```

Use a valid region identifier like `eu-west-1`, `us-east-1`, etc.

### CDK bootstrap required

```
Has the environment been bootstrapped?
```

Run bootstrap once per account/region:

```bash
npx cdk bootstrap aws://ACCOUNT_ID/REGION
```

### Configuration validation errors

The CDK stack validates all service configurations at synth time. Common issues:

| Error | Cause | Fix |
|-------|-------|-----|
| `Service name is required` | Empty `name` field in ServiceConfig | Provide a non-empty service name |
| `Service name must be a string` | Wrong type for `name` | Ensure `name` is a string |
| `Ports must be a non-empty array` | Missing or empty `ports` | Add at least one port number |
| `Port must be between 1 and 65535` | Port out of range | Use a valid port number |
| `hasDatabase must be a boolean` | Wrong type for `hasDatabase` | Use `true` or `false` |
| `publicAccess must be a boolean` | Wrong type for `publicAccess` | Use `true` or `false` |
| `Admin username is required` | Empty DB_ADMIN_USERNAME | Set the variable in `.env` |
| `Admin password is required` | Empty DB_ADMIN_PASSWORD | Set the variable in `.env` |

### TypeScript build errors

```bash
npm run build
```

If the build fails, check for syntax errors in any files you modified. The `tsconfig.json` uses strict mode.

### Stack deployment fails / rollback

Check the CloudFormation console for detailed error events:

```bash
aws cloudformation describe-stack-events \
  --stack-name CmvInfrastructureStack \
  --region "$CDK_DEFAULT_REGION" \
  --query 'StackEvents[?ResourceStatus==`CREATE_FAILED`]'
```

Common causes:
- **Resource limits** — Your account may have EC2 or VPC limits. Request a limit increase via the AWS console.
- **IAM permissions** — The deploying user/role needs permissions to create EC2, VPC, Security Groups, Secrets Manager, and SSM resources.
- **AMI not available** — The Debian AMI may not be available in your chosen region. Check AMI availability.

### SSH connection issues

Make sure:
1. The key pair was created during deployment (check the CDK outputs).
2. Your security group allows inbound SSH (port 22) from your IP.
3. You're using the correct private key file and the `admin` user (Debian default).

```bash
ssh -i your-key.pem admin@<instance-public-ip>
```
