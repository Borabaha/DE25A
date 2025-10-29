#!/usr/bin/env python3
import argparse
import json
from google.cloud import aiplatform
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description='Submit Vertex AI Pipeline')
    parser.add_argument('--project_id', required=True)
    parser.add_argument('--location', required=True)
    parser.add_argument('--pipeline_spec_path', required=True)
    parser.add_argument('--display_name', default='pipeline-job')
    parser.add_argument('--parameter_values', required=True)
    parser.add_argument('--enable_caching', default='false')
    
    args = parser.parse_args()
    parameter_values = json.loads(args.parameter_values)
    enable_caching = args.enable_caching.lower() == 'true'
    display_name = f"{args.display_name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    print(f"🚀 Submitting Vertex AI Pipeline: {display_name}")
    
    aiplatform.init(project=args.project_id, location=args.location)
    
    job = aiplatform.PipelineJob(
        display_name=display_name,
        template_path=args.pipeline_spec_path,
        parameter_values=parameter_values,
        enable_caching=enable_caching
    )
    
    job.submit()
    print(f"✅ Success: {job.resource_name}")

if __name__ == "__main__":
    main()