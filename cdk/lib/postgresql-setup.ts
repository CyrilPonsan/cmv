import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ssm from 'aws-cdk-lib/aws-ssm';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import { DatabaseConfig, validateCredentialSecurity, CredentialSecurityError } from './cmv-infrastructure-stack';

export interface PostgreSQLSetupProps {
  databaseConfig: DatabaseConfig;
  userData: ec2.UserData;
  useSecureCredentials?: boolean;
  adminSecret?: secretsmanager.Secret;
  crudSecret?: secretsmanager.Secret;
}

/**
 * PostgreSQL Setup Construct
 * 
 * This construct handles the installation and configuration of PostgreSQL
 * on an EC2 instance, including the creation of admin and CRUD roles
 * with appropriate privileges. Supports secure credential handling.
 */
export class PostgreSQLSetup extends Construct {
  constructor(scope: Construct, id: string, props: PostgreSQLSetupProps) {
    super(scope, id);

    // Validate user data for credential exposure if secure credentials are not used
    if (!props.useSecureCredentials) {
      try {
        const userDataContent = props.userData.render();
        validateCredentialSecurity(userDataContent, 'user data script');
      } catch (error) {
        if (error instanceof CredentialSecurityError) {
          console.warn(`Warning: ${error.message}`);
          console.warn('Consider using secure credential handling with AWS Secrets Manager.');
        }
      }
    }

    this.addPostgreSQLInstallation(props.userData, props.databaseConfig, props.useSecureCredentials, props.adminSecret, props.crudSecret);
  }

  /**
   * Adds PostgreSQL installation and configuration commands to the user data script
   * 
   * @param userData - The EC2 UserData object to add commands to
   * @param databaseConfig - Database configuration containing credentials and database name
   * @param useSecureCredentials - Whether to use AWS Secrets Manager for credentials
   * @param adminSecret - AWS Secrets Manager secret for admin credentials
   * @param crudSecret - AWS Secrets Manager secret for CRUD credentials
   */
  private addPostgreSQLInstallation(
    userData: ec2.UserData, 
    databaseConfig: DatabaseConfig, 
    useSecureCredentials?: boolean,
    adminSecret?: secretsmanager.Secret,
    crudSecret?: secretsmanager.Secret
  ): void {
    // Install PostgreSQL
    userData.addCommands(
      '# Install PostgreSQL',
      'apt-get install -y postgresql postgresql-contrib awscli',
      '',
      '# Start and enable PostgreSQL service',
      'systemctl enable postgresql',
      'systemctl start postgresql',
      ''
    );

    // Configure PostgreSQL with secure or direct credentials
    if (useSecureCredentials && adminSecret && crudSecret) {
      this.configureSecureCredentials(userData, databaseConfig, adminSecret, crudSecret);
    } else {
      // Configure PostgreSQL with admin role
      this.configureAdminRole(userData, databaseConfig);

      // Configure CRUD role with limited privileges
      this.configureCrudRole(userData, databaseConfig);
    }

    // Configure PostgreSQL networking
    this.configurePostgreSQLNetworking(userData);
  }

  /**
   * Configures PostgreSQL using secure credentials from AWS Secrets Manager
   * Requirements: 3.4 (prevent admin credentials from appearing in outputs)
   * 
   * @param userData - The EC2 UserData object to add commands to
   * @param databaseConfig - Database configuration containing non-sensitive information
   * @param adminSecret - AWS Secrets Manager secret for admin credentials
   * @param crudSecret - AWS Secrets Manager secret for CRUD credentials
   */
  private configureSecureCredentials(
    userData: ec2.UserData, 
    databaseConfig: DatabaseConfig,
    adminSecret: secretsmanager.Secret,
    crudSecret: secretsmanager.Secret
  ): void {
    const region = cdk.Stack.of(this).region;
    
    userData.addCommands(
      '# Configure PostgreSQL with secure credentials from AWS Secrets Manager',
      'sudo -u postgres psql -c "ALTER USER postgres PASSWORD \'temp_password\';"',
      '',
      `# Create database: ${databaseConfig.databaseName}`,
      `sudo -u postgres createdb ${databaseConfig.databaseName}`,
      '',
      '# Retrieve admin credentials from Secrets Manager',
      `ADMIN_SECRET=$(aws secretsmanager get-secret-value --secret-id ${adminSecret.secretArn} --region ${region} --query SecretString --output text)`,
      'ADMIN_USERNAME=$(echo $ADMIN_SECRET | jq -r .username)',
      'ADMIN_PASSWORD=$(echo $ADMIN_SECRET | jq -r .password)',
      '',
      '# Create admin role with retrieved credentials',
      'sudo -u postgres psql -c "CREATE USER $ADMIN_USERNAME WITH PASSWORD \'$ADMIN_PASSWORD\';"',
      'sudo -u postgres psql -c "ALTER USER $ADMIN_USERNAME CREATEDB CREATEROLE SUPERUSER;"',
      `sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ${databaseConfig.databaseName} TO $ADMIN_USERNAME;"`,
      `sudo -u postgres psql -d ${databaseConfig.databaseName} -c "GRANT ALL PRIVILEGES ON SCHEMA public TO $ADMIN_USERNAME;"`,
      `sudo -u postgres psql -d ${databaseConfig.databaseName} -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $ADMIN_USERNAME;"`,
      `sudo -u postgres psql -d ${databaseConfig.databaseName} -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $ADMIN_USERNAME;"`,
      '',
      '# Retrieve CRUD credentials from Secrets Manager',
      `CRUD_SECRET=$(aws secretsmanager get-secret-value --secret-id ${crudSecret.secretArn} --region ${region} --query SecretString --output text)`,
      'CRUD_USERNAME=$(echo $CRUD_SECRET | jq -r .username)',
      'CRUD_PASSWORD=$(echo $CRUD_SECRET | jq -r .password)',
      '',
      '# Create CRUD role with retrieved credentials',
      'sudo -u postgres psql -c "CREATE USER $CRUD_USERNAME WITH PASSWORD \'$CRUD_PASSWORD\';"',
      `sudo -u postgres psql -c "GRANT CONNECT ON DATABASE ${databaseConfig.databaseName} TO $CRUD_USERNAME;"`,
      `sudo -u postgres psql -d ${databaseConfig.databaseName} -c "GRANT USAGE ON SCHEMA public TO $CRUD_USERNAME;"`,
      `sudo -u postgres psql -d ${databaseConfig.databaseName} -c "GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO $CRUD_USERNAME;"`,
      `sudo -u postgres psql -d ${databaseConfig.databaseName} -c "GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO $CRUD_USERNAME;"`,
      `sudo -u postgres psql -d ${databaseConfig.databaseName} -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO $CRUD_USERNAME;"`,
      `sudo -u postgres psql -d ${databaseConfig.databaseName} -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO $CRUD_USERNAME;"`,
      `sudo -u postgres psql -d ${databaseConfig.databaseName} -c "REVOKE CREATE ON SCHEMA public FROM $CRUD_USERNAME;"`,
      '',
      '# Clear credential variables for security',
      'unset ADMIN_SECRET ADMIN_USERNAME ADMIN_PASSWORD CRUD_SECRET CRUD_USERNAME CRUD_PASSWORD',
      ''
    );
  }

  /**
   * Creates and configures the admin role with full privileges
   * Uses environment variables for credentials as per requirement 3.3
   * 
   * @param userData - The EC2 UserData object to add commands to
   * @param databaseConfig - Database configuration containing admin credentials
   */
  private configureAdminRole(userData: ec2.UserData, databaseConfig: DatabaseConfig): void {
    userData.addCommands(
      '# Configure PostgreSQL with temporary password',
      'sudo -u postgres psql -c "ALTER USER postgres PASSWORD \'temp_password\';"',
      '',
      `# Create database: ${databaseConfig.databaseName}`,
      `sudo -u postgres createdb ${databaseConfig.databaseName}`,
      '',
      `# Create admin role: ${databaseConfig.adminUsername}`,
      `sudo -u postgres psql -c "CREATE USER ${databaseConfig.adminUsername} WITH PASSWORD '${databaseConfig.adminPassword}';"`,
      '',
      '# Grant full privileges to admin role (CREATEDB, CREATEROLE, SUPERUSER)',
      `sudo -u postgres psql -c "ALTER USER ${databaseConfig.adminUsername} CREATEDB CREATEROLE SUPERUSER;"`,
      '',
      '# Grant all privileges on database to admin role',
      `sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ${databaseConfig.databaseName} TO ${databaseConfig.adminUsername};"`,
      '',
      '# Grant all privileges on schema to admin role',
      `sudo -u postgres psql -d ${databaseConfig.databaseName} -c "GRANT ALL PRIVILEGES ON SCHEMA public TO ${databaseConfig.adminUsername};"`,
      '',
      '# Grant all privileges on all tables to admin role',
      `sudo -u postgres psql -d ${databaseConfig.databaseName} -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ${databaseConfig.adminUsername};"`,
      '',
      '# Grant all privileges on all sequences to admin role',
      `sudo -u postgres psql -d ${databaseConfig.databaseName} -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ${databaseConfig.adminUsername};"`,
      '',
      '# Set default privileges for future objects created by admin',
      `sudo -u postgres psql -d ${databaseConfig.databaseName} -c "ALTER DEFAULT PRIVILEGES FOR USER ${databaseConfig.adminUsername} GRANT ALL PRIVILEGES ON TABLES TO ${databaseConfig.adminUsername};"`,
      `sudo -u postgres psql -d ${databaseConfig.databaseName} -c "ALTER DEFAULT PRIVILEGES FOR USER ${databaseConfig.adminUsername} GRANT ALL PRIVILEGES ON SEQUENCES TO ${databaseConfig.adminUsername};"`,
      ''
    );
  }

  /**
   * Creates and configures the CRUD role with limited privileges
   * Restricts privileges to SELECT, INSERT, UPDATE, DELETE only (no schema changes)
   * As per requirements 3.2 and 3.5
   * 
   * @param userData - The EC2 UserData object to add commands to
   * @param databaseConfig - Database configuration containing CRUD credentials
   */
  private configureCrudRole(userData: ec2.UserData, databaseConfig: DatabaseConfig): void {
    userData.addCommands(
      `# Create CRUD role: ${databaseConfig.crudUsername}`,
      `sudo -u postgres psql -c "CREATE USER ${databaseConfig.crudUsername} WITH PASSWORD '${databaseConfig.crudPassword}';"`,
      '',
      '# Grant basic connection privileges to CRUD role',
      `sudo -u postgres psql -c "GRANT CONNECT ON DATABASE ${databaseConfig.databaseName} TO ${databaseConfig.crudUsername};"`,
      '',
      '# Grant schema usage to CRUD role',
      `sudo -u postgres psql -d ${databaseConfig.databaseName} -c "GRANT USAGE ON SCHEMA public TO ${databaseConfig.crudUsername};"`,
      '',
      '# Grant limited privileges (SELECT, INSERT, UPDATE, DELETE) on all existing tables',
      `sudo -u postgres psql -d ${databaseConfig.databaseName} -c "GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ${databaseConfig.crudUsername};"`,
      '',
      '# Grant usage on all existing sequences (needed for INSERT operations with auto-increment)',
      `sudo -u postgres psql -d ${databaseConfig.databaseName} -c "GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO ${databaseConfig.crudUsername};"`,
      '',
      '# Set default privileges for future tables created by admin (CRUD role gets limited access)',
      `sudo -u postgres psql -d ${databaseConfig.databaseName} -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO ${databaseConfig.crudUsername};"`,
      '',
      '# Set default privileges for future sequences created by admin',
      `sudo -u postgres psql -d ${databaseConfig.databaseName} -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO ${databaseConfig.crudUsername};"`,
      '',
      '# Explicitly revoke schema modification privileges from CRUD role (ensure no CREATE, DROP, ALTER)',
      `sudo -u postgres psql -d ${databaseConfig.databaseName} -c "REVOKE CREATE ON SCHEMA public FROM ${databaseConfig.crudUsername};"`,
      ''
    );
  }

  /**
   * Configures PostgreSQL networking to accept connections from within the VPC
   * 
   * @param userData - The EC2 UserData object to add commands to
   */
  private configurePostgreSQLNetworking(userData: ec2.UserData): void {
    userData.addCommands(
      '# Configure PostgreSQL to accept connections from VPC',
      'sed -i "s/#listen_addresses = \'localhost\'/listen_addresses = \'*\'/" /etc/postgresql/*/main/postgresql.conf',
      '',
      '# Configure pg_hba.conf to allow connections from VPC CIDR (10.0.0.0/16)',
      'echo "host all all 10.0.0.0/16 md5" >> /etc/postgresql/*/main/pg_hba.conf',
      '',
      '# Restart PostgreSQL to apply configuration changes',
      'systemctl restart postgresql',
      '',
      '# Verify PostgreSQL is running',
      'systemctl status postgresql --no-pager',
      '',
      '# Log PostgreSQL setup completion',
      'echo "$(date): PostgreSQL setup completed successfully" >> /var/log/postgresql-setup.log',
      ''
    );
  }

  /**
   * Static method to create PostgreSQL user data commands
   * This can be used independently if needed
   * 
   * @param databaseConfig - Database configuration
   * @returns Array of shell commands for PostgreSQL setup
   */
  public static generatePostgreSQLCommands(databaseConfig: DatabaseConfig): string[] {
    const commands: string[] = [];

    // Installation commands
    commands.push(
      '# Install PostgreSQL',
      'apt-get install -y postgresql postgresql-contrib',
      '',
      '# Start and enable PostgreSQL service',
      'systemctl enable postgresql',
      'systemctl start postgresql',
      '',
      '# Configure PostgreSQL with temporary password',
      'sudo -u postgres psql -c "ALTER USER postgres PASSWORD \'temp_password\';"',
      '',
      `# Create database: ${databaseConfig.databaseName}`,
      `sudo -u postgres createdb ${databaseConfig.databaseName}`
    );

    // Admin role setup
    commands.push(
      '',
      `# Create admin role: ${databaseConfig.adminUsername}`,
      `sudo -u postgres psql -c "CREATE USER ${databaseConfig.adminUsername} WITH PASSWORD '${databaseConfig.adminPassword}';"`,
      `sudo -u postgres psql -c "ALTER USER ${databaseConfig.adminUsername} CREATEDB CREATEROLE SUPERUSER;"`,
      `sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ${databaseConfig.databaseName} TO ${databaseConfig.adminUsername};"`,
      `sudo -u postgres psql -d ${databaseConfig.databaseName} -c "GRANT ALL PRIVILEGES ON SCHEMA public TO ${databaseConfig.adminUsername};"`,
      `sudo -u postgres psql -d ${databaseConfig.databaseName} -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ${databaseConfig.adminUsername};"`,
      `sudo -u postgres psql -d ${databaseConfig.databaseName} -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ${databaseConfig.adminUsername};"`
    );

    // CRUD role setup
    commands.push(
      '',
      `# Create CRUD role: ${databaseConfig.crudUsername}`,
      `sudo -u postgres psql -c "CREATE USER ${databaseConfig.crudUsername} WITH PASSWORD '${databaseConfig.crudPassword}';"`,
      `sudo -u postgres psql -c "GRANT CONNECT ON DATABASE ${databaseConfig.databaseName} TO ${databaseConfig.crudUsername};"`,
      `sudo -u postgres psql -d ${databaseConfig.databaseName} -c "GRANT USAGE ON SCHEMA public TO ${databaseConfig.crudUsername};"`,
      `sudo -u postgres psql -d ${databaseConfig.databaseName} -c "GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ${databaseConfig.crudUsername};"`,
      `sudo -u postgres psql -d ${databaseConfig.databaseName} -c "GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO ${databaseConfig.crudUsername};"`,
      `sudo -u postgres psql -d ${databaseConfig.databaseName} -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO ${databaseConfig.crudUsername};"`,
      `sudo -u postgres psql -d ${databaseConfig.databaseName} -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO ${databaseConfig.crudUsername};"`,
      `sudo -u postgres psql -d ${databaseConfig.databaseName} -c "REVOKE CREATE ON SCHEMA public FROM ${databaseConfig.crudUsername};"`
    );

    // Networking configuration
    commands.push(
      '',
      '# Configure PostgreSQL networking',
      'sed -i "s/#listen_addresses = \'localhost\'/listen_addresses = \'*\'/" /etc/postgresql/*/main/postgresql.conf',
      'echo "host all all 10.0.0.0/16 md5" >> /etc/postgresql/*/main/pg_hba.conf',
      'systemctl restart postgresql',
      'systemctl status postgresql --no-pager',
      'echo "$(date): PostgreSQL setup completed successfully" >> /var/log/postgresql-setup.log'
    );

    return commands;
  }
}