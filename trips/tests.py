from datetime import datetime
from random import randint

from django.core.paginator import Paginator
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Company, Country, Trip
