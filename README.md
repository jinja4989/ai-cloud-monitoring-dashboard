# 🟦 AI Cloud Monitoring Dashboard  
AWS CloudWatch + Flask 기반 실시간 클라우드 모니터링 대시보드

이 프로젝트는 **AWS EC2에서 구동되는 Flask 서버**를 활용해  
- CloudWatch 메트릭(CPU 5분 평균)  
- EC2 내부 실시간 CPU 사용량
- AI 기반 간단한 상태 분석 (`/analyze`)
- 지정된 조건에서 메시지 알림 전송 기

을 웹 대시보드 형태로 시각화하는 모니터링 시스템입니다.  
Chart.js를 이용해 1초 단위 실시간 업데이트가 이루어지며,  
발표/데모 상황에서 EC2에 부하를 주면 그래프가 즉각 반응하는 것이 특징입니다.

---

## 📌 주요 기능 요약

### 1. **CloudWatch CPU 메트릭 조회**
- Boto3 기반 CloudWatch Metrics API 호출  
- `/cpu` 경로에서 최근 CPU 평균 사용률 제공  
- 프론트엔드에서 1초 주기로 실시간 갱신  

### 2. **EC2 실시간 CPU 측정**
- psutil 기반 CPU Percent 측정  
- `/cpu_live`에서 JSON 형태로 실시간 반환  
- Chart.js로 실시간 그래프 구현 

  ### 3. **AI 기반 상태 분석(`/analyze`)**
- 현재 CPU 평균, 실시간 CPU 값 등을 기반으로 간단한 상태 분석 메시지를 반환  
- 예: “CPU 부하가 높습니다”, “시스템이 안정적입니다” 등  
- 백엔드에서 서버 상태를 요약해주는 엔드포인트  
- JSON 형태로 결과 제공 

### 4. **Chart.js 기반 시각화**
- 두 개의 독립된 라인 그래프  
  - CloudWatch CPU 5분 평균  
  - 실시간 CPU 사용량  
- 시간 축 자동 갱신  
- 발표용 데모 시 CPU 부하가 증가하면 바로 시각적으로 반응  

### 5. **메시지 알람 기능**
- 특정 조건(예: CPU 고부하 감지)에서 자동 알림 전송  
- 현재 버전에서는 간단한 텍스트 메시지 알림 기능 제공  
- 장애 상황을 빠르게 파악할 수 있도록 설계됨  
- 향후 Slack / 텔레그램 / 카카오톡 API로 확장 가능 

---

## 📁 프로젝트 구조

```plaintext
project_root/
├── app.py                 # Flask 백엔드 서버
├── analyze_cpu_with_haiku.py
├── get_cost.py
├── get_cpu.py
├── bedrock-call.py
├── get_cpu_metric.py
├── requorements.txt
└── static/
    └── index.html
```


# 🔧 사용 기술 (Tech Stack)
Backend

Python 3

Flask

Boto3 (CloudWatch API)

AWS

EC2

CloudWatch Metrics

Frontend

HTML / CSS / JavaScript

chart.js

---

# 🚀 실행 방법
## 1. 저장소 클론
```
git clone https://github.com/<your-id>/<your-repo>.git

cd <your-repo>
```

## 2. 필요한 패키지 설치
```
pip install -r requirements.txt
```

(만약 requirements.txt가 없다면 아래를 설치하세요)
```
pip install flask boto3
```

## 3. Flask 서버 실행
```
python3 app.py
```

### 서버가 실행되면 브라우저에서:
```
http://<EC2-퍼블릭-IP>:5000
```


### 접속하면 대시보드가 보입니다.

---

# ⚙️ API 엔드포인트 문서
## GET /cpu

### CloudWatch의 CPU 사용률(5분 평균)을 반환
```
{
  "status": "ok",
  "average_cpu": 12.8,
  "timestamp": "2025-12-04 12:33:21"
}
```

## GET /cpu_live

### EC2의 실시간 CPU 사용률을 반환
```
{
  "status": "ok",
  "cpu_percent": 37.5,
  "timestamp": "2025-12-04 12:33:22"
}
```

## GET /analyze

### 기능 
서버의 현재 상태를 기반으로 다음과 같은 분석 정보를 제공:

- 최근 CloudWatch CPU 평균 데이터  
- 실시간 CPU 지표  
- 간단한 상태 판정(정상 / 주의 / 고부하)  
- 프론트엔드에서 버튼 클릭 시 분석 결과를 화면에 표시하거나 로그에 출력할 수 있음
- 최근 60분 / 240분 분석 버튼 

### 예시 응답(JSON)
<img width="897" height="582" alt="image" src="https://github.com/user-attachments/assets/8d6e5726-ca7d-4386-bcde-82daa9c88025" />


## GET /alarm
### 알람 조건 충족시

<img width="912" height="601" alt="image" src="https://github.com/user-attachments/assets/93af4c41-a26e-411e-83ad-87bd99d64a33" />

### 경고 알람 이메일

<img width="1412" height="747" alt="image" src="https://github.com/user-attachments/assets/9ec33304-4437-41b6-b4b5-a47b0000bc77" />

---

## 🧪 시연(데모) 팁

### EC2에서 아래 명령으로 CPU 부하를 인위적으로 발생시킬 수 있습니다:

<img width="901" height="588" alt="1" src="https://github.com/user-attachments/assets/40952896-664d-4b97-a4c1-e4e5a509bf64" />
```
yes > /dev/null &
```

종료는:

<img width="908" height="592" alt="pkill" src="https://github.com/user-attachments/assets/c9db95a0-f763-409b-b47b-eedb98c6d20b" />
```
pkill yes
```

부하를 걸면 대시보드 실시간 그래프가 즉시 상승 & 부하를 지우면 그래프 즉시 하강

---

## 🎯 프로젝트 목표

-클라우드 환경에서 모니터링 시스템 구축 경험 습득

-Flask와 AWS API를 활용한 실시간 데이터 처리 구조 이해

-CloudWatch 지표를 직접 가져와 시각화하는 엔드투엔드 구성 경험

-프론트엔드(Chart.js) + 백엔드 + AWS 통합 아키텍처 구축 능력 확보

---

## 📌 향후 개선 아이디어

-메모리 / 디스크 / 네트워크 대역폭 모니터링 추가

-알람 기능 (Slack, 텔레그램, 카카오톡)

-Docker 컨테이너화 및 AWS ECS 배포

-전체 시스템 구조도 시각화 추가

---



# 🟦 AI Cloud Monitoring Dashboard  
Real-Time Cloud Monitoring Dashboard Powered by AWS CloudWatch + Flask

This project is a real-time monitoring dashboard built with a **Flask server running on AWS EC2**, providing:

- CloudWatch metrics (CPU 5-minute average)  
- Real-time EC2 CPU usage  
- Basic AI-driven system analysis (`/analyze`)  
- Automated alert messages when predefined conditions are triggered  

The dashboard visualizes all data using Chart.js and updates every second.  
When CPU load is applied to the EC2 instance, the graphs react instantly, making it ideal for demonstrations or presentations.

---

## 📌 Core Features

### 1. **CloudWatch CPU Metric Retrieval**
- Uses Boto3 to call CloudWatch Metrics API  
- `/cpu` endpoint returns the latest 5-minute average CPU usage  
- Frontend updates every second  

### 2. **Real-Time EC2 CPU Monitoring**
- Powered by psutil to measure live CPU percent  
- `/cpu_live` returns real-time CPU usage in JSON  
- Rendered through a real-time Chart.js line graph  

### 3. **AI-Based System Analysis (`/analyze`)**
- Combines CloudWatch CPU and live CPU metrics  
- Returns simple system status messages (e.g., **“High load”**, **“Stable system”**)  
- Useful for summarizing server health  
- Response is provided in JSON  

### 4. **Data Visualization with Chart.js**
- Two independent, auto-updating line charts  
  - CloudWatch 5-minute CPU average  
  - Real-time CPU usage  
- Time axis updates dynamically  
- Graphs react instantly when CPU load increases  

### 5. **Alert Message System**
- Automatically sends alert messages when CPU overload is detected  
- Currently provides simple text/email alerts  
- Designed to quickly notify potential system issues  
- Future expansion planned (Slack / Telegram / KakaoTalk alerts)

---

## 📁 Project Structure

```plaintext
project_root/
├── app.py                 # Flask backend server
├── analyze_cpu_with_haiku.py
├── get_cost.py
├── get_cpu.py
├── bedrock-call.py
├── get_cpu_metric.py
├── requirements.txt
└── static/
    └── index.html
```
# 🔧 Tech Stack
Backend
Python 3

Flask

Boto3 (CloudWatch API)

AWS
EC2

CloudWatch Metrics

Frontend
HTML / CSS / JavaScript

Chart.js

# 🚀 How to Run the Project
## 1. Clone the Repository
```
git clone https://github.com/<your-id>/<your-repo>.git
cd <your-repo>
```
## 2. Install Dependencies
```
pip install -r requirements.txt
```
(If requirements.txt is missing, install manually:)
```
pip install flask boto3
```
## 3. Run the Flask Server
```
python3 app.py
```
### Open in Browser:
```
http://<EC2-Public-IP>:5000
```
The dashboard will appear on the screen.

# ⚙️ API Endpoints
## GET /cpu
Returns CPU 5-minute average from CloudWatch
```
{
  "status": "ok",
  "average_cpu": 12.8,
  "timestamp": "2025-12-04 12:33:21"
}
```

## GET /cpu_live
Returns real-time CPU usage
```
{
  "status": "ok",
  "cpu_percent": 37.5,
  "timestamp": "2025-12-04 12:33:22"
}
```

## GET /analyze
Description
Provides a combined system analysis using:

Recent CloudWatch CPU data

Real-time CPU metrics

Status classification (Normal / Warning / High Load)

Frontend buttons support 60-minute & 240-minute analysis modes

### Example Response
<img width="897" height="582" src="https://github.com/user-attachments/assets/8d6e5726-ca7d-4386-bcde-82daa9c88025" />

## GET /alarm

### Triggered When Alert Conditions Are Met
<img width="912" height="601" src="https://github.com/user-attachments/assets/93af4c41-a26e-411e-83ad-87bd99d64a33" />

### Example Warning Email
<img width="1412" height="747" src="https://github.com/user-attachments/assets/9ec33304-4437-41b6-b4b5-a47b0000bc77" />

# 🧪 Demo Tips
Apply CPU Load on EC2:
<img width="901" height="588" src="https://github.com/user-attachments/assets/40952896-664d-4b97-a4c1-e4e5a509bf64" />
```
yes > /dev/null &
```

Stop Load:
<img width="908" height="592" src="https://github.com/user-attachments/assets/c9db95a0-f763-409b-b47b-eedb98c6d20b" />
```
pkill yes
```
The dashboard will instantly reflect the rising or dropping CPU load.

# 🎯 Project Goals
Build hands-on experience with cloud monitoring on AWS

Understand real-time data processing using Flask + AWS APIs

Implement end-to-end visualization of CloudWatch metrics

Learn integration between frontend (Chart.js), backend, and AWS

# 📌 Future Improvements
Add monitoring for memory, disk, and network throughput

Integrate Slack / Telegram / KakaoTalk alert notifications

Dockerize and deploy via AWS ECS

Add system architecture diagrams
