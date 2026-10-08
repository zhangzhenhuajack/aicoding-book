import * as cdk from "aws-cdk-lib";
import * as ec2 from "aws-cdk-lib/aws-ec2";
import * as ecs from "aws-cdk-lib/aws-ecs";
import * as ecsPatterns from "aws-cdk-lib/aws-ecs-patterns";
import { Construct } from "constructs";

// 最小可部署形态：VPC + ECS Fargate service + 公网 ALB。
// 后端镜像由 backend/Dockerfile 构建后推到 ECR（见 scripts/rollback.sh 的部署约定）。
export class TeampulseStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const vpc = new ec2.Vpc(this, "teampulse-vpc", {
      maxAzs: 2,
      natGateways: 1,
    });

    const cluster = new ecs.Cluster(this, "teampulse-cluster", { vpc });

    const service = new ecsPatterns.ApplicationLoadBalancedFargateService(
      this,
      "teampulse-service",
      {
        cluster,
        cpu: 256,
        memoryLimitMiB: 512,
        desiredCount: 2,
        taskImageOptions: {
          // 演示用占位镜像；真实部署替换为 ECR 中 backend/Dockerfile 构建出的镜像。
          image: ecs.ContainerImage.fromRegistry("public.ecr.aws/docker/library/python:3.12-slim"),
          containerPort: 8000,
          environment: {
            TEAMPULSE_DATABASE_URL: "postgresql+psycopg://teampulse:change-me@db:5432/teampulse",
          },
        },
        publicLoadBalancer: true,
      },
    );

    // 简单健康检查：根路径即可（demo）。
    service.targetGroup.configureHealthCheck({ path: "/docs" });

    new cdk.CfnOutput(this, "service-url", {
      value: `http://${service.loadBalancer.loadBalancerDnsName}`,
      description: "TeamPulse 服务公网地址",
    });
  }
}
