import json
from datetime import datetime

import requests

# 人员清单
members_list = ['梁福乐', '吕士义', '徐垚', '王文凯', '李琛', '林渤涵', '韩鑫涛', '邱恒', '杨成', '赵文祥', '刘贺',
                '盛仕祯']


# 获取 测试中的 需求列表
def requirements_list():
    headers = {
        'Content-Type': 'application/json',
        'Token': 'eyJhbGciOiJIUzI1NiJ9.eyJMT0dJTl9VU0VSX0tFWSI6IjgzNDIxMTcxLWJkNmMtNDRjZC04YzcxLWI3N2Y2YzEzNjQ3MyJ9.Blw9KoO_-0E_BtZd-25NS37Cj4tveIs77VjIyFtLqK0'
    }

    filter_parameters = {
        "pageNo": 1,
        "pageSize": 1000,
        "showType": 1,
        "projectId": 68,
        "stateNames": [],
        "managers": [],
        "creators": [],
        "participators": [],
        "states": [],
        "labels": []
    }

    # 需求列表 全量数据
    result_all = requests.post(headers=headers, url="https://teamcycle.100credit.cn/api/requirement/listPage",
                               json=filter_parameters)

    records_all = result_all.json().get("data", {}).get("records", [])

    # 1、过滤掉 没有测试人员 的数据
    # 2、过滤掉 没有测试时间 的数据
    first_filter_records_all = [
        item for item in records_all
        if (item_value := item.get("expandCols", {}).get("测试")) and item_value != '-' and "|" in item_value
    ]

    # 1、获取 测试人员在members中的数据
    # 2、获取 测试时间在当前时间范围内的数据
    second_filter_records_all = []

    for items in first_filter_records_all:
        item = items.get("expandCols", {}).get("测试")
        date_str, persons = item.split("|")

        date_parts = date_str.split("-")

        if len(date_parts) == 2:
            start_str, end_str = date_parts
        else:
            start_str = date_parts[0]
            end_str = date_parts[0]

        # 解析月份和日期
        start_month, start_day = map(int, start_str.split("/"))
        end_month, end_day = map(int, end_str.split("/"))

        now = datetime.now()
        year = now.year

        # 判断是否跨年
        if end_month < start_month:
            # 跨年情况
            # 如果当前月份 < 开始月份,说明已经进入新年,开始日期应该是去年
            if now.month < start_month:
                start_date = datetime(year - 1, start_month, start_day)
                end_date = datetime(year, end_month, end_day, 23, 59, 59)
            else:
                # 当前月份 >= 开始月份,说明还在当前年,结束日期是明年
                start_date = datetime(year, start_month, start_day)
                end_date = datetime(year + 1, end_month, end_day, 23, 59, 59)
        else:
            # 不跨年情况
            start_date = datetime(year, start_month, start_day)
            end_date = datetime(year, end_month, end_day, 23, 59, 59)

        # 解析人员列表
        person_list = persons.split(",")

        # 判断是否有交集
        if start_date <= now <= end_date and any(p in members_list for p in person_list):
            second_filter_records_all.append(items)

    print(json.dumps(second_filter_records_all, ensure_ascii=False, indent=4))


if __name__ == '__main__':
    requirements_list()
