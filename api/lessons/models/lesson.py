import uuid

from django.db import models
from polymorphic.models import PolymorphicModel

"""
Why use a PolymorphicModel?

I wanted to be able to store different types of lessons. For example, maybe we
want to store a french lesson where the user needs to fill in the gaps. 

I considered having a just a lesson table with a type column and a payload JSON
column, this would allow a lot of flexibility on the data structure of the
lesson. Problem is that it's hard to evolve the schema. For example let's say
we want to remove a field from a lesson type, it's hard. We need to update each
JSON entry in the DB.

The other solution is having a table for each type of lesson, which is what I
did. This sacrifices a bit on performance since you need to join tables. I used
django-polymorphic lib here so it kinda improves performance a bit. It just
does one query for fetching base table and then one query for each lesson type.
I think this is the best compromise for having a solid easy to evolve schema,
and performance should not be so bad for most use cases.

You can read a bit more about it in the django-polymorphic docs: 
https://django-polymorphic.readthedocs.io/en/latest
https://django-polymorphic.readthedocs.io/en/latest/performance.html
"""
class Lesson(PolymorphicModel):
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order       = models.PositiveIntegerField()
    title       = models.CharField(max_length=200)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    is_active   = models.BooleanField(default=True)
