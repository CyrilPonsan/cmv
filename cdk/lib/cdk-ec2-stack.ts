import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as kms from 'aws-cdk-lib/aws-kms';
import { Construct } from 'constructs';

export class CdkEc2Stack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const vpc = new ec2.Vpc(this, 'Vpc', {
      maxAzs: 2,
      subnetConfiguration: [
        {
          cidrMask: 24,
          name: 'Public',
          subnetType: ec2.SubnetType.PUBLIC,
        },
      ],
    });

    const kmsKey = new kms.Key(this, 'EbsEncryptionKey', {
      enableKeyRotation: true,
    });

    const sgMedium = new ec2.SecurityGroup(this, 'SecurityGroupMedium', {
      vpc,
      description: 'Security group for EC2 T2.medium instance',
      allowAllOutbound: true,
    });
    sgMedium.addIngressRule(ec2.Peer.anyIpv4(), ec2.Port.tcp(22), 'Allow SSH access');

    const sgSmall = new ec2.SecurityGroup(this, 'SecurityGroupSmall', {
      vpc,
      description: 'Security group for EC2 T3.small instance',
      allowAllOutbound: true,
    });
    sgSmall.addIngressRule(ec2.Peer.anyIpv4(), ec2.Port.tcp(22), 'Allow SSH access');

    const ec2Medium = new ec2.Instance(this, 'Ec2InstanceMedium', {
      instanceType: ec2.InstanceType.of(ec2.InstanceClass.T2, ec2.InstanceSize.MEDIUM),
      machineImage: ec2.MachineImage.fromSsmParameter('/aws/service/debian/release/12/latest/amd64'),
      vpc,
      securityGroup: sgMedium,
      vpcSubnets: { subnetType: ec2.SubnetType.PUBLIC },
      blockDevices: [
        {
          deviceName: '/dev/xvda',
          volume: ec2.BlockDeviceVolume.ebs(30, {
            encrypted: true,
            kmsKey: kmsKey,
            volumeType: ec2.EbsDeviceVolumeType.GP3,
          }),
        },
      ],
    });

    const ec2Small = new ec2.Instance(this, 'Ec2InstanceSmall', {
      instanceType: ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.SMALL),
      machineImage: ec2.MachineImage.fromSsmParameter('/aws/service/debian/release/12/latest/amd64'),
      vpc,
      securityGroup: sgSmall,
      vpcSubnets: { subnetType: ec2.SubnetType.PUBLIC },
      blockDevices: [
        {
          deviceName: '/dev/xvda',
          volume: ec2.BlockDeviceVolume.ebs(30, {
            encrypted: true,
            kmsKey: kmsKey,
            volumeType: ec2.EbsDeviceVolumeType.GP3,
          }),
        },
      ],
    });
  }
}
