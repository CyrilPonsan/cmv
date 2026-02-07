# Design Document - AWS CDK Infrastructure

## Overview

Ce document décrit la conception d'une infrastructure AWS CDK en TypeScript pour déployer l'application CMV sur une architecture multi-instances. Le système permettra de déployer des instances EC2 configurables avec PostgreSQL optionnel, dans un environnement sécurisé et évolutif.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        AWS VPC                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   Gateway EC2   │  │  Patients EC2   │  │ Chambres EC2 │ │
│  │   + Frontend    │  │   + PostgreSQL  │  │ + PostgreSQL │ │
│  │   Port: 80/443  │  │   Port: 8002    │  │ Port: 8003   │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
│           │                     │                   │       │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Security Group Rules                      │ │
│  │  - Inter-instance communication                        │ │
│  │  - SSH access (key-based)                             │ │
│  │  - HTTP/HTTPS for gateway                             │ │
│  │  - PostgreSQL ports (internal only)                   │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Service Configuration Model

```typescript
interface ServiceConfig {
  name: string;
  hasDatabase: boolean;
  ports: number[];
  publicAccess: boolean;
  dockerImage?: string;
  environmentVars?: Record<string, string>;
}
```

## Components and Interfaces

### 1. CDK Stack Structure

```typescript
// Main Stack
class CmvInfrastructureStack extends Stack {
  private vpc: Vpc;
  private securityGroup: SecurityGroup;
  private keyPair: KeyPair;
  
  constructor(scope: Construct, id: string, props?: StackProps);
}

// Service Configuration Interface
interface ServiceConfig {
  name: string;
  hasDatabase: boolean;
  ports: number[];
  publicAccess: boolean;
  dockerImage?: string;
  environmentVars?: Record<string, string>;
}

// Database Configuration Interface
interface DatabaseConfig {
  adminUsername: string;
  adminPassword: string;
  crudUsername: string;
  crudPassword: string;
  databaseName: string;
}
```

### 2. Reusable Constructs

```typescript
// EC2 Instance Construct
class ServiceInstance extends Construct {
  public readonly instance: Instance;
  public readonly privateIp: string;
  
  constructor(scope: Construct, id: string, props: ServiceInstanceProps);
}

// PostgreSQL Setup Construct
class PostgreSQLSetup extends Construct {
  constructor(scope: Construct, id: string, props: PostgreSQLProps);
}
```

### 3. Configuration Array

```typescript
const servicesConfig: ServiceConfig[] = [
  {
    name: 'gateway',
    hasDatabase: true,
    ports: [80, 443, 8001],
    publicAccess: true,
    dockerImage: 'firizgoude/cmv_gateway:latest',
    environmentVars: {
      NODE_ENV: 'production',
      GATEWAY_DATABASE_URL: 'postgresql://...'
    }
  },
  {
    name: 'patients',
    hasDatabase: true,
    ports: [8002],
    publicAccess: false,
    dockerImage: 'firizgoude/cmv_patients:latest',
    environmentVars: {
      PATIENTS_DATABASE_URL: 'postgresql://...'
    }
  },
  {
    name: 'chambres',
    hasDatabase: true,
    ports: [8003],
    publicAccess: false,
    dockerImage: 'firizgoude/cmv_chambres:latest',
    environmentVars: {
      CHAMBRES_DATABASE_URL: 'postgresql://...'
    }
  }
];
```

## Data Models

### Environment Variables Structure

```typescript
interface EnvironmentConfig {
  // Database Admin Credentials
  DB_ADMIN_USERNAME: string;
  DB_ADMIN_PASSWORD: string;
  
  // Database CRUD User Credentials
  DB_CRUD_USERNAME: string;
  DB_CRUD_PASSWORD: string;
  
  // AWS Configuration
  AWS_REGION: string;
  KEY_PAIR_NAME: string;
  
  // Application Secrets
  SECRET_KEY: string;
  ALGORITHM: string;
  
  // AWS S3 Configuration (for patients service)
  AWS_BUCKET_NAME?: string;
  AWS_ACCESS_KEY_ID?: string;
  AWS_SECRET_ACCESS_KEY?: string;
}
```

### User Data Script Template

```bash
#!/bin/bash
# Base setup for all instances
apt-get update
apt-get install -y docker.io docker-compose curl

# Conditional PostgreSQL installation
if [ "$INSTALL_POSTGRES" = "true" ]; then
  apt-get install -y postgresql postgresql-contrib
  # Database setup with roles
fi

# Docker service setup
systemctl enable docker
systemctl start docker

# Pull and run application container
docker pull ${DOCKER_IMAGE}
docker run -d --name ${SERVICE_NAME} -p ${PORTS} ${DOCKER_IMAGE}
```

## 
Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

Property 1: Configuration-driven instance creation
*For any* valid service configuration array, the CDK stack should create exactly one EC2 instance per configuration object
**Validates: Requirements 1.1**

Property 2: Array expansion creates new instances
*For any* two configuration arrays where the second contains all elements of the first plus additional ones, deploying the second should result in additional instances being created
**Validates: Requirements 1.2**

Property 3: Conditional PostgreSQL installation
*For any* service configuration, PostgreSQL should be installed and configured if and only if the hasDatabase property is true
**Validates: Requirements 1.4**

Property 4: Stack outputs completeness
*For any* deployed configuration, the CDK stack outputs should contain connection details for every service instance created
**Validates: Requirements 1.5**

Property 5: Instance type consistency
*For any* deployed service instance, the EC2 instance type should be t2.micro
**Validates: Requirements 2.1**

Property 6: Operating system consistency
*For any* deployed service instance, the AMI should be a Debian-based image
**Validates: Requirements 2.2**

Property 7: VPC membership consistency
*For any* set of deployed service instances, all instances should belong to the same VPC
**Validates: Requirements 2.3**

Property 8: Subnet configuration validity
*For any* created VPC, the subnets should be properly configured with appropriate CIDR blocks and availability zones
**Validates: Requirements 2.4**

Property 9: Security group uniformity
*For any* set of deployed service instances, all instances should initially have the same security group attached
**Validates: Requirements 2.5**

Property 10: Admin role creation and privileges
*For any* database instance, an admin role should exist with full database privileges (CREATE, DROP, ALTER, etc.)
**Validates: Requirements 3.1**

Property 11: CRUD role privilege restriction
*For any* database instance, a CRUD role should exist with only data manipulation privileges (SELECT, INSERT, UPDATE, DELETE) and no schema modification privileges
**Validates: Requirements 3.2, 3.5**

Property 12: Environment variable credential usage
*For any* database instance, the admin and CRUD roles should be created using credentials from environment variables
**Validates: Requirements 3.3**

Property 13: Credential exposure prevention
*For any* deployment, admin credentials should not appear in CloudFormation outputs, logs, or console output
**Validates: Requirements 3.4**

Property 14: Configuration validation
*For any* invalid service configuration (missing required fields, invalid types), the CDK stack should reject the configuration with a clear error message before deployment
**Validates: Requirements 4.4, 4.5**

Property 15: Inter-instance communication
*For any* pair of service instances within the VPC, network communication should be allowed between them
**Validates: Requirements 5.1**

Property 16: Database external access restriction
*For any* database instance, PostgreSQL ports should not be accessible from outside the VPC
**Validates: Requirements 5.2**

Property 17: Gateway public access
*For any* service instance marked with publicAccess: true, HTTP and HTTPS traffic should be allowed from the internet
**Validates: Requirements 5.3**

Property 18: SSH key-based authentication
*For any* service instance, SSH access should be configured with key-based authentication only
**Validates: Requirements 5.4**

Property 19: Database access control
*For any* database instance, PostgreSQL connections should only be accepted from authorized service instances within the VPC
**Validates: Requirements 5.5**

## Error Handling

### Configuration Validation Errors
- Invalid service names (empty, special characters)
- Missing required fields in service configuration
- Invalid port numbers or ranges
- Conflicting network configurations

### Deployment Errors
- AWS resource limits exceeded
- Invalid AMI IDs for the specified region
- VPC/subnet creation failures
- Security group rule conflicts

### Database Setup Errors
- PostgreSQL installation failures
- Role creation errors due to invalid credentials
- Database connection failures
- Privilege assignment errors

### Recovery Strategies
- Rollback mechanisms for partial deployments
- Retry logic for transient AWS API errors
- Validation pre-checks before resource creation
- Clear error messages with remediation steps

## Testing Strategy

### Unit Testing Approach
- Test individual CDK constructs in isolation
- Mock AWS services for unit tests
- Validate configuration parsing and validation logic
- Test user data script generation

### Property-Based Testing Approach
- Use AWS CDK testing utilities and Jest for property-based testing
- Generate random valid service configurations to test deployment consistency
- Test configuration validation with invalid inputs
- Verify security group rules and network configurations across different scenarios

**Property-Based Testing Library**: We will use `@aws-cdk/assert` combined with `fast-check` for property-based testing of CDK constructs.

**Test Configuration**: Each property-based test will run a minimum of 100 iterations to ensure comprehensive coverage of the input space.

**Test Tagging**: Each property-based test will be tagged with a comment referencing the specific correctness property from this design document using the format: `**Feature: aws-cdk-infrastructure, Property {number}: {property_text}**`

### Integration Testing
- Deploy to a test AWS environment
- Verify actual EC2 instances are created with correct configurations
- Test database connectivity and role permissions
- Validate network security rules in practice

### Security Testing
- Verify database instances are not accessible externally
- Test SSH key-based authentication
- Validate that credentials are not exposed in outputs or logs
- Test inter-service communication restrictions