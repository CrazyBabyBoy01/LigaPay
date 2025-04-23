from django import template


# Этот файл нужен для кастомных фильтров, например в Моих услугах правильно подставлять URL для карточек

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_class_name(obj):
    return obj.__class__.__name__


@register.simple_tag
def get_route_map():
    return {
        "RPService": "products:riot-points_detail",
        "AccountService": "products:accounts_detail",
        "BoostService": "products:boost_detail",
        "TrainingService": "products:training_detail",
        "BattlePassService": "products:battlepass_detail",
        "DonationService": "products:donation_detail",
        "GeneralService": "products:services_detail",
        "QualificationService": "products:qualification_detail",
        "OtherService": "products:other_detail",
    }


@register.simple_tag
def get_viewname(service, route_map):
    """
    Возвращает имя представления на основе типа объекта service.
    """
    key = service.__class__.__name__
    return route_map.get(key, "")
