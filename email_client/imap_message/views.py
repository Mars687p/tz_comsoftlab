from django.db.models.query import QuerySet
from django.views.generic import ListView

from .models import MessageModel


class MessageViews(ListView):
    model = MessageModel
    template_name = 'imap_message/index.html'

    def get_queryset(self) -> QuerySet:
        return MessageModel.get_queryset(self.request.user.id,
                                         self.kwargs.get('mail_client_id')
                                         )
