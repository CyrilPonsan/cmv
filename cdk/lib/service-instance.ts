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

    // PostgreSQL will be managed via Docker Compose on each instance
    // No host-level PostgreSQL installation needed

    // Install and configure Nginx as reverse proxy for gateway instances
    if (serviceConfig.publicAccess) {
      const domain = process.env.DOMAIN || 'localhost';
      userData.addCommands(
        '# Install Nginx',
        'apt-get install -y nginx',
        '',
        '# Remove default site',
        'rm -f /etc/nginx/sites-enabled/default',
        '',
        '# Write nginx.conf',
        'cat > /etc/nginx/nginx.conf << \'NGINX_MAIN_CONF\'',
        'user www-data;',
        'worker_processes auto;',
        'pid /run/nginx.pid;',
        'error_log /var/log/nginx/error.log;',
        'include /etc/nginx/modules-enabled/*.conf;',
        '',
        'events {',
        '	worker_connections 768;',
        '	multi_accept on;',
        '}',
        '',
        'http {',
        '	set_real_ip_from 10.0.0.0/8;',
        '	set_real_ip_from 172.16.0.0/12;',
        '	set_real_ip_from 192.168.0.0/16;',
        '	real_ip_header X-Forwarded-For;',
        '	real_ip_recursive on;',
        '',
        '	sendfile on;',
        '	tcp_nopush on;',
        '	tcp_nodelay on;',
        '	types_hash_max_size 2048;',
        '	server_tokens off;',
        '',
        '	include /etc/nginx/mime.types;',
        '	default_type application/octet-stream;',
        '',
        '	ssl_protocols TLSv1.2 TLSv1.3;',
        '	ssl_prefer_server_ciphers on;',
        '	ssl_ciphers \'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384\';',
        '',
        '	access_log /var/log/nginx/access.log;',
        '',
        '	gzip on;',
        '	gzip_vary on;',
        '	gzip_proxied any;',
        '	gzip_comp_level 6;',
        '	gzip_buffers 16 8k;',
        '	gzip_http_version 1.1;',
        '	gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript image/svg+xml;',
        '',
        '	include /etc/nginx/conf.d/*.conf;',
        '	include /etc/nginx/sites-enabled/*;',
        '}',
        'NGINX_MAIN_CONF',
        '',
        '# Write server block config with DOMAIN substitution',
        `export DOMAIN="${domain}"`,
        'cat > /tmp/bloc_server.conf << \'NGINX_SERVER_CONF\'',
        'limit_req_zone $binary_remote_addr zone=one:10m rate=10r/s;',
        'limit_req_zone $binary_remote_addr zone=api:10m rate=30r/s;',
        '',
        'server {',
        '    listen 443 ssl http2;',
        '    server_name ${DOMAIN} www.${DOMAIN};',
        '',
        '    ssl_certificate /etc/letsencrypt/live/${DOMAIN}/fullchain.pem;',
        '    ssl_certificate_key /etc/letsencrypt/live/${DOMAIN}/privkey.pem;',
        '    include /etc/letsencrypt/options-ssl-nginx.conf;',
        '    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;',
        '',
        '    add_header Content-Security-Policy "default-src \'self\'; script-src \'self\' \'unsafe-inline\' \'unsafe-eval\' https://cdnjs.cloudflare.com; style-src \'self\' \'unsafe-inline\'; img-src \'self\' data:; font-src \'self\' data:; frame-ancestors \'none\';" always;',
        '',
        '    location /api/ {',
        '        proxy_set_header X-Real-IP $remote_addr;',
        '        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;',
        '        proxy_set_header X-Forwarded-Proto $scheme;',
        '        proxy_set_header Host $host;',
        '        proxy_set_header X-Nginx-Proxy true;',
        '        proxy_pass http://localhost:8001;',
        '        limit_req zone=api burst=30 nodelay;',
        '    }',
        '',
        '    location / {',
        '        proxy_set_header X-Real-IP $remote_addr;',
        '        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;',
        '        proxy_set_header X-Forwarded-Proto $scheme;',
        '        proxy_set_header Host $host;',
        '        proxy_set_header X-Nginx-Proxy true;',
        '        proxy_pass http://localhost:8001;',
        '        error_page 502 = @static;',
        '        limit_req zone=one burst=20 nodelay;',
        '    }',
        '',
        '    location @static {',
        '        try_files $uri /index.html =502;',
        '    }',
        '}',
        '',
        'server {',
        '    listen 80;',
        '    server_name ${DOMAIN} www.${DOMAIN};',
        '    return 301 https://$host$request_uri;',
        '}',
        'NGINX_SERVER_CONF',
        '',
        '# Substitute DOMAIN variable and place config',
        `envsubst '\\$DOMAIN' < /tmp/bloc_server.conf > /etc/nginx/sites-available/${domain}`,
        `ln -sf /etc/nginx/sites-available/${domain} /etc/nginx/sites-enabled/`,
        'rm /tmp/bloc_server.conf',
        '',
        '# Test and start Nginx (will fail gracefully if SSL certs not yet present)',
        'nginx -t 2>/dev/null && systemctl enable nginx && systemctl restart nginx || echo "Nginx config test failed - SSL certs may not be installed yet. Run certbot first."',
        ''
      );
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
      serviceConfig.hasDatabase ? 'echo "PostgreSQL: $(docker ps --filter name=postgres --format \\"table {{.Names}}\\\\t{{.Status}}\\")"' : '',
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