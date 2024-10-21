import asyncio
import aiohttp


URL_START = "http://localhost:8000"


async def load_json_post_handler(url, data=None):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            url, data=data, headers={"Content-Type": "application/json"}
        ) as resp:
            json_resp = await resp.json()
            print(json_resp)
            return json_resp


async def load_json_put_handler(url, data=None):
    async with aiohttp.ClientSession() as session:
        async with session.put(
            url, data=data, headers={"Content-Type": "application/json"}
        ) as resp:
            json_resp = await resp.json()
            print(json_resp)
            return json_resp


async def load_json_delete_handler(url, kwargs=None):
    async with aiohttp.ClientSession() as session:
        async with session.delete(
            url,
            # **kwargs,
            headers={"Content-Type": "application/json"},
        ) as resp:
            json_resp = await resp.json()
            print(json_resp)
            return json_resp


async def load_quiz():
    url = URL_START + "/v1/show-quiz"
    data = """{
        "active": 1,
        "limit": 50,
        "offset": 0,
        "order": "updated_dt",
        "text": "question"
    }"""
    return await load_json_post_handler(url, data)
    

async def load_questions():
    url = URL_START + "/v1/questions"
    data = """{
        "active": 1,
        "limit": 50,
        "offset": 0,
        "order": "updated_dt"
    }"""
    # "text": "question"
    return await load_json_post_handler(url, data)


async def add_question():
    url = URL_START + "/v1/add-question"
    data = """{
        "active": 1,
        "text": "question"
    }"""
    return await load_json_post_handler(url, data)


async def add_answer():
    url = URL_START + "/v1/add-answer"
    data = """{
         "correct": true,
        "question_id": 1,
        "text": "answer"
    }"""
    return await load_json_post_handler(url, data)


async def submit_answer():
    ans_id = 36
    url = URL_START + "/v1/submit-answer" + "?question_id={}".format(ans_id)
    data = """[0]
           """
    return await load_json_post_handler(url, data)


async def edit_question():
    q_id = 36
    text = "sdwrgv dvw?"
    active = 1
    url = (
        URL_START
        + "/v1/edit-question"
        + "?id={}&text={}&active={}".format(q_id, text, active)
    )
    data = """[0]
           """
    return await load_json_put_handler(url, data)


async def delete_question():
    q_id = 35
    url = URL_START + "/v1/delete-question" + "?id={}".format(q_id)
    return await load_json_delete_handler(url)


async def delete_answer():
    a_id = 35
    url = URL_START + "/v1/delete-answer" + "?id={}".format(a_id)
    return await load_json_delete_handler(url)


async def get_keyboard():
    ...
