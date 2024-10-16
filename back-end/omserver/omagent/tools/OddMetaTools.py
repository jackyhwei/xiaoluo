
class OddMetaToolsBase():
    """
    基础自定义Tool类，允许向Tool传递额外的上下文信息。
    """
    _user_id = 0
    _original_input = "how old r u，怎么是老是你"

    def __init__(self, user_id: int, original_input: str) -> None:
        OddMetaToolsBase._user_id = user_id
        OddMetaToolsBase._original_input = original_input

    def setSessionState(self, user_id: int, original_input: str):
        OddMetaToolsBase._user_id = user_id
        OddMetaToolsBase._original_input = original_input
