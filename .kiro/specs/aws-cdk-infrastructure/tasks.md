# Implementation Plan

- [x] 1. Set up CDK project structure and dependencies
  - Initialize new CDK TypeScript project
  - Install required dependencies (@aws-cdk/aws-ec2, @aws-cdk/aws-iam, etc.)
  - Configure tsconfig.json and package.json
  - Set up testing framework with Jest and fast-check
  - _Requirements: 4.1, 4.3_

- [ ]* 1.1 Write property test for project initialization
  - **Property 14: Configuration validation**
  - **Validates: Requirements 4.4, 4.5**

- [x] 2. Create core TypeScript interfaces and types
  - Define ServiceConfig interface with all required properties
  - Create DatabaseConfig interface for PostgreSQL credentials
  - Define EnvironmentConfig interface for environment variables
  - Add validation functions for configuration objects
  - _Requirements: 4.1, 4.4, 4.5_

- [ ]* 2.1 Write property test for configuration validation
  - **Property 14: Configuration validation**
  - **Validates: Requirements 4.4, 4.5**

- [x] 3. Implement VPC and networking infrastructure
  - Create VPC construct with public and private subnets
  - Configure internet gateway and route tables
  - Set up NAT gateway for private subnet internet access
  - Define security groups with appropriate rules
  - _Requirements: 2.3, 2.4, 5.1, 5.2_

- [ ]* 3.1 Write property test for VPC configuration
  - **Property 7: VPC membership consistency**
  - **Validates: Requirements 2.3**

- [ ]* 3.2 Write property test for subnet configuration
  - **Property 8: Subnet configuration validity**
  - **Validates: Requirements 2.4**

- [ ]* 3.3 Write property test for security group rules
  - **Property 9: Security group uniformity**
  - **Validates: Requirements 2.5**

- [x] 4. Create ServiceInstance construct
  - Implement reusable EC2 instance construct
  - Configure t2.micro instance type with Debian AMI
  - Set up key pair for SSH access
  - Generate user data scripts based on service configuration
  - _Requirements: 2.1, 2.2, 5.4_

- [ ]* 4.1 Write property test for instance type consistency
  - **Property 5: Instance type consistency**
  - **Validates: Requirements 2.1**

- [ ]* 4.2 Write property test for operating system consistency
  - **Property 6: Operating system consistency**
  - **Validates: Requirements 2.2**

- [ ]* 4.3 Write property test for SSH authentication
  - **Property 18: SSH key-based authentication**
  - **Validates: Requirements 5.4**

- [x] 5. Implement PostgreSQL setup construct
  - Create PostgreSQLSetup construct for database configuration
  - Generate user data scripts for PostgreSQL installation
  - Implement admin role creation with full privileges
  - Create CRUD role with limited privileges (SELECT, INSERT, UPDATE, DELETE)
  - Use environment variables for database credentials
  - _Requirements: 3.1, 3.2, 3.3, 3.5_

- [ ]* 5.1 Write property test for conditional PostgreSQL installation
  - **Property 3: Conditional PostgreSQL installation**
  - **Validates: Requirements 1.4**

- [ ]* 5.2 Write property test for admin role privileges
  - **Property 10: Admin role creation and privileges**
  - **Validates: Requirements 3.1**

- [ ]* 5.3 Write property test for CRUD role restrictions
  - **Property 11: CRUD role privilege restriction**
  - **Validates: Requirements 3.2, 3.5**

- [ ]* 5.4 Write property test for environment variable usage
  - **Property 12: Environment variable credential usage**
  - **Validates: Requirements 3.3**

- [x] 6. Create main CDK stack class
  - Implement CmvInfrastructureStack extending Stack
  - Process service configuration array
  - Create VPC and security groups
  - Deploy ServiceInstance constructs based on configuration
  - _Requirements: 1.1, 1.2, 1.5_

- [ ]* 6.1 Write property test for configuration-driven deployment
  - **Property 1: Configuration-driven instance creation**
  - **Validates: Requirements 1.1**

- [ ]* 6.2 Write property test for array expansion
  - **Property 2: Array expansion creates new instances**
  - **Validates: Requirements 1.2**

- [ ]* 6.3 Write property test for stack outputs
  - **Property 4: Stack outputs completeness**
  - **Validates: Requirements 1.5**

- [x] 7. Implement security group rules and network policies
  - Configure inter-instance communication rules
  - Block external access to database instances
  - Allow HTTP/HTTPS for gateway instances
  - Set up PostgreSQL port access restrictions
  - _Requirements: 5.1, 5.2, 5.3, 5.5_

- [ ]* 7.1 Write property test for inter-instance communication
  - **Property 15: Inter-instance communication**
  - **Validates: Requirements 5.1**

- [ ]* 7.2 Write property test for database access restriction
  - **Property 16: Database external access restriction**
  - **Validates: Requirements 5.2**

- [ ]* 7.3 Write property test for gateway public access
  - **Property 17: Gateway public access**
  - **Validates: Requirements 5.3**

- [ ]* 7.4 Write property test for database access control
  - **Property 19: Database access control**
  - **Validates: Requirements 5.5**

- [x] 8. Add credential security and output management
  - Implement secure credential handling
  - Prevent admin credentials from appearing in outputs
  - Create stack outputs for connection details
  - Add parameter validation for sensitive data
  - _Requirements: 3.4, 1.5_

- [ ]* 8.1 Write property test for credential exposure prevention
  - **Property 13: Credential exposure prevention**
  - **Validates: Requirements 3.4**

- [x] 9. Create service configuration array and environment setup
  - Define default service configurations for CMV application
  - Create environment variable template
  - Add configuration for gateway, patients, and chambres services
  - Set up Docker image references and port mappings
  - _Requirements: 1.1, 1.4_

- [x] 10. Implement deployment scripts and documentation
  - Create deployment script (deploy.sh)
  - Add environment variable setup instructions
  - Create README with usage examples
  - Add troubleshooting guide
  - _Requirements: 4.4, 4.5_

- [x] 11. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 12. Create integration test suite
  - Set up test AWS environment configuration
  - Create end-to-end deployment test
  - Verify actual EC2 instances and database connectivity
  - Test security group rules in practice
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 12.1 Write integration tests for network security
  - Test actual network connectivity between instances
  - Verify database access restrictions
  - Validate SSH key-based authentication
  - _Requirements: 5.1, 5.2, 5.4_

- [x] 13. Final checkpoint - Complete system validation
  - Ensure all tests pass, ask the user if questions arise.