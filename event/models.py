from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import Q

from base.enum import EventType, EventStatus, EventCategoryEnum, EventSubCategoryEnum
from base.models import BaseModel
from django.utils import timezone

from base.validators import CustomURLValidator


# Create your models here.

class EventModel(BaseModel):
    title = models.CharField(max_length=255, blank=False, null=False, help_text='Title of the event')
    description = models.TextField(blank=True, null=True, help_text='Description of the event')
    start_date = models.DateField(blank=True, null=True, help_text='Start date of the event')
    end_date = models.DateField(blank=True, null=True, help_text='End date of the event')
    is_all_day = models.BooleanField(default=False, help_text='Is this event all day')
    start_time = models.TimeField(blank=True, null=True, help_text='Start time of the event')
    end_time = models.TimeField(blank=True, null=True, help_text='End time of the event')
    event_image = models.ImageField(blank=True, null=True, upload_to="events/images", help_text='Image of the event')
    event_video = models.CharField(blank=True, null=True, max_length=700, help_text='Youtube video URL of the event')
    event_type = models.CharField(max_length=255, choices=EventType.choices(), blank=False, null=False, help_text='Type of the event')
    registration_available = models.BooleanField(default=False, help_text='Is this event registration available')
    registration_last_date = models.DateField(blank=True, null=True, help_text='Last date of the registration')
    registration_link =  models.CharField(
        validators=[CustomURLValidator()], max_length=700, blank=True, null=True,
        help_text="Registration link of the event"
    )

    # tags
    category = ArrayField(
        models.CharField(max_length=50, choices=EventCategoryEnum.choices()), default=list, blank=False, null=False
    )
    sub_category = ArrayField(
        models.CharField(max_length=50, choices=EventSubCategoryEnum.choices()), default=list, blank=False, null=False
    )

    # location
    meeting_link = models.URLField(help_text="Event online meeting link", blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True, help_text='Hosted country of the event')
    district = models.CharField(max_length=255, blank=True, null=True, help_text='Hosted district of the event')
    city = models.CharField(max_length=255, blank=True, null=True, help_text='Hosted city of the event')
    location = models.TextField(max_length=255, help_text="Event location", blank=True, null=True)
    location_link = models.CharField(
        max_length=700, blank=True, null=True,
        help_text='Location MAP URL of the event'
    )

    # additional data
    text_color = models.CharField(max_length=10, blank=True, null=True, help_text='Text color code of the event')
    bg_color = models.CharField(max_length=10, blank=True, null=True, help_text='Background color code of the event')
    status = models.CharField(max_length=100, choices=EventStatus.choices(),
                              default=EventStatus.PENDING.value, blank=True, null=True, help_text='Status of the event')
    admin_comment = models.TextField(blank=True, null=True, help_text='Admin comment for the event')

    class Meta:
        db_table = 'event'

    @property
    def get_image_name(self):
        return "event"


    def get_today_events(self):
        return self.active_objects.filter(
            Q(start_date__lte=timezone.now().date())|
            Q(end_date__gte=timezone.now().date())
        )

    def get_this_month_events(self):
        today = timezone.now().date()
        return self.active_objects.filter(
            Q(start_date__month=today.month, start_date__year=today.year)|
            Q(end_date__month=today.month, end_date__year=today.year)
        )
    def get_this_year_events(self):
        today = timezone.now().date()
        return self.active_objects.filter(
            Q(start_date__year=today.year)|
            Q(end_date__year=today.year)
        )
    def any_month_events(self, month, year):
        return self.active_objects.filter(
            Q(start_date__month=month, start_date__year=year) |
            Q(end_date__month=month, end_date__year=year)
        )
    def get_this_week_events(self):
        today = timezone.now().date()
        current_week = today.isocalendar()[1]
        return self.active_objects.filter(
            Q(start_date__week=current_week, start_date__year=today.year)|
            Q(end_date__week=current_week, end_date__year=today.year)
        )

class EventContactPerson(BaseModel):
    event = models.ForeignKey(EventModel, on_delete=models.CASCADE, related_name="event_contact_person")
    name = models.CharField(max_length=100, blank=False, null=False, help_text='Name of the person')
    position = models.CharField(max_length=100, blank=True, null=True, help_text='Position of the person')
    email = models.EmailField(blank=False, null=False, help_text='Email address of the person')
    contact_number = models.CharField(blank=False, null=False, max_length=50, help_text='Contact number of the person')
    wa_number = models.CharField(max_length=100, null=True, blank=True, help_text='WhatsApp number of the person')
    company = models.CharField(blank=True,null=False, max_length=50, help_text='Company of the person')
    whatsapp_available = models.BooleanField(default=False, help_text='Is this person whatsapp available')
    language = models.CharField(max_length=100, null=True, blank=True)
    photo = models.ImageField(blank=True, null=True, upload_to="events/contact_person", help_text='Image of the person')

    @property
    def get_image_name(self):
        return "event_contact_person"

    def get_languages(self):
        languages = self.language.split(",")
        return [language.title() for language in languages]