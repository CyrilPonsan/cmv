import * as cdk from 'aws-cdk-lib';
import { Template, Match } from 'aws-cdk-lib/assertions';
import { CdkEc2Stack } from '../lib/cdk-ec2-stack';

// Set required env vars before stack instantiation
process.env.CDK_DEFAULT_ACCOUNT = '123456789012';
process.env.CDK_DEFAULT_REGION = 'eu-west-1';
process.env.DOMAIN = 'test.example.com';

const app = new cdk.App();
const stack = new CdkEc2Stack(app, 'TestStack', {
  env: { account: '123456789012', region: 'eu-west-1' },
});
const template = Template.fromStack(stack);

describe('CdkEc2Stack unit tests', () => {
  // Requirement 3.1: VPC exists
  test('should create exactly one VPC', () => {
    template.resourceCountIs('AWS::EC2::VPC', 1);
  });

  // Requirement 4.1: KMS key with rotation enabled
  test('should create a KMS key with key rotation enabled', () => {
    template.hasResourceProperties('AWS::KMS::Key', {
      EnableKeyRotation: true,
    });
  });

  // Requirement 5.1: T2.medium instance exists
  test('should create a t2.medium EC2 instance', () => {
    template.hasResourceProperties('AWS::EC2::Instance', {
      InstanceType: 't2.medium',
    });
  });

  // Requirement 6.1: T3.small instance exists
  test('should create a t3.small EC2 instance', () => {
    template.hasResourceProperties('AWS::EC2::Instance', {
      InstanceType: 't3.small',
    });
  });

  // Requirements 5.3, 6.3: EBS volumes are 30 GB
  test('should configure EBS volumes with 30 GB on each instance', () => {
    template.hasResourceProperties('AWS::EC2::Instance', {
      InstanceType: 't2.medium',
      BlockDeviceMappings: Match.arrayWith([
        Match.objectLike({
          Ebs: Match.objectLike({ VolumeSize: 30 }),
        }),
      ]),
    });
    template.hasResourceProperties('AWS::EC2::Instance', {
      InstanceType: 't3.small',
      BlockDeviceMappings: Match.arrayWith([
        Match.objectLike({
          Ebs: Match.objectLike({ VolumeSize: 30 }),
        }),
      ]),
    });
  });

  // Requirements 7.6, 7.7: Security groups allow SSH (port 22)
  test('should create security groups allowing SSH on port 22', () => {
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
});

import * as fc from 'fast-check';

// Feature: cdk-ec2-deployment, Property 1: Stack environment propagation
describe('Property: Stack environment propagation', () => {
  /**
   * Validates: Requirements 1.2
   *
   * For any valid pair of (account, region), the synthesized stack
   * should carry those exact values as its account and region.
   */
  test('stack account and region match the provided env values (min 100 iterations)', () => {
    // Generator: 12-digit numeric account IDs
    const accountArb = fc.array(
      fc.constantFrom('0','1','2','3','4','5','6','7','8','9'),
      { minLength: 12, maxLength: 12 },
    ).map(chars => chars.join(''));

    // Generator: AWS-style region strings like "xx-yyyy-N"
    const lowerAlpha = fc.constantFrom(...'abcdefghijklmnopqrstuvwxyz'.split(''));
    const regionArb = fc.tuple(
      fc.array(lowerAlpha, { minLength: 2, maxLength: 2 }).map(c => c.join('')),
      fc.array(lowerAlpha, { minLength: 4, maxLength: 10 }).map(c => c.join('')),
      fc.integer({ min: 1, max: 9 }),
    ).map(([prefix, name, num]) => `${prefix}-${name}-${num}`);

    fc.assert(
      fc.property(accountArb, regionArb, (account: string, region: string) => {
        const testApp = new cdk.App();
        const testStack = new CdkEc2Stack(testApp, `PropTestStack-${account}-${region}`, {
          env: { account, region },
        });

        // Verify the stack carries the correct environment values
        expect(testStack.account).toBe(account);
        expect(testStack.region).toBe(region);

        // Also verify via template synthesis that the stack can be synthesized
        const testTemplate = Template.fromStack(testStack);
        expect(testTemplate).toBeDefined();
      }),
      { numRuns: 100 },
    );
  });
});
