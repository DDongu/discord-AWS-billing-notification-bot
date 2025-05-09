import json
import urllib3
import re

DISCORD_WEBHOOK_URL = "디스코드_웹훅_URL"

def lambda_handler(event, context):
    try:
        # SNS 메시지 원문
        raw_message = event['Records'][0]['Sns']['Message']
        print("Raw message:", raw_message)

        # 예산 이름
        budget_name_match = re.search(r"Budget Name:\s*(.+)", raw_message)
        budget_name = budget_name_match.group(1) if budget_name_match else "Unknown"

        # 현재 사용 금액
        cost_match = re.search(r"ACTUAL Amount:\s*\$([0-9.]+)", raw_message)
        cost_amount = cost_match.group(1) if cost_match else "0.00"

        # 예산 한도
        limit_match = re.search(r"Budgeted Amount:\s*\$([0-9.]+)", raw_message)
        budget_limit = limit_match.group(1) if limit_match else "??"

        # 임계값
        threshold_match = re.search(r"Alert Threshold:\s*>\s*\$([0-9.]+)", raw_message)
        threshold = threshold_match.group(1) if threshold_match else "??"

        # 메시지 구성
        content = (
            f"⚠️ **AWS 비용 경고** ⚠️\n"
            f"[**{budget_name}**] ❗ **${threshold} 초과** ❗\n"
            f"현재 사용액: `${cost_amount}`  / 예산 한도: `${budget_limit}`"
        )

        # Discord 전송
        http = urllib3.PoolManager()
        http.request(
            "POST",
            DISCORD_WEBHOOK_URL,
            body=json.dumps({"content": content}),
            headers={"Content-Type": "application/json"}
        )

        return {"statusCode": 200}

    except Exception as e:
        print("Error:", str(e))
        return {"statusCode": 500, "body": str(e)}