#!/usr/bin/env node
import * as cdk from "aws-cdk-lib";

import { TeampulseServiceStack } from "../lib/teampulse-service-stack";

const app = new cdk.App();
new TeampulseServiceStack(app, "TeampulseStack", {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION ?? "us-east-1",
  },
  description: "TeamPulse invitations backend on ECS Fargate behind an ALB",
});
