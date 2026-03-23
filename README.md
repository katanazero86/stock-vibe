# Stock Vibe

Stock Vibe는 TradingView 스크리너 기반 주식 대시보드입니다.  
Playwright로 TradingView의 거래량 상위 종목 데이터를 크롤링하고, Python API로 제공한 뒤 React + TailwindCSS UI로 보여줍니다.

## 프로젝트 개요

현재 지원하는 화면:
- `us`: NASDAQ 종목만 표시
- `kospi`: KOSPI 종목만 표시

수집/표시 항목:
- 종목 코드(symbol)
- 종목명(company name)
- 현재가(current price)
- 전일 대비 등락률(change percent)
- 거래량(volume)
- 거래대금 성격의 `Price * Vol`(turnover-like)
- 크롤링 시각(crawl timestamp)

## TradingView 크롤링 대상 URL

현재 크롤링은 아래 TradingView 페이지를 기준으로 동작합니다.

- 미국 주식 원본 페이지:
  - [https://www.tradingview.com/markets/stocks-usa/market-movers-active/](https://www.tradingview.com/markets/stocks-usa/market-movers-active/)
- 한국 주식 원본 페이지:
  - [https://kr.tradingview.com/markets/stocks-korea/market-movers-active/](https://kr.tradingview.com/markets/stocks-korea/market-movers-active/)

실제 적용 규칙:
- `us`
  - TradingView 미국 페이지에서 읽어온 뒤 `NASDAQ:` 행만 남깁니다.
- `kospi`
  - TradingView 한국 페이지에서 읽어온 뒤 KRX KOSPI 상장사 목록에 있는 종목만 남깁니다.
  - 종목명은 KRX 메타데이터를 사용해 한글명으로 보강합니다.

## 기술 구성

- 백엔드
  - Python
  - FastAPI
  - Playwright
  - pandas
- 프론트엔드
  - React
  - Vite
  - TailwindCSS
- 데이터 보강
  - KRX 상장사 메타데이터

## 디렉터리 구조

```text
stock-vibe/
├─ stock_vibe/
│  ├─ api.py
│  ├─ config.py
│  ├─ crawler.py
│  ├─ market_metadata.py
│  ├─ models.py
│  ├─ parsing.py
│  ├─ service.py
│  └─ storage.py
├─ frontend/
│  ├─ src/
│  ├─ package.json
│  └─ tailwind.config.js
├─ data/
├─ memory-bank/
├─ pyproject.toml
└─ README.md
```

## 요구 사항

- Python `3.13+`
- Node.js `22+`
- npm
- Playwright Chromium

## 설치 방법

### 1. 백엔드 설치

프로젝트 루트에서 실행:

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e .
python -m playwright install chromium
```

### 2. 프론트엔드 설치

```bash
cd frontend
npm install
cd ..
```

## 실행 방법

### 1. 백엔드 실행

```bash
python -m uvicorn stock_vibe.api:app --reload
```

기본 주소:
- API: [http://localhost:8000](http://localhost:8000)

### 2. 프론트엔드 실행

새 터미널에서:

```bash
cd frontend
npm run dev
```

기본 주소:
- UI: [http://localhost:5173](http://localhost:5173)

## 프론트엔드 빌드

```bash
cd frontend
npm run build
```

## 동작 방식

1. 프론트엔드에서 시장(`us`, `kospi`)을 선택합니다.
2. 백엔드가 해당 시장에 맞는 TradingView 페이지를 Playwright로 엽니다.
3. TradingView 표에서 종목 데이터를 읽습니다.
4. 시장별 필터를 적용합니다.
   - 미국: NASDAQ만 유지
   - 한국: KOSPI만 유지
5. 한국 종목은 KRX 메타데이터로 한글 종목명을 보강합니다.
6. 결과를 시장별 CSV 캐시로 저장합니다.
7. 새 크롤링이 실패하면 마지막 성공 캐시를 fallback으로 사용합니다.

## API

### 상태 확인

```http
GET /api/health
```

### 지원 시장 목록

```http
GET /api/markets
```

### 캐시 데이터 조회

```http
GET /api/snapshot?market=us
GET /api/snapshot?market=kospi
```

### TradingView에서 새로 크롤링

```http
POST /api/refresh?market=us
POST /api/refresh?market=kospi
```

## 환경 변수

### 백엔드

- `STOCK_VIBE_DEFAULT_MARKET`
  - 기본 시장 키
  - `us` 또는 `kospi`
- `STOCK_VIBE_TOP_N`
  - 유지할 목표 행 수
  - 기본값: `50`
- `STOCK_VIBE_MAX_RETRIES`
  - 크롤링 재시도 횟수
- `STOCK_VIBE_BACKOFF_SECONDS`
  - 재시도 백오프 기본 초
- `STOCK_VIBE_JITTER_SECONDS`
  - 주요 액션 사이 랜덤 지연
- `STOCK_VIBE_PAGE_TIMEOUT_MS`
  - Playwright 페이지 타임아웃
- `STOCK_VIBE_HEADLESS`
  - `false`로 두면 브라우저를 눈으로 확인 가능
- `STOCK_VIBE_DATA_DIR`
  - 캐시, 로그, 세션 파일 저장 디렉터리

### 프론트엔드

- `VITE_API_BASE_URL`
  - 기본값: `http://localhost:8000`

## 데이터 파일

`data/` 아래에 시장별 파일이 생성됩니다.

- `data/us-latest-market-snapshot.csv`
- `data/us-crawl-log.json`
- `data/us-storage-state.json`
- `data/kospi-latest-market-snapshot.csv`
- `data/kospi-crawl-log.json`
- `data/kospi-storage-state.json`
- `data/kospi-company-map.json`

예전 단일 시장 버전 파일이 남아 있을 수 있습니다.

- `data/latest_market_snapshot.csv`
- `data/crawl_log.json`
- `data/tradingview-storage-state.json`

현재 코드는 시장별 파일을 우선 사용합니다.

## 참고 사항

- TradingView DOM 구조가 바뀌면 선택자 수정이 필요할 수 있습니다.
- 크롤러는 retry, backoff, session reuse, jitter를 사용해 차단 가능성을 낮춥니다.
- CAPTCHA 해결이나 강한 우회 로직에는 의존하지 않습니다.
- KOSPI 종목명은 KRX 메타데이터 기준으로 한글명으로 보강합니다.
- KOSPI 종목코드는 문자열로 유지해서 앞자리 `0`이 보존됩니다.
- 현재 TradingView country-level 페이지를 기준으로 필터링하기 때문에, 거래량 상위 결과가 항상 정확히 50건이 채워지지 않을 수 있습니다.

## 빠른 시작

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e .
python -m playwright install chromium
cd frontend
npm install
cd ..
python -m uvicorn stock_vibe.api:app --reload
```

새 터미널에서:

```bash
cd frontend
npm run dev
```
