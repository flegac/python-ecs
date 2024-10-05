class IdGenerator:
    def __init__(self):
        self._last_id = -1

    def new_id(self):
        self._last_id += 1
        return self._last_id

    def gen(self, n: int):
        return [self.new_id() for _ in range(n)]
