class ApiDetail:
    def __init__(self, api_name: str, api_roots: list[str], api_type: str = 'method'):
        self.api_name = api_name
        self.api_roots = api_roots
        self.api_type = api_type

    def is_api_type_class(self):
        return self.api_type == 'class'

    def is_api_type_method(self):
        return self.api_type == 'method'
