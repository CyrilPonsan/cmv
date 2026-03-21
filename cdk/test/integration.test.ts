import * as cdk from 'aws-cdk-lib';
import { Template, Match } from 'aws-cdk-lib/assertions';
import {
  CmvInfrastructureStack,
  ServiceConfig,
  DatabaseConfig,
} from '../lib/cmv-infrastructure-stack';
import { createDefaultServicesConfig } from '../lib/services-config';

/**
 * Integration test suite for the CMV Infrastructure CDK Stack.
 *
 * These tests synthesize the full stack using the default CMV services
 * configuration (gateway, patients, chambres) and verify the resulting
 * CloudFormation template via CDK Template assertions.
 *
 * Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5
 */

describe('Integration: Full CMV Stack Deployment', () => {
  let app: cdk.App;
  let stack: CmvInfrastructureStack;
  let template: Template;

  const testDatabaseConfig: DatabaseConfig = {
    adminUsername: 'admin_user',
    adminPassword: 'secure_admin_password_123',
    crudUsername: 'crud_user',
    crudPassword: 'secure_crud_password_456',
    databaseName: 'cmv_db',
  };

  // Use the real default services config (gateway, patients, chambres)
  const servicesConfig: ServiceConfig[] = [
    {
      name: 'gateway',
      hasDatabase: true,
      ports: [80, 443, 8001],
      publicAccess: true,
      dockerImage: 'firizgoude/cmv_gateway:latest',
    },
    {
      name: 'patients',
      hasDatabase: true,
      ports: [8002],
      publicAccess: false,
      dockerImage: 'firizgoude/cmv_patients:latest',
    },
    {
      name: 'chambres',
      hasDatabase: true,
      ports: [8003],
      publicAccess: false,
      dockerImage: 'firizgoude/cmv_chambres:latest',
    },
  ];

  beforeEach(() => {
    app = new cdk.App();
    stack = new CmvInfrastructureStack(app, 'IntegrationTestStack', {
      env: { account: '123456789012', region: 'us-east-1' },
    });
    stack.deployServices(servicesConfig, testDatabaseConfig);
    template = Template.fromStack(stack);
  });

  // ─── End-to-end deployment verification ───────────────────────────

  describe('End-to-end deployment', () => {
    test('should create exactly 3 EC2 instances for gateway, patients, and chambres', () => {
      template.resourceCountIs('AWS::EC2::Instance', 3);
    });

    test('should create a VPC', () => {
      template.resourceCountIs('AWS::EC2::VPC', 1);
      template.hasResourceProperties('AWS::EC2::VPC', {
        CidrBlock: '10.0.0.0/16',
        EnableDnsHostnames: true,
        EnableDnsSupport: true,
      });
    });

    test('should create a key pair', () => {
      template.hasResourceProperties('AWS::EC2::KeyPair', {
        KeyName: 'cmv-infrastructure-key',
        KeyType: 'rsa',
        KeyFormat: 'pem',
      });
    });

    test('all instances should use t3.micro', () => {
      const instances = template.findResources('AWS::EC2::Instance');
      const instanceKeys = Object.keys(instances);
      expect(instanceKeys.length).toBe(3);

      instanceKeys.forEach((key) => {
        expect(instances[key].Properties.InstanceType).toBe('t3.micro');
      });
    });

    test('all instances should reference the key pair', () => {
      const instances = template.findResources('AWS::EC2::Instance');
      Object.values(instances).forEach((inst: any) => {
        expect(inst.Properties.KeyName).toBeDefined();
        expect(inst.Properties.KeyName.Ref).toMatch(/CmvKeyPair/);
      });
    });

    test('stack should expose deployed services output', () => {
      const outputs = template.toJSON().Outputs;
      const keys = Object.keys(outputs);
      expect(keys.some((k) => k.includes('DeployedServices'))).toBe(true);
      expect(keys.some((k) => k.includes('TotalServicesCount'))).toBe(true);
    });

    test('service instances should be retrievable by name', () => {
      expect(stack.getServiceInstance('gateway')).toBeDefined();
      expect(stack.getServiceInstance('patients')).toBeDefined();
      expect(stack.getServiceInstance('chambres')).toBeDefined();
      expect(stack.getAllServiceInstances().size).toBe(3);
    });
  });

  // ─── Helper to extract user data as a single string ────────────────
  // UserData may be a plain string or a Fn::Join with interleaved
  // CloudFormation references (e.g. secret ARNs). This helper
  // concatenates all string fragments so we can search the content.

  function extractUserDataString(instance: any): string {
    const base64 = instance.Properties.UserData['Fn::Base64'];
    if (typeof base64 === 'string') return base64;
    if (base64 && base64['Fn::Join']) {
      return base64['Fn::Join'][1]
        .filter((part: any) => typeof part === 'string')
        .join('');
    }
    return JSON.stringify(base64);
  }

  // ─── EC2 instance configuration verification ─────────────────────

  describe('EC2 instance configuration', () => {
    test('gateway instance should have Docker user data with correct image', () => {
      const instances = template.findResources('AWS::EC2::Instance');
      const gatewayInstance = Object.values(instances).find((inst: any) => {
        const tags = inst.Properties.Tags || [];
        return tags.some((t: any) => t.Key === 'Service' && t.Value === 'gateway');
      }) as any;

      expect(gatewayInstance).toBeDefined();
      const userData = extractUserDataString(gatewayInstance);
      expect(userData).toContain('docker');
      expect(userData).toContain('firizgoude/cmv_gateway:latest');
    });

    test('patients instance should have Docker user data with correct image', () => {
      const instances = template.findResources('AWS::EC2::Instance');
      const patientsInstance = Object.values(instances).find((inst: any) => {
        const tags = inst.Properties.Tags || [];
        return tags.some((t: any) => t.Key === 'Service' && t.Value === 'patients');
      }) as any;

      expect(patientsInstance).toBeDefined();
      const userData = extractUserDataString(patientsInstance);
      expect(userData).toContain('firizgoude/cmv_patients:latest');
    });

    test('chambres instance should have Docker user data with correct image', () => {
      const instances = template.findResources('AWS::EC2::Instance');
      const chambresInstance = Object.values(instances).find((inst: any) => {
        const tags = inst.Properties.Tags || [];
        return tags.some((t: any) => t.Key === 'Service' && t.Value === 'chambres');
      }) as any;

      expect(chambresInstance).toBeDefined();
      const userData = extractUserDataString(chambresInstance);
      expect(userData).toContain('firizgoude/cmv_chambres:latest');
    });

    test('each instance should have appropriate service tags', () => {
      const instances = template.findResources('AWS::EC2::Instance');
      const serviceNames = new Set<string>();

      Object.values(instances).forEach((inst: any) => {
        const tags: { Key: string; Value: string }[] = inst.Properties.Tags || [];
        const serviceTag = tags.find((t) => t.Key === 'Service');
        expect(serviceTag).toBeDefined();
        serviceNames.add(serviceTag!.Value);
      });

      expect(serviceNames).toEqual(new Set(['gateway', 'patients', 'chambres']));
    });
  });

  // ─── Database connectivity setup verification ─────────────────────

  describe('Database connectivity setup', () => {
    test('all three services should have PostgreSQL in docker-compose', () => {
      const instances = template.findResources('AWS::EC2::Instance');

      Object.values(instances).forEach((inst: any) => {
        const userData = extractUserDataString(inst);
        // Docker-compose files contain postgres:latest for each service
        expect(userData).toContain('postgres');
        expect(userData).toContain('docker-compose.yml');
      });
    });

    test('user data should contain .env with database credentials', () => {
      const instances = template.findResources('AWS::EC2::Instance');

      Object.values(instances).forEach((inst: any) => {
        const userData = extractUserDataString(inst);
        // .env file is written with DB credentials
        expect(userData).toContain('DB_CRUD_USERNAME');
        expect(userData).toContain('.env');
      });
    });

    test('PostgreSQL networking should be configured for VPC access', () => {
      // Verify the security group allows port 5432 within VPC
      const vpcCidr = Match.objectLike({
        'Fn::GetAtt': Match.arrayWith([
          Match.stringLikeRegexp('CmvVpc.*'),
          'CidrBlock',
        ]),
      });

      template.hasResourceProperties('AWS::EC2::SecurityGroup', {
        SecurityGroupIngress: Match.arrayWith([
          Match.objectLike({
            CidrIp: vpcCidr,
            IpProtocol: 'tcp',
            FromPort: 5432,
            ToPort: 5432,
          }),
        ]),
      });
    });

    test('Secrets Manager secrets should be created for database credentials', () => {
      template.resourceCountIs('AWS::SecretsManager::Secret', 2);

      template.hasResourceProperties('AWS::SecretsManager::Secret', {
        Description: 'Database admin credentials for CMV infrastructure',
      });

      template.hasResourceProperties('AWS::SecretsManager::Secret', {
        Description: 'Database CRUD user credentials for CMV infrastructure',
      });
    });
  });

  // ─── Security group rules (Requirements 5.1–5.5) ─────────────────

  describe('Requirement 5.1: Inter-instance communication within VPC', () => {
    test('should have self-referencing security group rule for all traffic', () => {
      template.hasResourceProperties('AWS::EC2::SecurityGroupIngress', {
        IpProtocol: '-1',
        Description: Match.stringLikeRegexp('.*inter-instance communication.*'),
        SourceSecurityGroupId: Match.objectLike({
          'Fn::GetAtt': Match.arrayWith([Match.stringLikeRegexp('CmvSecurityGroup.*')]),
        }),
        GroupId: Match.objectLike({
          'Fn::GetAtt': Match.arrayWith([Match.stringLikeRegexp('CmvSecurityGroup.*')]),
        }),
      });
    });

    test('should allow application ports 8001, 8002, 8003 within VPC CIDR', () => {
      const vpcCidr = Match.objectLike({
        'Fn::GetAtt': Match.arrayWith([
          Match.stringLikeRegexp('CmvVpc.*'),
          'CidrBlock',
        ]),
      });

      [8001, 8002, 8003].forEach((port) => {
        template.hasResourceProperties('AWS::EC2::SecurityGroup', {
          SecurityGroupIngress: Match.arrayWith([
            Match.objectLike({
              CidrIp: vpcCidr,
              IpProtocol: 'tcp',
              FromPort: port,
              ToPort: port,
            }),
          ]),
        });
      });
    });
  });

  describe('Requirement 5.2: Block external access to Database_Instance', () => {
    test('should not expose port 5432 to 0.0.0.0/0', () => {
      const securityGroups = template.findResources('AWS::EC2::SecurityGroup');

      Object.values(securityGroups).forEach((sg: any) => {
        const ingressRules = sg.Properties?.SecurityGroupIngress || [];
        ingressRules.forEach((rule: any) => {
          if (rule.FromPort === 5432) {
            expect(rule.CidrIp).not.toBe('0.0.0.0/0');
          }
        });
      });
    });

    test('non-public service ports should not be open to the internet', () => {
      const securityGroups = template.findResources('AWS::EC2::SecurityGroup');

      Object.values(securityGroups).forEach((sg: any) => {
        const ingressRules = sg.Properties?.SecurityGroupIngress || [];
        ingressRules.forEach((rule: any) => {
          // Ports 8002 and 8003 belong to non-public services
          if (rule.FromPort === 8002 || rule.FromPort === 8003) {
            expect(rule.CidrIp).not.toBe('0.0.0.0/0');
          }
        });
      });
    });
  });

  describe('Requirement 5.3: Gateway allows HTTP/HTTPS from the internet', () => {
    test('should allow public HTTP access on port 80', () => {
      template.hasResourceProperties('AWS::EC2::SecurityGroup', {
        SecurityGroupIngress: Match.arrayWith([
          Match.objectLike({
            CidrIp: '0.0.0.0/0',
            IpProtocol: 'tcp',
            FromPort: 80,
            ToPort: 80,
          }),
        ]),
      });
    });

    test('should allow public HTTPS access on port 443', () => {
      template.hasResourceProperties('AWS::EC2::SecurityGroup', {
        SecurityGroupIngress: Match.arrayWith([
          Match.objectLike({
            CidrIp: '0.0.0.0/0',
            IpProtocol: 'tcp',
            FromPort: 443,
            ToPort: 443,
          }),
        ]),
      });
    });

    test('should allow public access to gateway application port 8001', () => {
      template.hasResourceProperties('AWS::EC2::SecurityGroup', {
        SecurityGroupIngress: Match.arrayWith([
          Match.objectLike({
            CidrIp: '0.0.0.0/0',
            IpProtocol: 'tcp',
            FromPort: 8001,
            ToPort: 8001,
          }),
        ]),
      });
    });
  });

  describe('Requirement 5.4: SSH access with key-based authentication', () => {
    test('should allow SSH on port 22', () => {
      template.hasResourceProperties('AWS::EC2::SecurityGroup', {
        SecurityGroupIngress: Match.arrayWith([
          Match.objectLike({
            CidrIp: '0.0.0.0/0',
            IpProtocol: 'tcp',
            FromPort: 22,
            ToPort: 22,
          }),
        ]),
      });
    });

    test('should create an RSA key pair in PEM format', () => {
      template.hasResourceProperties('AWS::EC2::KeyPair', {
        KeyName: 'cmv-infrastructure-key',
        KeyType: 'rsa',
        KeyFormat: 'pem',
      });
    });

    test('every EC2 instance should reference the key pair', () => {
      const instances = template.findResources('AWS::EC2::Instance');
      expect(Object.keys(instances).length).toBeGreaterThan(0);

      Object.values(instances).forEach((inst: any) => {
        expect(inst.Properties.KeyName).toBeDefined();
        expect(inst.Properties.KeyName.Ref).toMatch(/CmvKeyPair/);
      });
    });
  });

  describe('Requirement 5.5: PostgreSQL connections only from authorized instances within VPC', () => {
    test('port 5432 should be restricted to VPC CIDR', () => {
      const vpcCidr = Match.objectLike({
        'Fn::GetAtt': Match.arrayWith([
          Match.stringLikeRegexp('CmvVpc.*'),
          'CidrBlock',
        ]),
      });

      template.hasResourceProperties('AWS::EC2::SecurityGroup', {
        SecurityGroupIngress: Match.arrayWith([
          Match.objectLike({
            CidrIp: vpcCidr,
            IpProtocol: 'tcp',
            FromPort: 5432,
            ToPort: 5432,
          }),
        ]),
      });
    });

    test('no security group should expose port 5432 to the public internet', () => {
      const allSGs = template.findResources('AWS::EC2::SecurityGroup');
      const allSGIngress = template.findResources('AWS::EC2::SecurityGroupIngress');

      // Check inline ingress rules
      Object.values(allSGs).forEach((sg: any) => {
        const rules = sg.Properties?.SecurityGroupIngress || [];
        rules.forEach((rule: any) => {
          if (rule.FromPort === 5432) {
            expect(rule.CidrIp).not.toBe('0.0.0.0/0');
          }
        });
      });

      // Check standalone ingress resources
      Object.values(allSGIngress).forEach((rule: any) => {
        if (rule.Properties?.FromPort === 5432) {
          expect(rule.Properties.CidrIp).not.toBe('0.0.0.0/0');
        }
      });
    });
  });
});


/**
 * Integration: Network Security Verification
 *
 * Deep integration tests that verify the full-stack synthesis produces
 * correct network security posture. These tests go beyond individual
 * resource assertions and cross-check relationships between VPC, security
 * groups, instances, key pairs, and user data.
 *
 * Validates: Requirements 5.1, 5.2, 5.4
 */
describe('Integration: Network Security Verification', () => {
  let app: cdk.App;
  let stack: CmvInfrastructureStack;
  let template: Template;

  const testDatabaseConfig: DatabaseConfig = {
    adminUsername: 'admin_user',
    adminPassword: 'secure_admin_password_123',
    crudUsername: 'crud_user',
    crudPassword: 'secure_crud_password_456',
    databaseName: 'cmv_db',
  };

  const servicesConfig: ServiceConfig[] = [
    {
      name: 'gateway',
      hasDatabase: true,
      ports: [80, 443, 8001],
      publicAccess: true,
      dockerImage: 'firizgoude/cmv_gateway:latest',
    },
    {
      name: 'patients',
      hasDatabase: true,
      ports: [8002],
      publicAccess: false,
      dockerImage: 'firizgoude/cmv_patients:latest',
    },
    {
      name: 'chambres',
      hasDatabase: true,
      ports: [8003],
      publicAccess: false,
      dockerImage: 'firizgoude/cmv_chambres:latest',
    },
  ];

  // Helper to extract user data as a single string (same as above)
  function extractUserDataString(instance: any): string {
    const base64 = instance.Properties.UserData['Fn::Base64'];
    if (typeof base64 === 'string') return base64;
    if (base64 && base64['Fn::Join']) {
      return base64['Fn::Join'][1]
        .filter((part: any) => typeof part === 'string')
        .join('');
    }
    return JSON.stringify(base64);
  }

  beforeEach(() => {
    app = new cdk.App();
    stack = new CmvInfrastructureStack(app, 'NetworkSecurityTestStack', {
      env: { account: '123456789012', region: 'us-east-1' },
    });
    stack.deployServices(servicesConfig, testDatabaseConfig);
    template = Template.fromStack(stack);
  });

  // ─── Requirement 5.1: Network connectivity between instances ──────

  describe('Req 5.1 – Network connectivity between instances', () => {
    test('all instances share the same VPC', () => {
      // There is exactly one VPC
      template.resourceCountIs('AWS::EC2::VPC', 1);

      // Every instance's SubnetId must reference a subnet that belongs to
      // the single VPC (CDK resolves this via Ref / Fn::GetAtt).
      const instances = template.findResources('AWS::EC2::Instance');
      const subnets = template.findResources('AWS::EC2::Subnet');
      const subnetLogicalIds = Object.keys(subnets);

      Object.values(instances).forEach((inst: any) => {
        const subnetRef = inst.Properties.SubnetId?.Ref;
        expect(subnetRef).toBeDefined();
        expect(subnetLogicalIds).toContain(subnetRef);
      });
    });

    test('all instances share the same security group', () => {
      const instances = template.findResources('AWS::EC2::Instance');
      const sgRefs: string[] = [];

      Object.values(instances).forEach((inst: any) => {
        const sgIds = inst.Properties.SecurityGroupIds;
        expect(sgIds).toBeDefined();
        expect(sgIds.length).toBeGreaterThan(0);
        // Collect the first SG logical-id reference for each instance
        const ref = sgIds[0]['Fn::GetAtt']?.[0] ?? sgIds[0].Ref;
        expect(ref).toBeDefined();
        sgRefs.push(ref);
      });

      // All references should be identical (same security group)
      const uniqueRefs = [...new Set(sgRefs)];
      expect(uniqueRefs.length).toBe(1);
    });

    test('self-referencing security group ingress rule exists (protocol -1)', () => {
      template.hasResourceProperties('AWS::EC2::SecurityGroupIngress', {
        IpProtocol: '-1',
        SourceSecurityGroupId: Match.objectLike({
          'Fn::GetAtt': Match.arrayWith([Match.stringLikeRegexp('CmvSecurityGroup.*')]),
        }),
        GroupId: Match.objectLike({
          'Fn::GetAtt': Match.arrayWith([Match.stringLikeRegexp('CmvSecurityGroup.*')]),
        }),
      });
    });

    test('application ports 8001, 8002, 8003 are accessible within VPC CIDR', () => {
      const vpcCidr = Match.objectLike({
        'Fn::GetAtt': Match.arrayWith([
          Match.stringLikeRegexp('CmvVpc.*'),
          'CidrBlock',
        ]),
      });

      [8001, 8002, 8003].forEach((port) => {
        template.hasResourceProperties('AWS::EC2::SecurityGroup', {
          SecurityGroupIngress: Match.arrayWith([
            Match.objectLike({
              CidrIp: vpcCidr,
              IpProtocol: 'tcp',
              FromPort: port,
              ToPort: port,
            }),
          ]),
        });
      });
    });

    test('all 3 instances belong to subnets within the same VPC', () => {
      const instances = template.findResources('AWS::EC2::Instance');
      const subnets = template.findResources('AWS::EC2::Subnet');

      // Collect VpcId references from all subnets used by instances
      const vpcRefs = new Set<string>();
      Object.values(instances).forEach((inst: any) => {
        const subnetRef = inst.Properties.SubnetId?.Ref;
        expect(subnetRef).toBeDefined();
        const subnet = subnets[subnetRef];
        expect(subnet).toBeDefined();
        const vpcRef = subnet.Properties.VpcId?.Ref;
        expect(vpcRef).toBeDefined();
        vpcRefs.add(vpcRef);
      });

      // All subnets should reference the same VPC
      expect(vpcRefs.size).toBe(1);
    });
  });

  // ─── Requirement 5.2: Database access restrictions ────────────────

  describe('Req 5.2 – Database access restrictions', () => {
    test('port 5432 is NOT exposed to 0.0.0.0/0 in any security group', () => {
      const securityGroups = template.findResources('AWS::EC2::SecurityGroup');

      Object.values(securityGroups).forEach((sg: any) => {
        const rules = sg.Properties?.SecurityGroupIngress || [];
        rules.forEach((rule: any) => {
          if (rule.FromPort === 5432 || rule.ToPort === 5432) {
            expect(rule.CidrIp).not.toBe('0.0.0.0/0');
          }
        });
      });
    });

    test('port 5432 is NOT exposed to 0.0.0.0/0 in any standalone ingress rule', () => {
      const ingressRules = template.findResources('AWS::EC2::SecurityGroupIngress');

      Object.values(ingressRules).forEach((rule: any) => {
        if (
          rule.Properties?.FromPort === 5432 ||
          rule.Properties?.ToPort === 5432
        ) {
          expect(rule.Properties.CidrIp).not.toBe('0.0.0.0/0');
        }
      });
    });

    test('port 5432 is restricted to VPC CIDR only', () => {
      const vpcCidr = Match.objectLike({
        'Fn::GetAtt': Match.arrayWith([
          Match.stringLikeRegexp('CmvVpc.*'),
          'CidrBlock',
        ]),
      });

      template.hasResourceProperties('AWS::EC2::SecurityGroup', {
        SecurityGroupIngress: Match.arrayWith([
          Match.objectLike({
            CidrIp: vpcCidr,
            IpProtocol: 'tcp',
            FromPort: 5432,
            ToPort: 5432,
          }),
        ]),
      });
    });

    test('non-public service ports (8002, 8003) are not exposed to the internet', () => {
      const securityGroups = template.findResources('AWS::EC2::SecurityGroup');

      Object.values(securityGroups).forEach((sg: any) => {
        const rules = sg.Properties?.SecurityGroupIngress || [];
        rules.forEach((rule: any) => {
          if (rule.FromPort === 8002 || rule.FromPort === 8003) {
            expect(rule.CidrIp).not.toBe('0.0.0.0/0');
          }
        });
      });

      // Also check standalone ingress resources
      const ingressRules = template.findResources('AWS::EC2::SecurityGroupIngress');
      Object.values(ingressRules).forEach((rule: any) => {
        if (
          rule.Properties?.FromPort === 8002 ||
          rule.Properties?.FromPort === 8003
        ) {
          expect(rule.Properties.CidrIp).not.toBe('0.0.0.0/0');
        }
      });
    });

    test('database instances have docker-compose with postgres but no public-facing rules for 5432', () => {
      const instances = template.findResources('AWS::EC2::Instance');
      const securityGroups = template.findResources('AWS::EC2::SecurityGroup');

      // Verify all instances with HasDatabase=true tag contain postgres in docker-compose
      Object.values(instances).forEach((inst: any) => {
        const tags: { Key: string; Value: string }[] = inst.Properties.Tags || [];
        const hasDbTag = tags.find(
          (t) => t.Key === 'HasDatabase' && t.Value === 'true',
        );
        if (hasDbTag) {
          const userData = extractUserDataString(inst);
          expect(userData).toContain('postgres');
        }
      });

      // Cross-check: no SG rule opens 5432 to the public internet
      Object.values(securityGroups).forEach((sg: any) => {
        const rules = sg.Properties?.SecurityGroupIngress || [];
        const publicDbRules = rules.filter(
          (r: any) => r.FromPort === 5432 && r.CidrIp === '0.0.0.0/0',
        );
        expect(publicDbRules.length).toBe(0);
      });
    });
  });

  // ─── Requirement 5.4: SSH key-based authentication ────────────────

  describe('Req 5.4 – SSH key-based authentication', () => {
    test('SSH port 22 is allowed in security group', () => {
      template.hasResourceProperties('AWS::EC2::SecurityGroup', {
        SecurityGroupIngress: Match.arrayWith([
          Match.objectLike({
            IpProtocol: 'tcp',
            FromPort: 22,
            ToPort: 22,
          }),
        ]),
      });
    });

    test('an RSA key pair in PEM format is created with name cmv-infrastructure-key', () => {
      template.hasResourceProperties('AWS::EC2::KeyPair', {
        KeyName: 'cmv-infrastructure-key',
        KeyType: 'rsa',
        KeyFormat: 'pem',
      });
    });

    test('every EC2 instance references the key pair', () => {
      const instances = template.findResources('AWS::EC2::Instance');
      expect(Object.keys(instances).length).toBe(3);

      Object.values(instances).forEach((inst: any) => {
        expect(inst.Properties.KeyName).toBeDefined();
        expect(inst.Properties.KeyName.Ref).toMatch(/CmvKeyPair/);
      });
    });

    test('no password-based SSH configuration exists in user data', () => {
      const instances = template.findResources('AWS::EC2::Instance');

      Object.values(instances).forEach((inst: any) => {
        const userData = extractUserDataString(inst);
        // Ensure no PasswordAuthentication yes directive
        expect(userData).not.toMatch(/PasswordAuthentication\s+yes/i);
      });
    });
  });
});
