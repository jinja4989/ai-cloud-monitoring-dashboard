import boto3
import json
from datetime import datetime, timedelta, timezone

# ---------- 설정 부분 ----------
REGION = "ap-northeast-2"

# 여기에 너 EC2 인스턴스 ID를 적어줘 (콘솔에서 보이던 i-로 시작하는 값)
INSTANCE_ID = "i-0e7de4c65819cd64a"   

# CloudWatch 에서 조회할 기간 (최근 1시간)
LOOKBACK_HOURS = 1
PERIOD_SECONDS = 300  # 5분 간격
# -----------------------------


def fetch_cpu_datapoints():
    cloudwatch = boto3.client("cloudwatch", region_name=REGION)

    end = datetime.now(timezone.utc)
    start = end - timedelta(hours=LOOKBACK_HOURS)

    resp = cloudwatch.get_metric_statistics(
        Namespace="AWS/EC2",
        MetricName="CPUUtilization",
        Dimensions=[{"Name": "InstanceId", "Value": INSTANCE_ID}],
        StartTime=start,
        EndTime=end,
        Period=PERIOD_SECONDS,
        Statistics=["Average"],
    )

    datapoints = sorted(resp["Datapoints"], key=lambda x: x["Timestamp"])

    return start, end, datapoints


def build_analysis_prompt(start, end, datapoints):
    if not datapoints:
        return None

    cpu_values = [dp["Average"] for dp in datapoints]

    avg_cpu = sum(cpu_values) / len(cpu_values)
    max_cpu = max(cpu_values)
    min_cpu = min(cpu_values)

    # Haiku에게 줄 프롬프트 (한국어)
    prompt = f"""
다음은 EC2 인스턴스 {INSTANCE_ID}의 최근 {LOOKBACK_HOURS}시간 동안 CPU 사용률 데이터입니다.

- 조회 구간 (UTC): {start.isoformat()} ~ {end.isoformat()}
- 데이터 포인트 개수: {len(cpu_values)}
- 평균 CPU 사용률: {avg_cpu:.2f}%
- 최대 CPU 사용률: {max_cpu:.2f}%
- 최소 CPU 사용률: {min_cpu:.2f}%

개별 데이터 포인트(시간 순서, 소수점 2자리 반올림):
{[round(v, 2) for v in cpu_values]}

이 데이터를 기반으로,

1) 현재 CPU 사용 패턴을 한 문단으로 요약해 주고,
2) 성능/안정성/비용 관점에서 위험 수준을 3단계(낮음/보통/높음)로 평가해 주며,
3) 개발자/운영자가 취할 수 있는 구체적인 조치 3가지를 항목 형태로 제안해 주세요.

답변은 모두 한국어로 작성해 주세요.
    """.strip()

    return prompt


def call_haiku(prompt: str):
    bedrock = boto3.client("bedrock-runtime", region_name=REGION)

    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 512,
        "temperature": 0.0,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    }
                ],
            }
        ],
    }

    response = bedrock.invoke_model(
        modelId="anthropic.claude-3-haiku-20240307-v1:0",
        contentType="application/json",
        accept="application/json",
        body=json.dumps(payload),
    )

    body = json.loads(response["body"].read())
    text = body["content"][0]["text"]
    return text


def main():
    print("CloudWatch 에서 실제 CPU 메트릭을 가져오는 중입니다...")
    start, end, datapoints = fetch_cpu_datapoints()

    if not datapoints:
        print("❗ 최근 구간에 CPU 데이터가 없습니다. 인스턴스가 꺼져 있거나, 기간이 너무 짧을 수 있습니다.")
        return

    print(f"가져온 데이터 포인트 수: {len(datapoints)}")

    prompt = build_analysis_prompt(start, end, datapoints)
    if not prompt:
        print("프롬프트 생성에 실패했습니다.")
        return

    print("\nHaiku 모델을 호출하여 분석 중입니다...\n")
    analysis = call_haiku(prompt)

    print("===== Haiku 분석 결과 =====")
    print(analysis)
    print("===========================")


if __name__ == "__main__":
    main()
