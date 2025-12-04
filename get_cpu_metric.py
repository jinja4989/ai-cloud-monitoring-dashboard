import boto3
from datetime import datetime, timedelta, timezone

INSTANCE_ID = "i-0e7de4c8591ccd64a"

cloudwatch = boto3.client("cloudwatch", region_name="ap-northeast-2")

end = datetime.now(timezone.utc)
start = end - timedelta(hours=3)

resp = cloudwatch.get_metric_statistics(
    Namespace="AWS/EC2",
    MetricName="CPUUtilization",
    Dimensions=[{"Name": "InstanceId", "Value": INSTANCE_ID}],
    StartTime=start,
    EndTime=end,
    Period=60, 
    Statistics=["Average"],
)

print("raw resp:", resp)

print("\nDatapoints:")
for dp in sorted(resp["Datapoints"], key=lambda x: x["Timestamp"]):
    print(dp["Timestamp"], f"{dp['Average']:.2f}%")

