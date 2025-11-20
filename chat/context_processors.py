from .utils import get_unread_message_count


def unread_message_count(request):
    user = request.user
    if user.is_authenticated:
        count = get_unread_message_count(user)
        return {'unread_message_count': count}
    return {'unread_message_count': 0}
