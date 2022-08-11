class BaseAdapter:
    mapping: dict = None
    _available_items: list = None

    def __init__(self, items_to_map: list):

        if set(items_to_map).intersection(set(self._available_items)) != set(items_to_map):
            raise ValueError(
                f"For this class you can choose any of provided items: {', '.join(self._available_items)}"
            )
        if len(items_to_map) == 0:
            raise ValueError("Please provide at least one item")

        self.items_to_map = items_to_map
        super().__init__()

    def __iter__(self):
        self._i = 0
        return self

    def __next__(self):
        if self._i > len(self.items_to_map) - 1:
            raise StopIteration

        item = self.mapping[self.items_to_map[self._i]]

        self._i += 1

        return item

    def __repr__(self):
        return "[" + ", ".join(self.items_to_map) + "]"

    def as_list(self):
        return list(self)


class ScopeAdapter(BaseAdapter):
    _available_items = ["openid", "email", "profile"]


class APIFieldAdapter(BaseAdapter):
    _available_items = ["id", "email", "verified_email", "first_name", "last_name", "avatar"]

    def __init__(self, items):
        items = set(items).intersection(set(self._available_items))
        super().__init__(items)

    def __getitem__(self, key):
        return self.mapping[key]

    def map_object(self, object):
        new_object = {}

        for k, v in object.items():
            if k not in self.mapping:
                continue

            new_object[self[k]] = v

        return new_object


class GoogleScopeAdapter(ScopeAdapter):
    mapping = {
        "openid": "openid",
        "email": "https://www.googleapis.com/auth/userinfo.email",
        "profile": "https://www.googleapis.com/auth/userinfo.profile",
    }


class GoogleAPIFieldAdapter(APIFieldAdapter):
    mapping = {
        "id": "social_id",
        "email": "email",
        "given_name": "first_name",
        "family_name": "last_name",
        "picture": "avatar",
    }


class FacebookScopeAdapter(ScopeAdapter):
    mapping = {"email": "email", "profile": "public_profile"}


class FacebookAPIFieldAdapter(APIFieldAdapter):
    mapping = {
        "id": "social_id",
        "email": "email",
        "first_name": "first_name",
        "last_name": "last_name",
        "picture": "avatar",
    }
