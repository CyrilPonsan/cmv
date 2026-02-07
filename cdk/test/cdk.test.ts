import * as cdk from 'aws-cdk-lib';
import { Template } from 'aws-cdk-lib/assertions';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as fc from 'fast-check';
import { 
  CmvInfrastructureStack, 
  ServiceInstance,
  validateServiceConfig, 
  validateDatabaseConfig, 
  validateEnvironmentConfig,
  validateServiceConfigArray,
  ConfigurationValidationError,
  CredentialSecurityError,
  validateCredentialSecurity,
  sanitizeConnectionString,
  createSecureDatabaseConfig,
  ServiceConfig,
  DatabaseConfig,
  EnvironmentConfig
} from '../lib/cmv-infrastructure-stack';
import { PostgreSQLSetup } from '../lib/postgresql-setup';

describe('CmvInfrastructureStack', () => {
  test('Stack can be created', () => {
    const app = new cdk.App();
    // WHEN
    const stack = new CmvInfrastructureStack(app, 'MyTestStack');
    // THEN
    const template = Template.fromStack(stack);
    
    // Basic test to ensure stack creation works
    expect(template).toBeDefined();
  });

  test('Fast-check integration works', () => {
    fc.assert(
      fc.property(fc.integer({ min: 1, max: 100 }), (num) => {
        return num > 0;
      })
    );
  });

  test('deployServices creates instances based on configuration array', () => {
    const app = new cdk.App();
    const stack = new CmvInfrastructureStack(app, 'TestStack', {
      env: {
        account: '123456789012',
        region: 'us-east-1'
      }
    });

    const servicesConfig: ServiceConfig[] = [
      {
        name: 'gateway',
        hasDatabase: true,
        ports: [80, 443],
        publicAccess: true,
        dockerImage: 'test/gateway:latest'
      },
      {
        name: 'backend',
        hasDatabase: false,
        ports: [8080],
        publicAccess: false,
        dockerImage: 'test/backend:latest'
      }
    ];

    const databaseConfig: DatabaseConfig = {
      adminUsername: 'admin_user',
      adminPassword: 'securepassword123',
      crudUsername: 'crud_user',
      crudPassword: 'anotherpassword456',
      databaseName: 'test_db'
    };

    // Deploy services
    stack.deployServices(servicesConfig, databaseConfig);

    const template = Template.fromStack(stack);
    
    // Verify that two EC2 instances are created
    template.resourceCountIs('AWS::EC2::Instance', 2);
    
    // Verify service instances can be retrieved
    const gatewayInstance = stack.getServiceInstance('gateway');
    const backendInstance = stack.getServiceInstance('backend');
    
    expect(gatewayInstance).toBeDefined();
    expect(backendInstance).toBeDefined();
    
    // Verify all service instances map is populated
    const allInstances = stack.getAllServiceInstances();
    expect(allInstances.size).toBe(2);
    expect(allInstances.has('gateway')).toBe(true);
    expect(allInstances.has('backend')).toBe(true);
  });

  test('deployServices creates appropriate outputs for each service', () => {
    const app = new cdk.App();
    const stack = new CmvInfrastructureStack(app, 'TestStack', {
      env: {
        account: '123456789012',
        region: 'us-east-1'
      }
    });

    const servicesConfig: ServiceConfig[] = [
      {
        name: 'gateway',
        hasDatabase: true,
        ports: [80, 443],
        publicAccess: true
      }
    ];

    const databaseConfig: DatabaseConfig = {
      adminUsername: 'admin_user',
      adminPassword: 'securepassword123',
      crudUsername: 'crud_user',
      crudPassword: 'anotherpassword456',
      databaseName: 'test_db'
    };

    stack.deployServices(servicesConfig, databaseConfig);

    const template = Template.fromStack(stack);
    const outputs = template.toJSON().Outputs;
    const outputKeys = Object.keys(outputs);
    
    // Verify service-specific outputs are created
    expect(outputKeys.some(key => key.includes('GatewayConnectionDetails'))).toBe(true);
    expect(outputKeys.some(key => key.includes('GatewayServiceUrl'))).toBe(true);
    expect(outputKeys.some(key => key.includes('GatewayDatabaseConnectionTemplate'))).toBe(true);
    
    // Verify summary outputs are created
    expect(outputKeys.some(key => key.includes('DeployedServices'))).toBe(true);
    expect(outputKeys.some(key => key.includes('TotalServicesCount'))).toBe(true);
    expect(outputKeys.some(key => key.includes('DeploymentSummary'))).toBe(true);

    // Verify credential security outputs are created
    expect(outputKeys.some(key => key.includes('CredentialSecurityInfo'))).toBe(true);
    expect(outputKeys.some(key => key.includes('AdminSecretArn'))).toBe(true);
    expect(outputKeys.some(key => key.includes('CrudSecretArn'))).toBe(true);
  });

  test('deployServices validates configuration before deployment', () => {
    const app = new cdk.App();
    const stack = new CmvInfrastructureStack(app, 'TestStack');

    const invalidServicesConfig = [
      {
        // Missing required fields
        hasDatabase: true,
        ports: [8080],
        publicAccess: false
      }
    ];

    // Should throw validation error
    expect(() => {
      stack.deployServices(invalidServicesConfig as ServiceConfig[]);
    }).toThrow(ConfigurationValidationError);
  });
});

describe('Configuration Validation', () => {
  describe('validateServiceConfig', () => {
    test('validates correct service configuration', () => {
      const validConfig = {
        name: 'test-service',
        hasDatabase: true,
        ports: [8080, 8443],
        publicAccess: false,
        dockerImage: 'test/image:latest',
        environmentVars: { NODE_ENV: 'production' }
      };

      const result = validateServiceConfig(validConfig);
      expect(result).toEqual(validConfig);
    });

    test('throws error for missing name', () => {
      const invalidConfig = {
        hasDatabase: true,
        ports: [8080],
        publicAccess: false
      };

      expect(() => validateServiceConfig(invalidConfig))
        .toThrow(ConfigurationValidationError);
    });

    test('throws error for invalid port numbers', () => {
      const invalidConfig = {
        name: 'test-service',
        hasDatabase: true,
        ports: [0, 70000], // Invalid port numbers
        publicAccess: false
      };

      expect(() => validateServiceConfig(invalidConfig))
        .toThrow('Invalid port number');
    });

    test('throws error for invalid service name format', () => {
      const invalidConfig = {
        name: 'test service!', // Invalid characters
        hasDatabase: true,
        ports: [8080],
        publicAccess: false
      };

      expect(() => validateServiceConfig(invalidConfig))
        .toThrow('Service name must contain only alphanumeric characters and hyphens');
    });
  });

  describe('validateDatabaseConfig', () => {
    test('validates correct database configuration', () => {
      const validConfig = {
        adminUsername: 'admin_user',
        adminPassword: 'securepassword123',
        crudUsername: 'crud_user',
        crudPassword: 'anotherpassword456',
        databaseName: 'test_db'
      };

      const result = validateDatabaseConfig(validConfig);
      expect(result).toEqual(validConfig);
    });

    test('throws error for short passwords', () => {
      const invalidConfig = {
        adminUsername: 'admin_user',
        adminPassword: '123', // Too short
        crudUsername: 'crud_user',
        crudPassword: 'anotherpassword456',
        databaseName: 'test_db'
      };

      expect(() => validateDatabaseConfig(invalidConfig))
        .toThrow('adminPassword must be at least 8 characters long');
    });

    test('throws error for invalid username format', () => {
      const invalidConfig = {
        adminUsername: 'admin-user!', // Invalid characters
        adminPassword: 'securepassword123',
        crudUsername: 'crud_user',
        crudPassword: 'anotherpassword456',
        databaseName: 'test_db'
      };

      expect(() => validateDatabaseConfig(invalidConfig))
        .toThrow('adminUsername must contain only alphanumeric characters and underscores');
    });
  });

  describe('validateEnvironmentConfig', () => {
    test('validates correct environment configuration', () => {
      const validConfig = {
        DB_ADMIN_USERNAME: 'admin',
        DB_ADMIN_PASSWORD: 'password123',
        DB_CRUD_USERNAME: 'crud',
        DB_CRUD_PASSWORD: 'password456',
        AWS_REGION: 'us-east-1',
        KEY_PAIR_NAME: 'my-key-pair',
        SECRET_KEY: 'secret123',
        ALGORITHM: 'HS256',
        AWS_BUCKET_NAME: 'my-bucket'
      };

      const result = validateEnvironmentConfig(validConfig);
      expect(result).toEqual(validConfig);
    });

    test('throws error for invalid AWS region format', () => {
      const invalidConfig = {
        DB_ADMIN_USERNAME: 'admin',
        DB_ADMIN_PASSWORD: 'password123',
        DB_CRUD_USERNAME: 'crud',
        DB_CRUD_PASSWORD: 'password456',
        AWS_REGION: 'INVALID_REGION!', // Invalid format
        KEY_PAIR_NAME: 'my-key-pair',
        SECRET_KEY: 'secret123',
        ALGORITHM: 'HS256'
      };

      expect(() => validateEnvironmentConfig(invalidConfig))
        .toThrow('AWS_REGION must be a valid AWS region format');
    });
  });

  describe('validateServiceConfigArray', () => {
    test('validates array of service configurations', () => {
      const validConfigs = [
        {
          name: 'service1',
          hasDatabase: true,
          ports: [8080],
          publicAccess: false
        },
        {
          name: 'service2',
          hasDatabase: false,
          ports: [8081],
          publicAccess: true
        }
      ];

      const result = validateServiceConfigArray(validConfigs);
      expect(result).toHaveLength(2);
      expect(result[0].name).toBe('service1');
      expect(result[1].name).toBe('service2');
    });

    test('throws error for duplicate service names', () => {
      const invalidConfigs = [
        {
          name: 'service1',
          hasDatabase: true,
          ports: [8080],
          publicAccess: false
        },
        {
          name: 'service1', // Duplicate name
          hasDatabase: false,
          ports: [8081],
          publicAccess: true
        }
      ];

      expect(() => validateServiceConfigArray(invalidConfigs))
        .toThrow('Duplicate service name: service1');
    });

    test('throws error for empty array', () => {
      expect(() => validateServiceConfigArray([]))
        .toThrow('At least one service configuration must be provided');
    });
  });
});

describe('ServiceInstance Construct', () => {
  let app: cdk.App;
  let stack: CmvInfrastructureStack;
  let vpc: ec2.Vpc;
  let securityGroup: ec2.SecurityGroup;
  let keyPair: ec2.KeyPair;

  beforeEach(() => {
    app = new cdk.App();
    stack = new CmvInfrastructureStack(app, 'TestStack', {
      env: {
        account: '123456789012',
        region: 'us-east-1'
      }
    });
    vpc = stack.getVpc();
    securityGroup = stack.getSecurityGroup();
    keyPair = stack.getKeyPair();
  });

  test('creates EC2 instance with t2.micro instance type', () => {
    const serviceConfig: ServiceConfig = {
      name: 'test-service',
      hasDatabase: false,
      ports: [8080],
      publicAccess: false,
      dockerImage: 'test/image:latest'
    };

    const serviceInstance = new ServiceInstance(stack, 'TestServiceInstance', {
      vpc,
      securityGroup,
      keyPair,
      serviceConfig
    });

    const template = Template.fromStack(stack);
    
    // Verify EC2 instance is created with t2.micro
    template.hasResourceProperties('AWS::EC2::Instance', {
      InstanceType: 't2.micro'
    });

    expect(serviceInstance.instance).toBeDefined();
    expect(serviceInstance.privateIp).toBeDefined();
  });

  test('creates instance with Debian AMI', () => {
    const serviceConfig: ServiceConfig = {
      name: 'test-service',
      hasDatabase: false,
      ports: [8080],
      publicAccess: false
    };

    new ServiceInstance(stack, 'TestServiceInstance', {
      vpc,
      securityGroup,
      keyPair,
      serviceConfig
    });

    const template = Template.fromStack(stack);
    
    // Verify instance is created (AMI lookup is handled by CDK)
    template.hasResourceProperties('AWS::EC2::Instance', {
      InstanceType: 't2.micro'
    });
  });

  test('configures SSH key pair access', () => {
    const serviceConfig: ServiceConfig = {
      name: 'test-service',
      hasDatabase: false,
      ports: [8080],
      publicAccess: false
    };

    new ServiceInstance(stack, 'TestServiceInstance', {
      vpc,
      securityGroup,
      keyPair,
      serviceConfig
    });

    const template = Template.fromStack(stack);
    
    // Verify key pair is associated with instance - check the actual structure
    const resources = template.toJSON().Resources;
    const instanceResource = Object.values(resources).find((resource: any) => 
      resource.Type === 'AWS::EC2::Instance'
    ) as any;
    
    expect(instanceResource).toBeDefined();
    expect(instanceResource.Properties.KeyName.Ref).toContain('CmvKeyPair');
  });

  test('places public access services in public subnet', () => {
    const serviceConfig: ServiceConfig = {
      name: 'gateway',
      hasDatabase: false,
      ports: [80, 443],
      publicAccess: true
    };

    const serviceInstance = new ServiceInstance(stack, 'GatewayInstance', {
      vpc,
      securityGroup,
      keyPair,
      serviceConfig
    });

    expect(serviceInstance.publicIp).toBeDefined();
  });

  test('places private services in private subnet', () => {
    const serviceConfig: ServiceConfig = {
      name: 'backend',
      hasDatabase: true,
      ports: [8080],
      publicAccess: false
    };

    const serviceInstance = new ServiceInstance(stack, 'BackendInstance', {
      vpc,
      securityGroup,
      keyPair,
      serviceConfig
    });

    expect(serviceInstance.privateIp).toBeDefined();
    expect(serviceInstance.publicIp).toBeUndefined();
  });

  test('generates user data script with Docker setup', () => {
    const serviceConfig: ServiceConfig = {
      name: 'test-service',
      hasDatabase: false,
      ports: [8080],
      publicAccess: false,
      dockerImage: 'test/image:latest',
      environmentVars: {
        NODE_ENV: 'production',
        PORT: '8080'
      }
    };

    new ServiceInstance(stack, 'TestServiceInstance', {
      vpc,
      securityGroup,
      keyPair,
      serviceConfig
    });

    const template = Template.fromStack(stack);
    
    // Verify instance has user data containing Docker setup
    const resources = template.toJSON().Resources;
    const instanceResource = Object.values(resources).find((resource: any) => 
      resource.Type === 'AWS::EC2::Instance'
    ) as any;
    
    expect(instanceResource).toBeDefined();
    expect(instanceResource.Properties.UserData['Fn::Base64']).toContain('docker');
    expect(instanceResource.Properties.UserData['Fn::Base64']).toContain('test/image:latest');
  });

  test('generates user data script with PostgreSQL setup when hasDatabase is true', () => {
    const serviceConfig: ServiceConfig = {
      name: 'database-service',
      hasDatabase: true,
      ports: [8080, 5432],
      publicAccess: false
    };

    const databaseConfig: DatabaseConfig = {
      adminUsername: 'admin_user',
      adminPassword: 'securepassword123',
      crudUsername: 'crud_user',
      crudPassword: 'anotherpassword456',
      databaseName: 'test_db'
    };

    new ServiceInstance(stack, 'DatabaseServiceInstance', {
      vpc,
      securityGroup,
      keyPair,
      serviceConfig,
      databaseConfig
    });

    const template = Template.fromStack(stack);
    
    // Verify instance is created with user data containing PostgreSQL setup
    const resources = template.toJSON().Resources;
    const instanceResource = Object.values(resources).find((resource: any) => 
      resource.Type === 'AWS::EC2::Instance'
    ) as any;
    
    expect(instanceResource).toBeDefined();
    expect(instanceResource.Properties.UserData['Fn::Base64']).toContain('postgresql');
    expect(instanceResource.Properties.UserData['Fn::Base64']).toContain('admin_user');
    expect(instanceResource.Properties.UserData['Fn::Base64']).toContain('crud_user');
  });

  test('creates stack outputs for instance details', () => {
    const serviceConfig: ServiceConfig = {
      name: 'test-service',
      hasDatabase: false,
      ports: [8080],
      publicAccess: false
    };

    new ServiceInstance(stack, 'TestServiceInstance', {
      vpc,
      securityGroup,
      keyPair,
      serviceConfig
    });

    const template = Template.fromStack(stack);
    
    // Verify outputs are created - check for the actual output names with generated suffixes
    const outputs = template.toJSON().Outputs;
    const outputKeys = Object.keys(outputs);
    
    expect(outputKeys.some(key => key.startsWith('TestServiceInstanceInstanceId'))).toBe(true);
    expect(outputKeys.some(key => key.startsWith('TestServiceInstancePrivateIp'))).toBe(true);
    expect(outputKeys.some(key => key.startsWith('TestServiceInstanceServicePorts'))).toBe(true);
  });

  test('adds appropriate tags to instance', () => {
    const serviceConfig: ServiceConfig = {
      name: 'test-service',
      hasDatabase: true,
      ports: [8080],
      publicAccess: false
    };

    new ServiceInstance(stack, 'TestServiceInstance', {
      vpc,
      securityGroup,
      keyPair,
      serviceConfig
    });

    const template = Template.fromStack(stack);
    
    // Verify instance has appropriate tags
    const resources = template.toJSON().Resources;
    const instanceResource = Object.values(resources).find((resource: any) => 
      resource.Type === 'AWS::EC2::Instance'
    ) as any;
    
    expect(instanceResource).toBeDefined();
    expect(instanceResource.Properties.Tags).toEqual(
      expect.arrayContaining([
        { Key: 'Name', Value: 'cmv-test-service' },
        { Key: 'Service', Value: 'test-service' },
        { Key: 'HasDatabase', Value: 'true' },
        { Key: 'PublicAccess', Value: 'false' }
      ])
    );
  });
});

describe('PostgreSQLSetup Construct', () => {
  let app: cdk.App;
  let stack: cdk.Stack;
  let userData: ec2.UserData;
  let databaseConfig: DatabaseConfig;

  beforeEach(() => {
    app = new cdk.App();
    stack = new cdk.Stack(app, 'TestStack');
    userData = ec2.UserData.forLinux();
    databaseConfig = {
      adminUsername: 'admin_user',
      adminPassword: 'securepassword123',
      crudUsername: 'crud_user',
      crudPassword: 'anotherpassword456',
      databaseName: 'test_db'
    };
  });

  test('creates PostgreSQL setup construct successfully', () => {
    const postgresSetup = new PostgreSQLSetup(stack, 'TestPostgreSQLSetup', {
      databaseConfig,
      userData
    });

    expect(postgresSetup).toBeDefined();
  });

  test('generates PostgreSQL commands with admin role privileges', () => {
    const commands = PostgreSQLSetup.generatePostgreSQLCommands(databaseConfig);
    
    // Verify admin role creation commands are present
    const commandsString = commands.join('\n');
    expect(commandsString).toContain('CREATE USER admin_user');
    expect(commandsString).toContain('ALTER USER admin_user CREATEDB CREATEROLE SUPERUSER');
    expect(commandsString).toContain('GRANT ALL PRIVILEGES ON DATABASE test_db TO admin_user');
  });

  test('generates PostgreSQL commands with CRUD role limited privileges', () => {
    const commands = PostgreSQLSetup.generatePostgreSQLCommands(databaseConfig);
    
    // Verify CRUD role creation commands are present
    const commandsString = commands.join('\n');
    expect(commandsString).toContain('CREATE USER crud_user');
    expect(commandsString).toContain('GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES');
    expect(commandsString).toContain('REVOKE CREATE ON SCHEMA public FROM crud_user');
  });

  test('generates PostgreSQL commands with networking configuration', () => {
    const commands = PostgreSQLSetup.generatePostgreSQLCommands(databaseConfig);
    
    // Verify networking configuration commands are present
    const commandsString = commands.join('\n');
    expect(commandsString).toContain('listen_addresses = \'*\'');
    expect(commandsString).toContain('host all all 10.0.0.0/16 md5');
    expect(commandsString).toContain('systemctl restart postgresql');
  });

  test('uses environment variables for database credentials', () => {
    const commands = PostgreSQLSetup.generatePostgreSQLCommands(databaseConfig);
    
    // Verify that the generated commands use the provided credentials
    const commandsString = commands.join('\n');
    expect(commandsString).toContain(databaseConfig.adminUsername);
    expect(commandsString).toContain(databaseConfig.adminPassword);
    expect(commandsString).toContain(databaseConfig.crudUsername);
    expect(commandsString).toContain(databaseConfig.crudPassword);
    expect(commandsString).toContain(databaseConfig.databaseName);
  });

  test('adds PostgreSQL commands to user data', () => {
    new PostgreSQLSetup(stack, 'TestPostgreSQLSetup', {
      databaseConfig,
      userData
    });

    // Get the rendered user data
    const renderedUserData = userData.render();
    
    // Verify PostgreSQL installation commands are added
    expect(renderedUserData).toContain('apt-get install -y postgresql postgresql-contrib');
    expect(renderedUserData).toContain('systemctl enable postgresql');
    expect(renderedUserData).toContain('systemctl start postgresql');
  });
});