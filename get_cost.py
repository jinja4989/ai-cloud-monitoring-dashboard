import boto3
from datetime import date, timedelta

ce = boto3.client("ce")  # Cost Explorer

end = date.today()
start = end - timedelta(days=7)  # 최근 7일

resp = ce.get_cost_and_usage(
    TimePeriod={"Start": start.strftime("%Y-%m-%d"),
                "End": end.strftime("%Y-%m-%d")},
    Granularity="DAILY",
    Metrics=["UnblendedCost"],
    GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
)

for result in resp["ResultsByTime"]:
    day = result["TimePeriod"]["Start"]
    print(f"=== {day} ===")
    for group in result["Groups"]:
        service = group["Keys"][0]
        amount = group["Metrics"]["UnblendedCost"]["Amount"]
        print(f"{service:40s} {float(amount):.4f} USD")
