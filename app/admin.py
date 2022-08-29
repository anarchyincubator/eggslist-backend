from django.contrib import admin
from django.contrib.admin.apps import AdminConfig


class EggslistAdminSite(admin.AdminSite):
    def get_app_list(self, request):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        models_ordering = {
            "ProductArticle": 1,
            "Category": 2,
            "Subcategory": 3,
            "UserViewTimestamp": 4,
            "BlogArticle": 1,
            "BlogCategory": 2,
            "User": 1,
            "VerifiedSellerApplication": 2,
            "LocationCountry": 1,
            "LocationState": 2,
            "LocationCity": 3,
            "LocationZipCode": 4,
            "Testimonial": 5,
            "FAQ": 6,
            "Group": 1,
        }
        apps_ordering = {"store": 1, "blogs": 2, "users": 3, "site_configuration": 4, "auth": 5}

        app_dict = self._build_app_dict(request)
        app_list = sorted(app_dict.values(), key=lambda x: x["name"].lower())
        app_list = list(filter(lambda x: x["app_label"] in apps_ordering, app_list))
        app_list.sort(key=lambda x: apps_ordering[x["app_label"]])

        for app in app_list:
            app["models"].sort(key=lambda x: models_ordering[x["object_name"]])

        return app_list


class EggslistAdminConfig(AdminConfig):
    default_site = "app.admin.EggslistAdminSite"
