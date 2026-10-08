// TeamPulse 服务栈（本书示例）：把后端容器部署到 ECS Fargate，前置 ALB。
//
// 选型说明（第 22 章三方案对比的落地其一）：
//   - ECS Fargate：免管理节点，按任务计费，水平扩缩简单，适合单容器 Web 服务。
//   - 备选 App Runner：更省心但可调项少；备选 EC2 ECS：更省钱但要管节点。
// 这里取 Fargate + ALB 作为"最小可用且可演进"的生产形态。
//
// 资源命名统一用连字符（不用 em dash）。
import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import * as ec2 from "aws-cdk-lib/aws-ec2";
import * as ecs from "aws-cdk-lib/aws-ecs";
import * as ecsPatterns from "aws-cdk-lib/aws-ecs-patterns";
import * as logs from "aws-cdk-lib/aws-logs";
import * as path from "path";

export class TeampulseServiceStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // 网络：2 个可用区，含公有 + 私有子网。Fargate 任务跑在私有子网，经 NAT 出网拉镜像。
    const vpc = new ec2.Vpc(this, "teampulse-vpc", {
      maxAzs: 2,
      natGateways: 1,
    });

    const cluster = new ecs.Cluster(this, "teampulse-cluster", {
      vpc,
      containerInsights: true,
    });

    // 容器镜像：从 ../backend 的 Dockerfile 现场构建并推到 CDK 托管的 ECR。
    // synth 阶段只记录 asset 引用，不会真的构建（除非 deploy）。
    const image = ecs.ContainerImage.fromAsset(
      path.join(__dirname, "..", "..", "backend"),
      {
        // 构建上下文是 backend/，Dockerfile 在其根部。
        file: "Dockerfile",
      }
    );

    // L3 构造：一次性拉起 Fargate service + ALB + target group + 安全组。
    const service = new ecsPatterns.ApplicationLoadBalancedFargateService(
      this,
      "teampulse-fargate",
      {
        cluster,
        desiredCount: 2, // 两个任务，滚动发布时保证可用。
        cpu: 256,
        memoryLimitMiB: 512,
        publicLoadBalancer: true,
        // 滚动部署的健康基线：至少保留 100%、最多上浮 200%，实现零停机滚动。
        minHealthyPercent: 100,
        maxHealthyPercent: 200,
        circuitBreaker: { rollback: true }, // 部署失败自动回滚到上一个稳定 task def。
        taskImageOptions: {
          image,
          containerName: "teampulse-backend",
          containerPort: 8000,
          environment: {
            // demo：真实部署应从 Secrets Manager 注入数据库连接串，而非明文环境变量。
            TEAMPULSE_DATABASE_URL:
              "postgresql+psycopg://teampulse:teampulse@db.internal:5432/teampulse",
          },
          logDriver: ecs.LogDrivers.awsLogs({
            streamPrefix: "teampulse",
            logRetention: logs.RetentionDays.TWO_WEEKS,
          }),
        },
      }
    );

    // ALB 健康检查打到 FastAPI 自带的 /docs（demo 简化；生产应加一个 /healthz 轻量端点）。
    service.targetGroup.configureHealthCheck({
      path: "/docs",
      healthyHttpCodes: "200",
    });

    // 按 CPU 自动扩缩：2~6 个任务，目标 CPU 利用率 60%。
    const scaling = service.service.autoScaleTaskCount({
      minCapacity: 2,
      maxCapacity: 6,
    });
    scaling.scaleOnCpuUtilization("cpu-scaling", {
      targetUtilizationPercent: 60,
      scaleInCooldown: cdk.Duration.seconds(60),
      scaleOutCooldown: cdk.Duration.seconds(60),
    });

    new cdk.CfnOutput(this, "service-url", {
      value: `http://${service.loadBalancer.loadBalancerDnsName}`,
      description: "ALB DNS name for the TeamPulse backend",
    });
  }
}
