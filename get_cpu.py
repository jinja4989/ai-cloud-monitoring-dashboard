import boto3
from datetime import datetime, timedelta, timezone

region = "ap-northeast-2"  # 서울
instance_id = "YOUR_INSTANCE_ID_HERE"  # 너 EC2 인스턴스 ID로 바꾸기

cloudwatch = boto3.client("cloudwatch", region_name=region)

end = datetime.now(timezone.utc)
start = end - timedelta(hours=1)

response = cloudwatch.get_metric_statistics(
    Namespace="AWS/EC2",
    MetricName="CPUUtilization",
    Dimensions=[
        {"Name": "InstanceId", "Value": instance_id}
    ],
    StartTime=start,
    EndTime=end,
    Period=300,   # 5분 간격
    Statistics=["Average", "Maximum"]
)

print("Datapoints:")
for dp in sorted(response["Datapoints"], key=lambda x: x["Timestamp"]):
    print(
        dp["Timestamp"],
        "Avg:", round(dp["Average"], 2),
        "Max:", round(dp["Maximum"], 2)
    )
