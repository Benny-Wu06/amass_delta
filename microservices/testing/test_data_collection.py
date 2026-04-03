import json
import os
import boto3
import pytest
import requests
from botocore.config import Config
import gzip
import io

AWS_REGION = "ap-southeast-2"
URL = "https://7mz3fi8zw1.execute-api.ap-southeast-2.amazonaws.com/"
BUCKET_NAME = "amass-cisa-bucket-staging"

lambda_client = boto3.client(
    "lambda",
    region_name=AWS_REGION,
    config=Config(read_timeout=700, connect_timeout=10),
)

s3_client = boto3.client("s3", region_name=AWS_REGION)
s3 = boto3.resource('s3')
bucket = s3.Bucket(BUCKET_NAME)

def invoke_lambda(function_name, payload=None):
    response = lambda_client.invoke(
        FunctionName=function_name,
        InvocationType="RequestResponse",
        Payload=json.dumps(payload or {}),
    )
    function_error = response.get("FunctionError")
    parsed = json.loads(response["Payload"].read())
    if parsed is None:
        return {"statusCode": None, "body": None, "raw": None, "function_error": function_error}
    return {
        "statusCode": parsed.get("statusCode"),
        "body": parsed.get("body"),
        "raw": parsed,
        "function_error": function_error,
    }

@pytest.fixture(scope="function", autouse=True)
def clearns3bucket():
    bucket.objects.all().delete()

class TestCisaComponent:

    def test_cisa_works_200(self):
        result = invoke_lambda("cisa_scraper")
        assert result["function_error"] is None
        assert result["statusCode"] == 200
    
    def test_cisa_response_body_success(self):
        result = invoke_lambda("cisa_scraper")
        body = json.loads(result["body"])
        assert body["status"] == "success"
    
    def test_cisa_scraper_response_includes_file_path(self):
        result = invoke_lambda("cisa_scraper")
        body = json.loads(result["body"])
        assert "file" in body
        assert body["file"].startswith("raw/")
        assert "cisa_kev" in body["file"]

    def test_cisa_scraper_file_actually_lands_in_s3(self):
        result = invoke_lambda("cisa_scraper")
        body = json.loads(result["body"])
        file_key = body["file"]
        s3_response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix="raw/")
        keys = [obj["Key"] for obj in s3_response.get("Contents", [])]
        assert file_key in keys

    def test_cisa_scraper_uploaded_file_is_valid_json(self):
        result = invoke_lambda("cisa_scraper")
        body = json.loads(result["body"])
        file_key = body["file"]

        s3_obj = s3_client.get_object(Bucket=BUCKET_NAME, Key=file_key)
        content = json.loads(s3_obj["Body"].read().decode("utf-8"))
        assert "vulnerabilities" in content
        assert isinstance(content["vulnerabilities"], list)
        assert len(content["vulnerabilities"]) > 0

class TestCisaIntegration:

    def test_get_scrape_returns_200(self):
        response = requests.get(f"{URL}/v1/scrape", timeout=60)
        assert response.status_code == 200

    def test_get_scrape_returns_json_content_type(self):
        response = requests.get(f"{URL}/v1/scrape", timeout=60)
        assert "application/json" in response.headers.get("Content-Type", "")

    def test_get_scrape_response_body_is_valid_json(self):
        response = requests.get(f"{URL}/v1/scrape", timeout=60)
        body = response.json()
        assert isinstance(body, dict)

    def test_get_scrape_response_has_all_expected_fields(self):
        response = requests.get(f"{URL}/v1/scrape", timeout=60)
        body = response.json()
        assert "status" in body
        assert "file" in body
        assert "timestamp" in body

    def test_get_scrape_status_field_is_success(self):
        response = requests.get(f"{URL}/v1/scrape", timeout=60)
        body = response.json()
        assert body["status"] == "success"

    def test_post_to_scrape_route_returns_404(self):
        response = requests.post(f"{URL}/v1/scrape", timeout=30)
        assert response.status_code == 404

class TestNvdScrapperComponent:

    def test_nvd_scrapper_returns_200(self):
        result = invoke_lambda("nvd_scrapper", payload={"files": ["nvdcve-2.0-modified.json.gz"]})
        assert result["function_error"] is None
        assert result["statusCode"] == 200
    
    def test_nvd_scrapper_response_body_success(self):
        result = invoke_lambda("nvd_scrapper", payload={"files": ["nvdcve-2.0-modified.json.gz"]})
        body = json.loads(result["body"])
        assert body["status"] == "success"
    
    def test_nvd_scrapper_response_includes_file_path(self):
        result = invoke_lambda("nvd_scrapper", payload={"files": ["nvdcve-2.0-modified.json.gz"]})
        body = json.loads(result["body"])
        assert "file" in body
        assert isinstance(body["file"], list)
        file_key = body["file"][0]
        assert file_key.startswith("reference/")
        assert "nvdcve-2.0" in file_key

    def test_nvd_scrapper_file_actually_lands_in_s3(self):
        result = invoke_lambda("nvd_scrapper", payload={"files": ["nvdcve-2.0-modified.json.gz"]})
        body = json.loads(result["body"])
        file_key = body["file"][0]

        s3_response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix="reference/")
        keys = [obj["Key"] for obj in s3_response.get("Contents", [])]
        assert file_key in keys

    def test_nvd_scrapper_uploaded_file_is_valid_json(self):
        result = invoke_lambda("nvd_scrapper", payload={"files": ["nvdcve-2.0-modified.json.gz"]})
        body = json.loads(result["body"])
        file_key = body["file"][0]

        s3_obj = s3_client.get_object(Bucket=BUCKET_NAME, Key=file_key)
        gz_bytes = s3_obj["Body"].read()
        normal_bytes = gzip.decompress(gz_bytes)
        content = json.loads(normal_bytes.decode("utf-8"))
        assert "vulnerabilities" in content
        assert isinstance(content["vulnerabilities"], list)
        assert len(content["vulnerabilities"]) > 0

class TestReferenceIntegration:

    def test_get_reference_returns_200(self):
        response = requests.get(f"{URL}/v1/reference", timeout=60, json={"files": ["nvdcve-2.0-modified.json.gz"]})
        assert response.status_code == 200

    def test_get_reference_returns_json_content_type(self):
        response = requests.get(f"{URL}/v1/reference", timeout=60, json={"files": ["nvdcve-2.0-modified.json.gz"]})
        assert "application/json" in response.headers.get("Content-Type", "")

    def test_get_reference_response_body_is_valid_json(self):
        response = requests.get(f"{URL}/v1/reference", timeout=60, json={"files": ["nvdcve-2.0-modified.json.gz"]})
        body = response.json()
        assert isinstance(body, dict)

    def test_get_reference_response_has_all_expected_fields(self):
        response = requests.get(f"{URL}/v1/reference", timeout=60, json={"files": ["nvdcve-2.0-modified.json.gz"]})
        body = response.json()
        assert "status" in body
        assert "file" in body

    def test_get_reference_status_field_is_success(self):
        response = requests.get(f"{URL}/v1/reference", timeout=60, json={"files": ["nvdcve-2.0-modified.json.gz"]})
        body = response.json()
        assert body["status"] == "success"

    def test_post_to_reference_route_returns_404(self):
        response = requests.post(f"{URL}/v1/reference", timeout=30, json={"files": ["nvdcve-2.0-modified.json.gz"]})
        assert response.status_code == 404

class TestEnrichmentComponent:

    @pytest.fixture(autouse=True)
    def clearns3bucket(self):
        pass

    @pytest.fixture(scope="class", autouse=True)
    def setup_s3_data(self):
        bucket.objects.all().delete()
        invoke_lambda("cisa_scraper")
        invoke_lambda("nvd_scrapper", payload={"files": ["nvdcve-2.0-modified.json.gz"]})

    def test_enrichment_returns_200(self):
        result = invoke_lambda("enrichment")
        assert result["function_error"] is None
        assert result["statusCode"] == 200

    def test_enrichment_response_body_success(self):
        result = invoke_lambda("enrichment")
        body = json.loads(result["body"])
        assert "Successfully enriched" in body

    def test_enrichment_creates_enriched_file_in_s3(self):
        invoke_lambda("enrichment")
        s3_response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix="enriched/")
        keys = [obj["Key"] for obj in s3_response.get("Contents", [])]
        assert "enriched/enriched.json" in keys

    def test_enrichment_output_has_cvss_and_epss_scores(self):
        invoke_lambda("enrichment")
        s3_obj = s3_client.get_object(Bucket=BUCKET_NAME, Key="enriched/enriched.json")
        content = json.loads(s3_obj["Body"].read().decode("utf-8"))
        assert "vulnerabilities" in content
        vuln = content["vulnerabilities"][0]
        assert "cvss_score" in vuln
        assert "epss_score" in vuln

    def test_enrichment_succeeds_without_reference_data(self):
        bucket.objects.all().delete()
        invoke_lambda("cisa_scraper")
        result = invoke_lambda("enrichment")
        assert result["function_error"] is None
        assert result["statusCode"] == 200

    def test_enrichment_returns_400_when_no_raw_data(self):
        bucket.objects.all().delete()
        result = invoke_lambda("enrichment")
        assert result["function_error"] is None
        assert result["statusCode"] == 400  

class TestEnrichmentIntegration:

    @pytest.fixture(autouse=True)
    def clearns3bucket(self):
        pass

    @pytest.fixture(scope="class", autouse=True)
    def setup_s3_data(self):
        bucket.objects.all().delete()
        invoke_lambda("cisa_scraper")
        invoke_lambda("nvd_scrapper", payload={"files": ["nvdcve-2.0-modified.json.gz"]})

    def test_post_enrichment_returns_200(self):
        response = requests.post(f"{URL}/enrichment", timeout=120)
        assert response.status_code == 200

    def test_post_enrichment_response_body_is_valid(self):
        response = requests.post(f"{URL}/enrichment", timeout=120)
        body = response.json()
        assert isinstance(body, str)
        assert "Successfully enriched" in body

    def test_post_enrichment_creates_enriched_file_in_s3(self):
        requests.post(f"{URL}/enrichment", timeout=120)
        s3_response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix="enriched/")
        keys = [obj["Key"] for obj in s3_response.get("Contents", [])]
        assert "enriched/enriched.json" in keys

    def test_get_to_enrichment_returns_404(self):
        response = requests.get(f"{URL}/enrichment", timeout=30)
        assert response.status_code == 404

class TestProcessorComponent:

    @pytest.fixture(autouse=True)
    def clearns3bucket(self):
        pass

    @pytest.fixture(scope="class", autouse=True)
    def setup_full_pipeline(self):
        bucket.objects.all().delete()
        invoke_lambda("cisa_scraper")
        invoke_lambda("nvd_scrapper", payload={"files": ["nvdcve-2.0-modified.json.gz"]})
        invoke_lambda("enrichment")

    def test_processor_returns_200(self):
        result = invoke_lambda("amass-rds-processor")
        assert result["function_error"] is None
        assert result["statusCode"] == 200

    def test_processor_response_body_contains_inserted(self):
        result = invoke_lambda("amass-rds-processor")
        assert "Inserted" in result["body"]
        assert "vulnerabilities" in result["body"]

    def test_processor_inserts_nonzero_vulnerabilities(self):
        result = invoke_lambda("amass-rds-processor")
        count = int(result["body"].split("Inserted ")[1].split(" vulnerabilities")[0])
        assert count > 0

    def test_processor_fails_without_enriched_data(self):
        bucket.objects.all().delete()
        result = invoke_lambda("amass-rds-processor")
        assert result["function_error"] is not None
