import google.cloud.aiplatform as aip
import kfp
from kfp import compiler
from kfp import dsl
from kfp.dsl import (Artifact,
                     Input,
                     Output,
                     OutputPath)


@dsl.container_component
def data_ingestion(project: str, bucket: str, data_file_name: str, features: Output[Artifact]):
    return dsl.ContainerSpec(
        image=f'us-central1-docker.pkg.dev/{project}/labrepo/dataingestor:0.0.1',
        command=[
            'python3', '/pipelines/component/src/component.py'
        ],
        args=['--project_id', project, '--bucket', bucket, '--file_name', data_file_name, '--feature_path',
              features.path])


@dsl.container_component
def mlp_training(project: str, features: Input[Artifact], model_bucket: str, metrics: OutputPath(str)):
    return dsl.ContainerSpec(
        image=f'us-central1-docker.pkg.dev/{project}/labrepo/mlptrainer:0.0.1',
        command=[
            'python3', '/pipelines/component/src/component.py'
        ],
        args=['--project_id', project, '--feature_path', features.path, '--model_repo', model_bucket, '--metrics_path',
              metrics])


# Define the workflow of the pipeline.
@kfp.dsl.pipeline(
    name="heartdisease-predictor-mlp")
def mlp_pipeline(project_id: str, data_bucket: str, trainset_filename: str, model_repo: str):
    # The first step
    di_op = data_ingestion(
        project=project_id,
        bucket=data_bucket,
        data_file_name=trainset_filename
    )

    # The second step 
    training_op = mlp_training(
        project=project_id,
        model_bucket=model_repo,
        features=di_op.outputs['features']
    )


def compile_pipeline():
    compiler.Compiler().compile(pipeline_func=mlp_pipeline,
                                package_path='heartdisease_predictor_mlp.yaml')


def run_pipeline():
    # The Google Cloud project that this pipeline runs in.
    PROJECT_ID = "de2025-475823"
    # The region that this pipeline runs in
    REGION = "us-central1"
    # TODO: Replace with your temp bucket name
    PIPELINE_ROOT = "gs://temp_de2025_group6"

    # Before initializing, make sure to set the GOOGLE_APPLICATION_CREDENTIALS
    # environment variable to the path of your service account.
    aip.init(
        project=PROJECT_ID,
        location=REGION,
    )

    job = aip.PipelineJob(
        display_name="heartdisease-predictor-mlp-pipeline",
        template_path="heartdisease_predictor_mlp.yaml",
        enable_caching=False,
        pipeline_root=PIPELINE_ROOT,
        parameter_values={
            'project_id': PROJECT_ID,
            'data_bucket': 'data_de2025_group6',  # makesure to use your data bucket name
            'trainset_filename': 'Heart_disease_cleveland_new.csv',
            'model_repo': 'models_de2025_group6'  # makesure to use your model bucket name
        }
    )

    job.run()


if __name__ == '__main__':
    compile_pipeline()
    # run_pipeline()
