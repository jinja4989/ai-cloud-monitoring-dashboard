import boto3

client = boto3.client("bedrock-runtime", region_name="ap-northeast-2")

response = client.invoke_model(
    modelId="amazon.titan-embed-text-v2:0",
    contentType="application/json",
    accept="application/json",
    body='{"inputText": "hello world"}'
)

print(response["body"].read().decode())
