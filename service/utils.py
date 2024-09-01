class QuestionsManager:
    session = None

    def __init__(self, session) -> None:
        self.session = session

    async def add_question(self, text): ...

    async def remove_question(self, id_): ...

    async def deactivate_question(self, id_):
        pass

    async def find_all_answers(self, q_id): ...

    async def find_correct_answer(self, q_id): ...

    async def get_question(self, id_): ...

    async def get_all_questions(self): ...


class AnswersManager:
    session = None

    def __init__(self, session) -> None:
        self.session = session

    async def add_answer(self, text, question_id): ...

    async def remove_answer(self, id_): ...

    async def get_answer(self, ans_id): ...

    async def get_answers_for_question(self, q_id): ...
