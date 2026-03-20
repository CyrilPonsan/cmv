import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import { ServiceConfig, DatabaseConfig } from './cmv-infrastructure-stack';
import { PostgreSQLSetup } from './postgresql-setup';

export interface ServiceInstanceProps {
  vpc: ec2.Vpc;
  securityGroup: ec2.SecurityGroup;
  keyPair: ec2.KeyPair;
  serviceConfig: ServiceConfig;
  databaseConfig?: DatabaseConfig;
  subnet?: ec2.ISubnet;
  adminSecret?: secretsmanager.Secret;
  crudSecret?: secretsmanager.Secret;
  useSecureCredentials?: boolean;
}

export class ServiceInstance extends Construct {
  public readonly instance: ec2.Instance;
  public readonly privateIp: string;
  public readonly publicIp?: string;

  constructor(scope: Construct, id: string, props: ServiceInstanceProps) {
    super(scope, id);

    // Get the latest Debian AMI - use static AMI for testing environments
    let debianAmi: ec2.IMachineImage;
    
    // Check if we're in a testing environment (no account/region specified)
    const stack = cdk.Stack.of(this);
    const isTestEnvironment = !stack.account || !stack.region || stack.account === 'unknown-account';
    
    if (isTestEnvironment) {
      // Use a generic Linux AMI for testing
      debianAmi = ec2.MachineImage.genericLinux({
        'us-east-1': 'ami-0c02fb55956c7d316', // Amazon Linux 2 AMI for testing
        'us-west-2': 'ami-0c02fb55956c7d316',
        'eu-west-1': 'ami-0c02fb55956c7d316',
      });
    } else {
      // Use actual Debian AMI lookup for real deployments
      debianAmi = ec2.MachineImage.lookup({
        name: 'debian-12-amd64-*',
        owners: ['136693071363'], // Debian official AMI owner
        filters: {
          'virtualization-type': ['hvm'],
          'architecture': ['x86_64'],
          'root-device-type': ['ebs'],
        },
      });
    }

    // Create IAM role for EC2 instance
    const instanceRole = new iam.Role(this, 'InstanceRole', {
      assumedBy: new iam.ServicePrincipal('ec2.amazonaws.com'),
      description: `IAM role for ${props.serviceConfig.name} service instance`,
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonSSMManagedInstanceCore'),
      ],
    });

    // Add Secrets Manager permissions if using secure credentials
    if (props.useSecureCredentials && (props.adminSecret || props.crudSecret)) {
      const secretArns: string[] = [];
      if (props.adminSecret) secretArns.push(props.adminSecret.secretArn);
      if (props.crudSecret) secretArns.push(props.crudSecret.secretArn);

      instanceRole.addToPolicy(new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: [
          'secretsmanager:GetSecretValue',
          'secretsmanager:DescribeSecret',
        ],
        resources: secretArns,
      }));
    }

    // Add S3 permissions if needed (for patients service)
    if (props.serviceConfig.environmentVars?.AWS_BUCKET_NAME) {
      instanceRole.addToPolicy(new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: [
          's3:GetObject',
          's3:PutObject',
          's3:DeleteObject',
          's3:ListBucket',
        ],
        resources: [
          `arn:aws:s3:::${props.serviceConfig.environmentVars.AWS_BUCKET_NAME}`,
          `arn:aws:s3:::${props.serviceConfig.environmentVars.AWS_BUCKET_NAME}/*`,
        ],
      }));
    }

    // Generate user data script
    const userData = this.generateUserDataScript(
      props.serviceConfig, 
      props.databaseConfig,
      props.useSecureCredentials,
      props.adminSecret,
      props.crudSecret
    );

    // Determine subnet - use private subnet for non-public services, public for gateway
    const subnet = props.subnet || (props.serviceConfig.publicAccess 
      ? props.vpc.publicSubnets[0] 
      : props.vpc.privateSubnets[0]);

    // Create EC2 instance
    this.instance = new ec2.Instance(this, 'Instance', {
      instanceType: ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.MICRO),
      machineImage: debianAmi,
      vpc: props.vpc,
      vpcSubnets: {
        subnets: [subnet],
      },
      securityGroup: props.securityGroup,
      keyPair: props.keyPair,
      role: instanceRole,
      userData: userData,
      userDataCausesReplacement: true,
      detailedMonitoring: false, // Cost optimization
      blockDevices: [
        {
          deviceName: '/dev/xvda',
          volume: ec2.BlockDeviceVolume.ebs(20, {
            volumeType: ec2.EbsDeviceVolumeType.GP3,
            encrypted: true,
            deleteOnTermination: true,
          }),
        },
      ],
    });

    // Store IP addresses
    this.privateIp = this.instance.instancePrivateIp;
    if (props.serviceConfig.publicAccess) {
      this.publicIp = this.instance.instancePublicIp;
    }

    // Add tags to the instance
    cdk.Tags.of(this.instance).add('Name', `cmv-${props.serviceConfig.name}`);
    cdk.Tags.of(this.instance).add('Service', props.serviceConfig.name);
    cdk.Tags.of(this.instance).add('HasDatabase', props.serviceConfig.hasDatabase.toString());
    cdk.Tags.of(this.instance).add('PublicAccess', props.serviceConfig.publicAccess.toString());

    // Create stack outputs for this instance
    new cdk.CfnOutput(this, 'InstanceId', {
      value: this.instance.instanceId,
      description: `Instance ID for ${props.serviceConfig.name} service`,
      exportName: `Cmv${this.capitalizeFirstLetter(props.serviceConfig.name)}InstanceId`,
    });

    new cdk.CfnOutput(this, 'PrivateIp', {
      value: this.privateIp,
      description: `Private IP for ${props.serviceConfig.name} service`,
      exportName: `Cmv${this.capitalizeFirstLetter(props.serviceConfig.name)}PrivateIp`,
    });

    if (this.publicIp) {
      new cdk.CfnOutput(this, 'PublicIp', {
        value: this.publicIp,
        description: `Public IP for ${props.serviceConfig.name} service`,
        exportName: `Cmv${this.capitalizeFirstLetter(props.serviceConfig.name)}PublicIp`,
      });
    }

    // Output service ports
    const portsString = props.serviceConfig.ports.join(',');
    new cdk.CfnOutput(this, 'ServicePorts', {
      value: portsString,
      description: `Service ports for ${props.serviceConfig.name}`,
      exportName: `Cmv${this.capitalizeFirstLetter(props.serviceConfig.name)}Ports`,
    });
  }

  private generateUserDataScript(
    serviceConfig: ServiceConfig, 
    databaseConfig?: DatabaseConfig,
    useSecureCredentials?: boolean,
    adminSecret?: secretsmanager.Secret,
    crudSecret?: secretsmanager.Secret
  ): ec2.UserData {
    const userData = ec2.UserData.forLinux();

    // Base system setup
    userData.addCommands(
      '#!/bin/bash',
      'set -e',
      '',
      '# Update system packages',
      'apt-get update',
      'apt-get upgrade -y',
      '',
      '# Install essential packages',
      'apt-get install -y curl wget gnupg2 software-properties-common apt-transport-https ca-certificates',
      '',
      '# Install Docker',
      'curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg',
      'echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null',
      'apt-get update',
      'apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin',
      '',
      '# Start and enable Docker service',
      'systemctl enable docker',
      'systemctl start docker',
      '',
      '# Add admin user to docker group',
      'usermod -aG docker admin',
      ''
    );

    // Conditional PostgreSQL installation using PostgreSQLSetup construct
    if (serviceConfig.hasDatabase && databaseConfig) {
      const postgresSetup = new PostgreSQLSetup(this, 'PostgreSQLSetup', {
        databaseConfig: databaseConfig,
        userData: userData,
        useSecureCredentials: useSecureCredentials,
        adminSecret: adminSecret,
        crudSecret: crudSecret,
      });
    }

    // Docker service setup
    if (serviceConfig.dockerImage) {
      // Build environment variables string
      let envVarsString = '';
      if (serviceConfig.environmentVars) {
        const envVars = Object.entries(serviceConfig.environmentVars)
          .map(([key, value]) => `-e ${key}="${value}"`)
          .join(' ');
        envVarsString = envVars;
      }

      // Build port mappings string
      const portMappings = serviceConfig.ports
        .map(port => `-p ${port}:${port}`)
        .join(' ');

      userData.addCommands(
        `# Pull Docker image: ${serviceConfig.dockerImage}`,
        `docker pull ${serviceConfig.dockerImage}`,
        '',
        `# Run ${serviceConfig.name} service container`,
        `docker run -d --name ${serviceConfig.name} --restart unless-stopped \\`,
        `  ${portMappings} \\`,
        `  ${envVarsString} \\`,
        `  ${serviceConfig.dockerImage}`,
        ''
      );
    }

    // Create a simple health check script
    userData.addCommands(
      '# Create health check script',
      'cat > /home/admin/health-check.sh << EOF',
      '#!/bin/bash',
      '# Health check script for service monitoring',
      'echo "Service: ' + serviceConfig.name + '"',
      'echo "Status: $(systemctl is-active docker)"',
      'echo "Container: $(docker ps --filter name=' + serviceConfig.name + ' --format "table {{.Names}}\\t{{.Status}}")"',
      serviceConfig.hasDatabase ? 'echo "PostgreSQL: $(systemctl is-active postgresql)"' : '',
      'EOF',
      '',
      'chmod +x /home/admin/health-check.sh',
      'chown admin:admin /home/admin/health-check.sh',
      '',
      '# Create service startup completion marker',
      'touch /home/admin/service-ready',
      'chown admin:admin /home/admin/service-ready',
      '',
      '# Log completion',
      `echo "$(date): ${serviceConfig.name} service setup completed" >> /var/log/service-setup.log`
    );

    return userData;
  }

  private capitalizeFirstLetter(str: string): string {
    return str.charAt(0).toUpperCase() + str.slice(1);
  }
}