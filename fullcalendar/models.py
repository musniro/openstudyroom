from django.db import models
from django.utils import timezone
from django.db.models import Q
from operator import attrgetter
import datetime
from league.models import User, Division
from postman.api import pm_broadcast

# Create your models here.


class CalEvent(models.Model):

    start = models.DateTimeField()
    end = models.DateTimeField()

    class Meta:
        abstract = True


class PublicEvent(CalEvent):
    title = models.CharField(max_length=30)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True)

    @staticmethod
    def get_future_public_events():
        """return a query of all future public events to a user."""
        now = timezone.now()
        public_events = PublicEvent.objects.filter(end__gte=now)
        return public_events


class AvailableEvent(CalEvent):
    user = models.ForeignKey(User)

    @staticmethod
    def get_formated_other_available(user, division_list):
        """Return the other-available events related to a user for the divisions
        in division_list

        First we create a changes list that contain dicts formated as such:
        {
            'time': datetime,
            'user': user,
            'type': 1 if the user becomes available 0 otherwise
        }
        Then we go over this changes list and create new events formated as such:
        {
            ‘start’:datetime,
            ‘end’: datetime,
            ‘users’: a list of users available at between start and end
        }
        """
        now = timezone.now()
        list_users = user.get_opponents(division_list)
        availables = AvailableEvent.objects.filter(
            end__gte=now,
            user__in=list_users
        )
        changes = []
        for event in availables:
            change = {
                'time': event.start,
                'user': event.user.kgs_username,
                'type': 1  # means the user becomes available
            }
            changes.append(change)
            change = {
                'time': event.end,
                'user': event.user.kgs_username,
                'type': 0  # means the user becomes unavailable
            }
            changes.append(change)
        changes = sorted(changes, key=lambda k: k['time'])

        events = []
        for idx, change in enumerate(changes):
            if idx == 0:
                time = change['time']
                list_users = [change['user']]
                continue

            if time == change['time']:
                # another change at the same moment.
                # We just add or remove a player
                if change['type'] == 1:  # user becomes available
                    list_users.append(change['user'])
                else:
                    list_users.remove(change['user'])
            else:
                if len(list_users) == 0:
                    if change['type'] == 1:
                        # we need to start a new event
                        time = change['time']
                        list_users.append(change['user'])
                else:
                    # we add the event to the events list
                    events.append({
                        'start': time,
                        'end': change['time'],
                        'users': [u for u in list_users]
                    })
                    time = change['time']
                    if change['type'] == 0:  # new user available
                        list_users.remove(change['user'])
                    else:
                        list_users.append(change['user'])
        return events


class GameRequestEvent(CalEvent):
    sender = models.ForeignKey(
        User,
        related_name="%(app_label)s_%(class)s_related_sender",
        related_query_name="%(app_label)s_%(class)ss_sender",
    )
    receivers = models.ManyToManyField(
        User,
        related_name="%(app_label)s_%(class)s_related_receiver",
        related_query_name="%(app_label)s_%(class)ss_receiver",
    )


class GameAppointmentEvent(CalEvent):
    users = models.ManyToManyField(
        User,
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)ss",
    )

    def title(self):
        users = self.users.all()
        return 'Game ' + users[0].kgs_username + ' vs ' + users[1].kgs_username

    def opponent(self,user):
        """Return the opponent of a game appointment"""
        return self.users.exclude(pk=user.pk).first()

    @staticmethod
    def get_future_games(user):
        """Return all the future game appointments for a user."""
        now = timezone.now()
        return user.fullcalendar_gameappointmentevent_related.filter(
            start__gte=now
        )
