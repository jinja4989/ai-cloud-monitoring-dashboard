from flask import Flask, jsonify, request, send_from_directory
import boto3
from datetime import datetime, timedelta, timezone
import json
import time
import psutil  # 실시간 CPU 측정용

app = Flask(__name__)

# ==========================
# 기본 설정
# ==========================
INSTANCE_ID = "i-0e7de4c65819cd64a"
REGION = "ap-northeast-2"

cloudwatch = boto3.client("cloudwatch", region_name=REGION)
bedrock = boto3.client("bedrock-runtime", region_name=REGION)
sns = boto3.client("sns", region_name=REGION)

# 👉 SNS Topic ARN 
SNS_TOPIC_ARN = "arn:aws:sns:ap-northeast-2:907569901932:monitoring-alerts"

# 👉 Bedrock Haiku 모델 ID 
MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"

# 쿨다운
ANALYZE_COOLDOWN_SECONDS = 30
ALERT_COOLDOWN_SECONDS = 300
LAST_ANALYZE_TS = 0
LAST_ALERT_TS = 0


# ==========================
# index.html 서빙
# ==========================
@app.route("/")
def dashboard():
    return send_from_directory("static", "index.html")


# ==========================
# CloudWatch CPU (5분 평균)
# ==========================
@app.route("/cpu")
def cpu_report():
    try:
        end = datetime.now(timezone.utc)
        start = end - timedelta(hours=1)

        resp = cloudwatch.get_metric_statistics(
            Namespace="AWS/EC2",
            MetricName="CPUUtilization",
            Dimensions=[{"Name": "InstanceId", "Value": INSTANCE_ID}],
            StartTime=start,
            EndTime=end,
            Period=300,
            Statistics=["Average"],
            Unit="Percent",
        )

        datapoints = resp.get("Datapoints", [])
        datapoints.sort(key=lambda p: p["Timestamp"])

        return jsonify({
            "status": "ok",
            "timestamps": [dp["Timestamp"].isoformat() for dp in datapoints],
            "values": [dp["Average"] for dp in datapoints],
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ==========================
# 실시간 CPU (psutil)
# ==========================
@app.route("/cpu_live")
def cpu_live():
    try:
        cpu = psutil.cpu_percent(interval=0.1)
        now = datetime.now(timezone.utc).isoformat()
        return jsonify({
            "status": "ok",
            "timestamp": now,
            "cpu_percent": cpu,
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ==========================
# 메트릭 요약 함수
# ==========================
def get_metric_summary(instance_id, region, period_minutes=60):
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(minutes=period_minutes)

    metrics_def = {
        "CPUUtilization": ("Percent", ["Average", "Maximum"]),
        "NetworkIn": ("Bytes", ["Average", "Maximum"]),
        "NetworkOut": ("Bytes", ["Average", "Maximum"]),
    }

    summary = {
        "instance_id": instance_id,
        "region": region,
        "period_minutes": period_minutes,
        "time_range_utc": {
            "start": start_time.isoformat(),
            "end": end_time.isoformat(),
        },
        "metrics": {},
    }

    for metric_name, (unit, stats) in metrics_def.items():
        resp = cloudwatch.get_metric_statistics(
            Namespace="AWS/EC2",
            MetricName=metric_name,
            Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
            StartTime=start_time,
            EndTime=end_time,
            Period=300,
            Statistics=stats,
            Unit=unit,
        )
        datapoints = resp.get("Datapoints", [])
        if not datapoints:
            summary["metrics"][metric_name] = {
                "average": None,
                "maximum": None,
                "datapoint_count": 0,
            }
            continue

        averages = [dp.get("Average") for dp in datapoints if "Average" in dp]
        maximums = [dp.get("Maximum") for dp in datapoints if "Maximum" in dp]

        summary["metrics"][metric_name] = {
            "average": sum(averages) / len(averages) if averages else None,
            "maximum": max(maximums) if maximums else None,
            "datapoint_count": len(datapoints),
        }

    return summary


# ==========================
# Haiku 프롬프트
# ==========================
AI_ANALYZE_SYSTEM_PROMPT = """
너는 AWS 인프라 운영을 돕는 SRE/DevOps AI 어시스턴트이다.
아래 메트릭 요약(CPU, NetworkIn, NetworkOut)을 바탕으로
JSON 리포트를 작성하라:

{
    "status": "OK" | "WARNING" | "CRITICAL",
    "summary": "3문장 이하 요약",
    "suspected_causes": ["원인1", "원인2"],
    "recommended_actions": ["조치1", "조치2"]
}
"""


def build_ai_prompt(metric_summary):
    m = metric_summary["metrics"]
    fmt = lambda x: "N/A" if x is None else round(x, 2)

    lines = [
        f"기간: 최근 {metric_summary['period_minutes']}분",
        f"시간 범위: {metric_summary['time_range_utc']['start']} ~ {metric_summary['time_range_utc']['end']}",
        "",
        f"CPU 평균: {fmt(m['CPUUtilization']['average'])}, 최대: {fmt(m['CPUUtilization']['maximum'])}",
        f"NetworkIn 평균: {fmt(m['NetworkIn']['average'])}, 최대: {fmt(m['NetworkIn']['maximum'])}",
        f"NetworkOut 평균: {fmt(m['NetworkOut']['average'])}, 최대: {fmt(m['NetworkOut']['maximum'])}",
        "",
        "현재 인스턴스 상태를 리포트 형태로 평가해줘.",
    ]
    return "\n".join(lines)


# ==========================
# Bedrock Haiku 호출
# ==========================
def call_haiku(metric_summary):

    payload = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {"text": AI_ANALYZE_SYSTEM_PROMPT},
                    {"text": build_ai_prompt(metric_summary)},
                ],
            }
        ],
        "inferenceConfig": {
            "maxTokens": 400,
            "temperature": 0.3,
        }
    }

    resp = bedrock.converse(
        modelId=MODEL_ID,
        messages=payload["messages"],
        inferenceConfig=payload["inferenceConfig"]
    )

    text = resp["output"]["message"]["content"][0]["text"]

    try:
        return json.loads(text)
    except:
        return {
            "status": "WARNING",
            "summary": "AI 응답을 파싱하지 못함",
            "suspected_causes": ["JSON 형식 오류"],
            "recommended_actions": ["프롬프트 수정 필요"],
            "raw": text,
        }


# ==========================
# SNS 알람 발송
# ==========================
def send_alert(metric_summary, ai_result):
    global LAST_ALERT_TS

    now = time.time()
    if now - LAST_ALERT_TS < ALERT_COOLDOWN_SECONDS:
        return {
            "alert_sent": False,
            "reason": "cooldown",
            "cooldown_remaining": ALERT_COOLDOWN_SECONDS - int(now - LAST_ALERT_TS),
        }

    cpu = metric_summary["metrics"]["CPUUtilization"]
    avg, mx = cpu["average"], cpu["maximum"]

    cpu_cond = (avg and avg > 70) or (mx and mx > 90)
    ai_cond = ai_result.get("status") == "CRITICAL"

    if not (cpu_cond or ai_cond):
        return {"alert_sent": False, "reason": "no_condition_matched"}

    subject = "[EC2 ALERT] CPU 또는 AI 경고 감지"
    message = json.dumps(ai_result, ensure_ascii=False, indent=2)

    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject=subject,
        Message=message,
    )

    LAST_ALERT_TS = now
    return {"alert_sent": True, "subject": subject}


# ==========================
# /analyze
# ==========================
@app.route("/analyze")
def analyze():
    global LAST_ANALYZE_TS

    now = time.time()
    if now - LAST_ANALYZE_TS < ANALYZE_COOLDOWN_SECONDS:
        return jsonify({
            "status": "TOO_FREQUENT",
            "retry_after_seconds": ANALYZE_COOLDOWN_SECONDS - int(now - LAST_ANALYZE_TS),
        }), 429

    LAST_ANALYZE_TS = now

    minutes = int(request.args.get("minutes", 60))

    metric_summary = get_metric_summary(INSTANCE_ID, REGION, minutes)
    ai_result = call_haiku(metric_summary)
    alert = send_alert(metric_summary, ai_result)

    return jsonify({
        "status": "OK",
        "metric_summary": metric_summary,
        "ai_report": ai_result,
        "alert": alert,
        "minutes": minutes,
    })


# ==========================
# 실행
# ==========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
