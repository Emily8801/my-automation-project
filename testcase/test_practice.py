import requests


def test_user_detail():
    """查询用户详情接口，校验状态码和返回字段"""
    user_id = 1
    url = f"https://jsonplaceholder.typicode.com/users/{user_id}"

    # 1. 发请求：网络异常单独捕获，转成明确的断言失败
    try:
        resp = requests.get(url, timeout=10)
    except requests.exceptions.RequestException as e:
        raise AssertionError(f"请求接口失败：{e}") from e

    # 2. 校验状态码
    assert resp.status_code == 200, f"预期200，实际状态码：{resp.status_code}"

    result = resp.json()

    # 3. 校验三个字段 key 必须存在
    for key in ["id", "name", "phone"]:
        assert key in result, f"返回报文缺失字段：{key}"

    # 4. 校验返回的 id 与请求一致
    assert result["id"] == user_id, \
        f"返回id和请求不一致，预期{user_id}，实际{result['id']}"