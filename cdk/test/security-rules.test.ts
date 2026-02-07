import * as cdk from 'aws-cdk-lib';
import { Template } from 'aws-cdk-lib/assertions';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import { CmvInfrastructureStack, ServiceConfig, DatabaseConfig } from '../lib/cmv-infrastructure-stack';

describe('Security Group Rules and Network Policies', () => {
  let app: cdk.App;
  let stack: CmvInfrastructureStack;
  let template: Template;

  const testServicesConfig: ServiceConfig[] = [
    {
      name: 'gateway',
      hasDatabase: true,
      ports: [80, 443, 8001],
      publicAccess: true,
      dockerImage: 'test/gateway:latest',
    },
    {
      name: 'patients',
      hasDatabase: true,
      ports: [8002],
      publicAccess: false,
      dockerImage: 'test/patients:latest',
    },
    {
      name: 'chambres',
      hasDatabase: true,
      ports: [8003],
      publicAccess: false,
      dockerImage: 'test/chambres:latest',
    }
  ];

  const testDatabaseConfig: DatabaseConfig = {
    adminUsername: 'test_admin',
    adminPassword: 'test_admin_password_123',
    crudUsername: 'test_crud',
    crudPassword: 'test_crud_password_123',
    databaseName: 'test_database',
  };

  beforeEach(() => {
    app = new cdk.App();
    stack = new CmvInfrastructureStack(app, 'TestSecurityStack', {
      env: {
        account: '123456789012',
        region: 'us-east-1',
      },
    });
    stack.deployServices(testServicesConfig, testDatabaseConfig);
    template = Template.fromStack(stack);
  });

  describe('Requirement 5.1: Inter-instance communication', () => {
    test('should allow all traffic between instances in the same security group', () => {
      // Verify that there's a security group rule allowing self-referencing traffic
      template.hasResourceProperties('AWS::EC2::SecurityGroup', {
        SecurityGroupIngress: [
          {
            SourceSecurityGroupId: { Ref: 'CmvSecurityGroup' },
            IpProtocol: '-1',
            Description: 'Allow all traffic between instances in the same security group (inter-instance communication)'
          }
        ]
      });
    });

    test('should allow application ports within VPC for inter-service communication', () => {
      // Verify that application ports are accessible within VPC
      template.hasResourceProperties('AWS::EC2::SecurityGroup', {
        SecurityGroupIngress: [
          {
            CidrIp: '10.0.0.0/16',
            IpProtocol: 'tcp',
            FromPort: 8001,
            ToPort: 8001,
            Description: 'Allow application traffic on port 8001 within VPC (inter-service communication)'
          },
          {
            CidrIp: '10.0.0.0/16',
            IpProtocol: 'tcp',
            FromPort: 8002,
            ToPort: 8002,
            Description: 'Allow application traffic on port 8002 within VPC (inter-service communication)'
          },
          {
            CidrIp: '10.0.0.0/16',
            IpProtocol: 'tcp',
            FromPort: 8003,
            ToPort: 8003,
            Description: 'Allow application traffic on port 8003 within VPC (inter-service communication)'
          }
        ]
      });
    });
  });

  describe('Requirement 5.2: Block external access to database instances', () => {
    test('should restrict PostgreSQL port access to VPC only', () => {
      // Verify that PostgreSQL port 5432 is only accessible from VPC CIDR
      template.hasResourceProperties('AWS::EC2::SecurityGroup', {
        SecurityGroupIngress: [
          {
            CidrIp: '10.0.0.0/16',
            IpProtocol: 'tcp',
            FromPort: 5432,
            ToPort: 5432,
            Description: 'Allow PostgreSQL access within VPC only (blocks external database access)'
          }
        ]
      });
    });

    test('should not allow external access to database service ports', () => {
      // Verify that non-public services don't have 0.0.0.0/0 access rules for their ports
      const securityGroups = template.findResources('AWS::EC2::SecurityGroup');
      
      Object.values(securityGroups).forEach((sg: any) => {
        const ingressRules = sg.Properties?.SecurityGroupIngress || [];
        
        // Check that database service ports (8002, 8003) don't have public access
        ingressRules.forEach((rule: any) => {
          if (rule.FromPort === 8002 || rule.FromPort === 8003) {
            expect(rule.CidrIp).not.toBe('0.0.0.0/0');
            expect(rule.CidrIp).toBe('10.0.0.0/16'); // Should only allow VPC access
          }
        });
      });
    });
  });

  describe('Requirement 5.3: Gateway public access', () => {
    test('should allow public HTTP and HTTPS access for gateway instances', () => {
      // Verify that HTTP and HTTPS ports are accessible from anywhere for gateway
      template.hasResourceProperties('AWS::EC2::SecurityGroup', {
        SecurityGroupIngress: [
          {
            CidrIp: '0.0.0.0/0',
            IpProtocol: 'tcp',
            FromPort: 80,
            ToPort: 80,
            Description: 'Allow public HTTP access to gateway service'
          },
          {
            CidrIp: '0.0.0.0/0',
            IpProtocol: 'tcp',
            FromPort: 443,
            ToPort: 443,
            Description: 'Allow public HTTPS access to gateway service'
          },
          {
            CidrIp: '0.0.0.0/0',
            IpProtocol: 'tcp',
            FromPort: 8001,
            ToPort: 8001,
            Description: 'Allow public access to gateway on port 8001'
          }
        ]
      });
    });
  });

  describe('Requirement 5.4: SSH key-based authentication', () => {
    test('should allow SSH access for administration', () => {
      // Verify that SSH port 22 is accessible for administration
      template.hasResourceProperties('AWS::EC2::SecurityGroup', {
        SecurityGroupIngress: [
          {
            CidrIp: '0.0.0.0/0',
            IpProtocol: 'tcp',
            FromPort: 22,
            ToPort: 22,
            Description: 'Allow SSH access for administration (key-based authentication)'
          }
        ]
      });
    });

    test('should create a key pair for SSH access', () => {
      // Verify that a key pair is created
      template.hasResourceProperties('AWS::EC2::KeyPair', {
        KeyName: 'cmv-infrastructure-key',
        KeyType: 'rsa',
        KeyFormat: 'pem'
      });
    });

    test('should configure EC2 instances to use the key pair', () => {
      // Verify that EC2 instances reference the key pair
      template.hasResourceProperties('AWS::EC2::Instance', {
        KeyName: { Ref: 'CmvKeyPair' }
      });
    });
  });

  describe('Requirement 5.5: Database access control', () => {
    test('should restrict PostgreSQL connections to authorized instances within VPC', () => {
      // This is already tested in Requirement 5.2, but we verify the specific access control
      template.hasResourceProperties('AWS::EC2::SecurityGroup', {
        SecurityGroupIngress: [
          {
            CidrIp: '10.0.0.0/16',
            IpProtocol: 'tcp',
            FromPort: 5432,
            ToPort: 5432,
            Description: 'Allow PostgreSQL access within VPC only (blocks external database access)'
          }
        ]
      });
    });
  });

  describe('Network Access Control Lists (NACLs)', () => {
    test('should create custom NACLs for additional security', () => {
      // Verify that custom NACLs are created
      template.hasResourceProperties('AWS::EC2::NetworkAcl', {
        VpcId: { Ref: 'CmvVpc' }
      });
    });

    test('should deny external PostgreSQL access at subnet level', () => {
      // Verify that NACLs explicitly deny external PostgreSQL access
      template.hasResourceProperties('AWS::EC2::NetworkAclEntry', {
        Protocol: 6, // TCP
        PortRange: {
          From: 5432,
          To: 5432
        },
        RuleAction: 'deny',
        RuleNumber: 50
      });
    });

    test('should allow HTTP/HTTPS traffic in public subnets', () => {
      // Verify that public NACLs allow HTTP/HTTPS
      template.hasResourceProperties('AWS::EC2::NetworkAclEntry', {
        Protocol: 6, // TCP
        PortRange: {
          From: 80,
          To: 80
        },
        RuleAction: 'allow',
        RuleNumber: 100
      });

      template.hasResourceProperties('AWS::EC2::NetworkAclEntry', {
        Protocol: 6, // TCP
        PortRange: {
          From: 443,
          To: 443
        },
        RuleAction: 'allow',
        RuleNumber: 110
      });
    });
  });

  describe('Additional Security Groups', () => {
    test('should create dedicated database security group', () => {
      const dbSecurityGroup = stack.createDatabaseSecurityGroup();
      expect(dbSecurityGroup).toBeInstanceOf(ec2.SecurityGroup);
      expect(dbSecurityGroup.securityGroupId).toBeDefined();
    });

    test('should create dedicated gateway security group', () => {
      const gatewaySecurityGroup = stack.createGatewaySecurityGroup();
      expect(gatewaySecurityGroup).toBeInstanceOf(ec2.SecurityGroup);
      expect(gatewaySecurityGroup.securityGroupId).toBeDefined();
    });
  });

  describe('Network Security Validation', () => {
    test('should validate network security policies without errors', () => {
      // This should not throw any errors
      expect(() => {
        stack.validateNetworkSecurity();
      }).not.toThrow();
    });
  });

  describe('VPC Configuration', () => {
    test('should create VPC with proper CIDR block', () => {
      template.hasResourceProperties('AWS::EC2::VPC', {
        CidrBlock: '10.0.0.0/16'
      });
    });

    test('should create public and private subnets', () => {
      // Verify public subnets
      template.hasResourceProperties('AWS::EC2::Subnet', {
        MapPublicIpOnLaunch: true
      });

      // Verify private subnets
      template.hasResourceProperties('AWS::EC2::Subnet', {
        MapPublicIpOnLaunch: false
      });
    });

    test('should create NAT Gateway for private subnet internet access', () => {
      template.hasResourceProperties('AWS::EC2::NatGateway', {
        AllocationId: { 'Fn::GetAtt': ['CmvVpcPublicSubnet1EIP', 'AllocationId'] }
      });
    });

    test('should create Internet Gateway for public subnet access', () => {
      template.hasResourceProperties('AWS::EC2::InternetGateway', {});
    });
  });
});