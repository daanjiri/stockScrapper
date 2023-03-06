import json
import requests
from bs4 import BeautifulSoup
import boto3
from datetime import datetime, timedelta


def lambda_handler(event, context):
    # TODO implement

    s3 = boto3.resource("s3")

    name = event['pathParameters']['symbol']

    start_date = datetime(2023, 3, 5, 0, 0, 0)
    end_date = datetime(2023, 3, 5, 23, 59, 59)
    
    utc_now =  datetime.utcnow()
    col_offset = timedelta(hours=-5) 
    check_date = utc_now + col_offset
    
    print('fecha',check_date)

    if start_date <= check_date <= end_date:
        print('entra-----------------------------------------------')

        try:
            s3_object = s3.Object("stock-cloud", f"{name}.json").get()
            file_content = json.loads(s3_object["Body"].read().decode("utf-8"))
        except:
            file_content = {
                'array': [],
                'position': 0
            }

        position = file_content['position']
        stock = file_content["array"][position]
        if position >= (len(file_content["array"])-1):
            file_content["position"] = 0
        else:
            file_content["position"] = position + 1

        s3.Object("stock-cloud", f"{name}.json").put(Body=json.dumps(file_content))

        return {
            'statusCode': 200,
            'body': json.dumps(stock)
        }

    else:
        print('Else-entra-----------------------------------------------')
        url = f"https://www.marketwatch.com/investing/stock/{name}?mod=search_symbol"
        response = requests.get(url, headers={'Cache-Control': 'no-cache'})
        soup = BeautifulSoup(response.text, 'html.parser')

        price = soup.findAll("h2", {"class": "intraday__price"})[
            0].find('bg-quote').text
        movement = soup.findAll("span", {"class": "change--point--q"})[
            0].find('bg-quote').text

        stock = {
            'price': price,
            'movement': movement
        }

        try:
            s3_object = s3.Object("stock-cloud", f"{name}.json").get()
            file_content = json.loads(s3_object["Body"].read().decode("utf-8"))
        except:
            file_content = {
                'array': [],
                'position': 0
            }

        print('stock', stock)
        print('file_content', file_content)

        file_content["array"].append(stock)

        # Upload the modified file back to S3
        s3.Object("stock-cloud", f"{name}.json").put(Body=json.dumps(file_content))

        return {
            'statusCode': 200,
            'body': json.dumps(stock)
        }
