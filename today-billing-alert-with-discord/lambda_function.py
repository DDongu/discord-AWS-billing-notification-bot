import boto3
import datetime
import json
import urllib3

DISCORD_WEBHOOK_URL = "디스코드_웹훅_URL"

def lambda_handler(event, context):
    try:
        start = '2025-04-01'                                    # 비용 조회 시작일자
        end = datetime.datetime.utcnow().strftime('%Y-%m-%d')   # 비용 조회 마지막일자

        client = boto3.client('ce', region_name='us-east-1')

        response = client.get_cost_and_usage(
            TimePeriod={
                'Start': start,
                'End': end
            },
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],
            GroupBy=[
                {'Type': 'DIMENSION', 'Key': 'SERVICE'}
            ]
        )

        total = 0.0
        service_costs = []
        for group in response['ResultsByTime'][0]['Groups']:
            service = group['Keys'][0]
            amount = float(group['Metrics']['UnblendedCost']['Amount'])
            total += amount
            service_costs.append((service, amount))

        # Discord 메시지 구성
        content = f"📊 **AWS 사용량 리포트 ({start} ~ {end})**\n\n"
        for service, cost in sorted(service_costs, key=lambda x: -x[1])[:5]:
            content += f"• {service}: `${cost:.2f}`\n"
        content += f"\n💰 **총 사용량: ${total:.2f}**"

        # Discord로 전송
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