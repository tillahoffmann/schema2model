from pydantic import RootModel


class StringList(RootModel[list[str]]):
    pass


class IntMapping(RootModel[dict[str, int]]):
    pass
