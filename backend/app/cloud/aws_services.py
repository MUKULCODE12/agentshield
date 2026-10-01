import os
import json
import boto3
from typing import Dict, Any, Optional

class AWSServicesClient:
    """
    AWS Cloud Services Integration Module:
    - Amazon S3 (Report & Audit PDF Exports)
    - AWS Secrets Manager (Production API Key Retrieval)
    - Amazon CloudWatch (Infra-level Log & Metric Monitoring)
    """
    def __init__(self, region_name: str = "us-east-1"):
        self.region_name = region_name
        self.aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self._s3_client = None
        self._secrets_client = None
        self._cloudwatch_client = None

    def get_secret(self, secret_name: str = "agentshield/prod/api_keys") -> Dict[str, Any]:
        """Fetches API keys and secrets from AWS Secrets Manager."""
        if not self.aws_access_key:
            # Fallback to local env settings if AWS credentials not present
            return {"SECRET_KEY": os.getenv("SECRET_KEY", "local_jwt_secret"), "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY")}

        try:
            client = boto3.client("secretsmanager", region_name=self.region_name)
            response = client.get_secret_value(SecretId=secret_name)
            return json.loads(response.get("SecretString", "{}"))
        except Exception as e:
            print(f"[AWS Secrets Manager] Note: {e}")
            return {"SECRET_KEY": os.getenv("SECRET_KEY")}

    def upload_audit_report_to_s3(self, report_filename: str, report_content: bytes, bucket_name: str = "agentshield-audit-reports-prod") -> str:
        """Uploads compliance audit reports to Amazon S3."""
        if not self.aws_access_key:
            print(f"[AWS S3] Mock Mode: Simulated S3 upload for '{report_filename}'.")
            return f"https://s3.amazonaws.com/{bucket_name}/{report_filename}"

        try:
            client = boto3.client("s3", region_name=self.region_name)
            client.put_object(
                Bucket=bucket_name,
                Key=report_filename,
                Body=report_content,
                ContentType="application/json"
            )
            return f"https://{bucket_name}.s3.{self.region_name}.amazonaws.com/{report_filename}"
        except Exception as e:
            print(f"[AWS S3 Error] {e}")
            return f"https://s3.amazonaws.com/{bucket_name}/{report_filename}"

    def log_metric_to_cloudwatch(self, metric_name: str, value: float, unit: str = "Count"):
        """Logs infra-level execution metrics to Amazon CloudWatch."""
        if not self.aws_access_key:
            return

        try:
            client = boto3.client("cloudwatch", region_name=self.region_name)
            client.put_metric_data(
                Namespace="Sentinel/AgentShield",
                MetricData=[
                    {
                        "MetricName": metric_name,
                        "Value": value,
                        "Unit": unit
                    }
                ]
            )
        except Exception as e:
            pass

aws_services = AWSServicesClient()
