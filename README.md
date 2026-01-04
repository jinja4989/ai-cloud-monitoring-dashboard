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
* **목적**: 실시간 그래프 구현 과 서버 자원(CPU) 사용률의 모니터링 경험을 / 접속, 과부하와 같은 로그 분석을 통해 조건부 자동 알람 경험을 쌓음.
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

## 🔥 트러블 슈팅 

<details>
<summary><b>1. EC2 Flask 서버 외부 접속 불가 문제</b></summary>

- **문제**: EC2에서 서버가 구동 중임에도 외부 브라우저에서 접속되지 않음.
- **원인**: AWS EC2 인바운드 규칙(Security Group)이 기본적으로 닫혀 있어 외부 트래픽을 차단함.
- **해결**: 인바운드 규칙에 Flask 기본 포트(5000)를 추가하고, 소스 범위를 `0.0.0.0/0`으로 설정하여 외부 접근을 허용함.

</details>

<details>
<summary><b>2. Chart.js 그래프 렌더링 오류 (비동기 처리)</b></summary>

- **문제**: 페이지 로드 시 차트가 나타나지 않거나 데이터가 표시되지 않음.
- **원인**: 프론트엔드 스크립트 실행 순서 오류로 인해, API 데이터를 수집하기 전 빈 데이터를 차트에 push하려고 시도함.
- **해결**: 데이터 Fetch 로직과 차트 렌더링 로직의 실행 순서를 조정하여, 데이터를 정상적으로 수신한 후 차트에 반영되도록 수정함.

</details>

<details>
<summary><b>3. 200 OK 응답에도 그래프 미출력 문제 (URL & 규격 불일치)</b></summary>

- **문제**: 서버 로그에는 정상 응답(200 OK)이 기록되나 브라우저 화면에는 변화가 없음.
- **원인**: `fetch` 경로가 상대 경로로 설정되어 발생한 주소 오류 및 서버 응답 JSON 구조와 프론트엔드 파싱 로직의 규격 불일치.
- **해결**: `fetch` 경로를 절대 경로로 고정하여 주소 오류를 방지하고, 백엔드 응답 데이터 포맷을 프론트엔드 요구 사양에 맞춰 통일함.

</details>

<details>
<summary><b>4. 파일 수정 과정에서의 인터페이스(JSON Key) 어긋남</b></summary>

- **문제**: 기능 추가 및 코드 수정 후 갑작스럽게 데이터 연동이 중단됨.
- **원인**: `app.py`(백엔드)와 `index.html`(프론트엔드)을 개별 수정하는 과정에서 JSON 데이터의 Key 이름이 서로 다르게 변경됨.
- **해결**: 양쪽 파일의 데이터 인터페이스 구조를 전수 점검하여 JSON Key 명칭을 하나로 통일함.

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
```
## 🎯 프로젝트 목표 및 향후 계획
[x] AWS Boto3를 활용한 클라우드 메트릭 수집 파이프라인 구축

[x] 실시간 데이터 시각화 및 AI 분석 기능 통합

[ ] Slack / Telegram API 연동을 통한 알람 채널 다각화

[ ] AWS ECS / EKS 배포 환경으로 확장
