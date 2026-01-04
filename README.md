# 🤖 AI Cloud Monitoring Dashboard
> **AWS CloudWatch + Bedrock AI 기반 실시간 클라우드 모니터링 및 자동 분석 시스템**

이 프로젝트는 AWS EC2 환경에서 **Flask** 서버를 구동하여, **CloudWatch** 메트릭과 실시간 **psutil** 데이터를 수집하고, **AWS Bedrock(Claude)**을 통해 서버 상태를 지능적으로 분석하여 리포팅하는 엔드투엔드 모니터링 솔루션입니다.

---

## 📌 목차
1. [프로젝트 개요](#-프로젝트-개요)
2. [기술 스택](#-기술-스택)
3. [🔥 트러블 슈팅 (핵심 경험)](#-트러블-슈팅-핵심-경험)
4. [주요 기능 및 API](#-주요-기능-및-api)
5. [🧪 데모 및 실행 방법](#-데모-및-실행-방법)
6. [🎯 프로젝트 목표 및 향후 계획](#-프로젝트-목표-및-향후-계획)

---

## 📖 프로젝트 개요
* **목적**: 인프라 관리자가 수많은 지표를 직접 해석하는 수고를 덜고, AI가 정제된 인사이트를 제공하여 즉각적인 의사결정을 돕는 시스템 구축.
* **핵심 가치**: 실시간 시각화(Chart.js) + AI 기반 지능형 리포팅 + 조건부 자동 알람.

---

## 🛠 기술 스택
### Backend / Cloud
- **Language**: ![Python](https://img.shields.io/badge/python-3670A0?style=flat-square&logo=python&logoColor=ffdd54)
- **Framework**: ![Flask](https://img.shields.io/badge/flask-%23000.svg?style=flat-square&logo=flask&logoColor=white)
- **Infrastructure**: ![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=flat-square&logo=amazon-aws&logoColor=white) (EC2, CloudWatch, Bedrock, SES)
- **Libraries**: Boto3, psutil, Chart.js

### DevOps
- **Container**: ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat-square&logo=docker&logoColor=white) ![Docker Compose](https://img.shields.io/badge/Docker_Compose-2496ED?style=flat-square&logo=docker&logoColor=white)

---

## 🔥 트러블 슈팅 (핵심 경험)

<details>
<summary><b>1. AI 응답 데이터 파싱 및 형식 고정 문제</b></summary>

- **문제점**: Bedrock AI가 분석 결과를 제공할 때 응답 형식이 일정하지 않아 웹 대시보드 파싱 에러 발생.
- **해결책**: 
    - **Prompt Engineering**: 시스템 프롬프트에 JSON 출력 형식을 명시적으로 지정하고 Few-shot 예시 제공.
    - **Validation**: Python 코드에서 JSON 정합성을 체크하는 로직 추가.
- **결과**: AI 분석 결과의 웹 연동 성공 및 데이터 신뢰도 확보.

<img width="435" alt="AI Prompt" src="https://github.com/user-attachments/assets/dd9c6ca7-e425-4d05-b9f1-62451f2f1569">

</details>

<details>
<summary><b>2. CloudWatch 지연(5분) 보완을 위한 실시간 지표 도입</b></summary>

- **문제점**: CloudWatch Metrics API는 기본 5분 단위 데이터라 실시간 장애 대응에 한계가 있음.
- **해결책**: `psutil` 라이브러리를 사용해 인스턴스 내부의 1초 단위 실시간 CPU 사용량 지표를 병행 수집.
- **결과**: 대시보드에서 실시간 부하 상태를 즉각 확인 가능(Chart.js 실시간 갱신).

</details>

---

## 🚀 주요 기능 및 API

### 1. 실시간 모니터링 (Chart.js)
- `/cpu`: CloudWatch의 5분 평균 데이터 반환
- `/cpu_live`: EC2의 1초 단위 실시간 CPU 점유율 반환
- **특징**: 부하 발생 시 그래프가 즉각적으로 반응하여 시각적 인지 능력 극대화.

### 2. AI 기반 상태 분석 (`/analyze`)
현재 CPU 메트릭을 바탕으로 AI가 시스템 상태를 판정하고 운영 리포트를 작성합니다.
- **엔드포인트**: `GET /analyze`
- **결과 예시**:
<img width="897" alt="Analyze Result" src="https://github.com/user-attachments/assets/8d6e5726-ca7d-4386-bcde-82daa9c88025">

### 3. 지능형 알람 시스템 (`/alarm`)
특정 조건(고부하 등) 충족 시 AI 분석 내용을 포함한 알람을 발송합니다.
- **경보 이미지**:
<img width="912" alt="Alarm Trigger" src="https://github.com/user-attachments/assets/93af4c41-a26e-411e-83ad-87bd99d64a33">
- **이메일 리포트**:
<img width="1412" alt="Email Report" src="https://github.com/user-attachments/assets/9ec33304-4437-41b6-b4b5-a47b0000bc77">

---

## 🧪 데모 및 실행 방법

### 1. Docker 기반 실행 (권장)
```bash
# 저장소 클론
git clone [https://github.com/jinja4989/ai-cloud-monitoring-dashboard.git](https://github.com/jinja4989/ai-cloud-monitoring-dashboard.git)
cd ai-cloud-monitoring-dashboard

# Docker Compose 실행
docker compose up --build
서버 접속: http://localhost:5000 (또는 EC2 퍼블릭 IP)

2. CPU 부하 시뮬레이션
데모 중 그래프의 실시간 변화를 확인하려면 아래 명령어를 사용하세요.

부하 발생: yes > /dev/null &

부하 중지: pkill yes

<img width="901" alt="Load Test" src="https://github.com/user-attachments/assets/40952896-664d-4b97-a4c1-e4e5a509bf64">

🎯 프로젝트 목표 및 향후 계획
[x] AWS Boto3를 활용한 클라우드 메트릭 수집 파이프라인 구축

[x] 실시간 데이터 시각화 및 AI 분석 기능 통합

[ ] Slack / Telegram API 연동을 통한 알람 채널 다각화

[ ] AWS ECS / EKS 배포 환경으로 확장
