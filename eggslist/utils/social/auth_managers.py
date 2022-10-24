import typing as t

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.images import ImageFile
from django.core.files.temp import NamedTemporaryFile
from requests_oauthlib import OAuth2Session

from eggslist.utils.social import adapters

if t.TYPE_CHECKING:
    from django.http import QueryDict

User = get_user_model()


class SocialAuthManager:
    api_base_url: str = None
    api_token_url: str = None
    api_user_profile_url: str = None
    client_id: str = None
    client_secret: str = None
    scope_adapter_class: adapters.ScopeAdapter = None
    user_fields_adapter_class: adapters.APIFieldAdapter = None
    redirect_url: str = None
    scope: t.Optional[t.List[str]] = None

    def __init__(self):
        oauth_client_kwargs = {"client_id": self.client_id, "redirect_uri": self.redirect_url}

        if self.scope is not None and self.scope_adapter_class is not None:
            oauth_client_kwargs.update(scope=self.scope_adapter_class(self.scope).as_list())

        self.client = OAuth2Session(**oauth_client_kwargs)

    def get_authorization_url(self) -> str:
        url, state = self.client.authorization_url(self.api_base_url)
        return url

    def get_social_profile(self, query_params: "QueryDict") -> t.Dict:
        self.client.fetch_token(
            token_url=self.api_token_url,
            client_secret=self.client_secret,
            authorization_response=f"{self.redirect_url}?{query_params.urlencode()}",
        )
        user_data = self.client.get(self.api_user_profile_url).json()
        return user_data

    def process_user_avatar(self, user_kwargs) -> t.Dict:
        image_url = user_kwargs["avatar"]

        r = requests.get(url=image_url)

        image_name = image_url.split("/")[-1]
        image_name = f"{image_name}.jpg" if "." not in image_name else image_name

        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(r.content)
        img_temp.flush()

        avatar = ImageFile(file=img_temp, name=image_name)
        user_kwargs["avatar"] = avatar
        return user_kwargs

    def process_user_kwargs(self, user_kwargs) -> t.Dict:
        if "avatar" in user_kwargs:
            user_kwargs = self.process_user_avatar(user_kwargs)

        return user_kwargs

    def get_or_create_user(self, social_user_profile: t.Dict) -> "User":
        adapter = self.user_fields_adapter_class(social_user_profile.keys())
        kwargs = adapter.map_object(social_user_profile)
        kwargs = self.process_user_kwargs(kwargs)

        kwargs.pop("social_id")

        try:
            user = User.objects.get(email=kwargs["email"])
        except User.DoesNotExist:
            user = User.objects.create_user(**kwargs)

        return user


class GoogleSocialManager(SocialAuthManager):
    api_base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    api_token_url = "https://www.googleapis.com/oauth2/v4/token"
    api_user_profile_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    client_id = settings.GOOGLE_CLIENT_ID
    client_secret = settings.GOOGLE_SECRET_KEY
    redirect_url = f"{settings.SITE_URL}/{settings.GOOGLE_AUTH_REDIRECT_URL}"
    scope_adapter_class = adapters.GoogleScopeAdapter
    user_fields_adapter_class = adapters.GoogleAPIFieldAdapter
    scope = settings.GOOGLE_OAUTH_SCOPE


class FacebookSocialManager(SocialAuthManager):
    api_base_url = "https://www.facebook.com/dialog/oauth"
    api_token_url = "https://graph.facebook.com/oauth/access_token"
    api_user_profile_url = (
        "https://graph.facebook.com/me?fields=first_name, last_name, email, picture"
    )
    client_id = settings.FACEBOOK_CLIENT_ID
    client_secret = settings.FACEBOOK_SECRET_KEY
    redirect_url = f"{settings.SITE_URL}/{settings.FACEBOOK_AUTH_REDIRECT_URL}"
    scope_adapter_class = adapters.FacebookScopeAdapter
    user_fields_adapter_class = adapters.FacebookAPIFieldAdapter
    scope = settings.FACEBOOK_OAUTH_SCOPE

    def process_user_kwargs(self, kwargs) -> t.Dict:
        new_kwargs = kwargs.copy()
        new_kwargs["avatar"] = new_kwargs["avatar"]["data"]["url"]
        super().process_user_kwargs(new_kwargs)
        return new_kwargs
