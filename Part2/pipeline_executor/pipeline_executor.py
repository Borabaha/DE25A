#!/usr/bin/env python3
"""
Pipeline Executor for Cross-Account Vertex AI Pipeline Submission
账户B调用，账户A运行
"""

import argparse
import json
from google.cloud import aiplatform
from datetime import datetime


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--project_id', required=True, help='目标项目ID (账户A)')
    parser.add_argument('--location', required=True, help='目标区域')
    parser.add_argument('--pipeline_spec_path', required=True, help='Pipeline YAML路径')
    parser.add_argument('--display_name', default='pipeline-job', help='Pipeline显示名称')
    parser.add_argument('--parameter_values', required=True, help='Pipeline参数 (JSON)')
    
    args = parser.parse_args()
    
    # 解析参数
    params = json.loads(args.parameter_values)
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    display_name = f"{args.display_name}-{timestamp}"
    
    print("=" * 60)
    print("🚀 Pipeline Executor - Cross Account")
    print("=" * 60)
    print(f"目标项目: {args.project_id}")
    print(f"目标区域: {args.location}")
    print(f"Pipeline: {args.pipeline_spec_path}")
    print(f"名称: {display_name}")
    print(f"参数: {json.dumps(params, indent=2)}")
    print("=" * 60)
    
    # 初始化目标项目 (账户A)
    aiplatform.init(
        project=args.project_id,
        location=args.location,
        staging_bucket=f"gs://temp2_de2025_group6"
    )
    
    # 创建Pipeline Job
    job = aiplatform.PipelineJob(
        display_name=display_name,
        template_path=args.pipeline_spec_path,
        parameter_values=params,
        enable_caching=False
    )
    
    # 提交
    print("\n📤 提交到账户A的Vertex AI...")
    job.submit()
    
    print("\n✅ 成功!")
    print(f"📊 Job: {job.resource_name}")
    print(f"🔗 查看: https://console.cloud.google.com/vertex-ai/pipelines?project={args.project_id}")


if __name__ == "__main__":
    main()