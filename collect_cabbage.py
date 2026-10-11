
import os
import time
import requests
import pandas as pd

# 환경변수에서 API 인증키 가져오기
SERVICE_KEY = os.getenv("DATA_API_KEY")

if not SERVICE_KEY:
    raise ValueError(
        "DATA_API_KEY 환경변수를 설정해주세요."
    )

BASE_URL = "https://apis.data.go.kr/B552845/perDay/price"

VARIETIES = {
    "01": "봄",
    "02": "여름(고랭지)",
    "03": "가을",
    "06": "월동"
}

all_data = []

for year in range(2015, 2025):
    for code, name in VARIETIES.items():
        params = {
            "serviceKey": SERVICE_KEY,
            "pageNo": 1,
            "numOfRows": 200,
            "returnType": "JSON",
            "cond[exmn_ymd::GTE]": f"{year}0101",
            "cond[exmn_ymd::LTE]": f"{year}1231",
            "cond[se_cd::EQ]": "02",
            "cond[ctgry_cd::EQ]": "200",
            "cond[item_cd::EQ]": "211",
            "cond[grd_cd::EQ]": "04",
            "cond[sgg_cd::EQ]": "1101",
            "cond[mrkt_cd::EQ]": "0110211",
            "cond[vrty_cd::EQ]": code
        }

        try:
            response = requests.get(
                BASE_URL,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()

            body = result.get("response", {}).get("body", {})
            total_count = int(body.get("totalCount", 0) or 0)
            items = body.get("items", [])

            if isinstance(items, dict):
                items = items.get("item", [])

            if isinstance(items, dict):
                items = [items]
            elif not isinstance(items, list):
                items = []

            for item in items:
                item["수집연도"] = year
                item["품종"] = name
                item["품종코드"] = code
                all_data.append(item)

            print(
                f"{year}년 {name}: "
                f"API 응답 {total_count}건"
            )

        except (requests.RequestException, ValueError) as e:
            print(f"{year}년 {name}: 오류 - {e}")

        time.sleep(0.1)

if all_data:
    df = pd.DataFrame(all_data)
    df.to_csv(
        "cabbage_price_2015_2024.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print("\n데이터 수집 완료")
    print(f"저장한 행 수: {len(df)}")
    print("파일명: cabbage_price_2015_2024.csv")
    print(df.head())
else:
    print("\n수집된 데이터가 없습니다.")
    print("인증키와 API 응답을 확인해주세요.")