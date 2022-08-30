import requests

def bucketTraffic(bucket, start, end):
    header = {"Authorization" : "Basic c3lzYWRtaW46cHVibGlj"}

    BI_url = f"https://172.16.30.5:19443/usage?bucket={bucket}&operation=BI&startTime={start}0000&endTime={end}0000&granularity=month"
    BI_response = requests.get(BI_url, headers = header, verify = False)

    BO_url = f"https://172.16.30.5:19443/usage?bucket={bucket}&operation=BO&startTime={start}0000&endTime={end}0000&granularity=month"
    BO_response = requests.get(BO_url, headers = header, verify = False)

    return {'BI': str(BI_response.content, 'UTF-8'), 'BO': str(BO_response.content, 'UTF-8')}