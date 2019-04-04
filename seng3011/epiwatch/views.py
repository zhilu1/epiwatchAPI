from django.template.response import TemplateResponse

from rest_framework_mongoengine import viewsets
from rest_framework.response import Response

from epiwatch.custom_viewset import ListOnlyModelViewSet
from epiwatch.serializers import *
from epiwatch.models import Article
from epiwatch.mixins import LoggingMixin
from rest_framework.filters import BaseFilterBackend
import coreapi
import datetime
from mongoengine.queryset.visitor import Q
import re
import calendar


class SimpleFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
                # queryset = Article.objects.all()
        location = request.query_params.get('location', None)
        if location is not None:
            # filter the queryset whose location matches location or country in reporteed  events
            location_filter = Q(
#                reports__reported_events__location__iexact=location)
             reports__reported_events__location__location__iexact=location) | Q(
             reports__reported_events__location__country__iexact=location)
            queryset = queryset.filter(
                location_filter)
        keyterms = request.query_params.get('keyterms', None)
        if keyterms is not None and keyterms is not '':
            # filter queryset whose disease or syndrome matches keyterms
            keyterm_arr = keyterms.split(',')
            # discard empty strings in the list
            keyterm_arr = filter(None, keyterm_arr)
            keyterm_filter = Q()
            for keyterm in keyterm_arr:
                keyterm_filter |= Q(main_text__icontains=keyterm)
                # keyterm_filter |= Q(reports__syndrome__iexact=keyterm)
            queryset = queryset.filter(keyterm_filter)
        return queryset

    def get_schema_fields(self, view):
        return [
            coreapi.Field(
                name='start_date',
                location='query',
                required=True,
                type='string',
                description='the starting datetime of the period you interested in, in the format of “yyyy-MM-ddTHH:mm:ss” '
            ),
            coreapi.Field(
                name='end_date',
                location='query',
                required=True,
                type='string',
                description='the ending datetime of the period you interested in, in the format of “yyyy-MM-ddTHH:mm:ss”'
            ),
            coreapi.Field(
                name='keyterms',
                location='query',
                required=False,
                type='array',
                description='list of all the key terms you want to get news about'
            ),
            coreapi.Field(
                name='location',
                location='query',
                required=False,
                type='string',
                description=' a location name (city/country/state etc.), which is a string to be matched with the content in the diseasereport'
            ),

        ]


class ArticleViewSet(LoggingMixin, ListOnlyModelViewSet):

    serializer_class = ArticleSerializer
    filter_backends = (SimpleFilterBackend,)
    queryset = Article.objects.all()

    def list(self, request):
        """
        GET a list articles based on input parameters.
        The structure of article response is as following

        {
            url: String,
            date_of_publication: <string::date>,
            headline: String,
            main_text: String,
            reports: [<object::report>]
        }

        object::report An object containing information about 1 or more events (death, reports, etc) of a disease and/or syndromes.
        {
            disease: [<string::disease>],
            syndrome: [<string::syndrome>],
            reported_events: [<object::event-report>],
            comment: String
        }

        object::event-report
        {
            type: <string::event-type>,
            date: <string::date>,
            location: [<object::location>],
            number_affected: <number>
        }

        object::location
        {
            country: [String]
            location: [String]
        }
example input:

        start_date: 2011-11-11T11:11:11,
        end_date: 2021-11-11T11:11:11,
        keyterms: cholera,malaria
        location: Uganda
        """

        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        # get starting date and ending date from url parameters
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        filtered_data = serializer.data
        results = []
        if end_date is not None and start_date is not None:
            # filter dates after getting data from database
            # since date_of_publication is in String type in database, we need to convert it to datetime before filtering
            try:
                st = datetime.datetime.strptime(
                    start_date, '%Y-%m-%dT%H:%M:%S')
                ed = datetime.datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%S')
            except:
                return Response(data="please input correct datetime which matches format '%Y-%m-%dT%H:%M:%S'", status=400)
            for result in filtered_data:
                # getting min possible date and max possible date from dates
                min_date = ""
                max_date = ""
                gs = re.match(
                    r'([\dx]{4})-([\dx]{2})-([\dx]{2})T([\dx]{2}):([\dx]{2}):([\dx]{2})', result["date_of_publication"]).groups()
                min_date = gs[0]  # year
                max_date = gs[0]
                year = int(gs[0])
                month = gs[1]
                if(gs[1] == "xx"):  # month
                    min_date += "-01"
                    max_date += "-12"
                    month = 12
                else:
                    min_date = min_date + "-" + gs[1]
                    max_date = max_date + "-" + gs[1]
                if(gs[2] == "xx"):  # day
                    min_date += "-01"
                    day = calendar.monthrange(year, month)[1]
                    max_date = max_date + "-" + str(day)
                else:
                    min_date = min_date + "-" + gs[2]
                    max_date = max_date + "-" + gs[2]
                min_date = min_date + "T"
                max_date = max_date + "T"
                if(gs[3] == "xx"):  # day
                    min_date += "00"
                    max_date += "23"
                else:
                    min_date = min_date + gs[3]
                    max_date = max_date + gs[3]

                for i in range(4, 6):
                    if(gs[i] == "xx"):  # month
                        min_date += ":00"
                        max_date += ":59"
                    else:
                        min_date = min_date + ":" + gs[i]
                        max_date = max_date + ":" + gs[i]

                minimum_date = datetime.datetime.strptime(
                    min_date, '%Y-%m-%dT%H:%M:%S')
                maximum_date = datetime.datetime.strptime(
                    max_date, '%Y-%m-%dT%H:%M:%S')

                # check if [min_date,max_date] and [st,ed] has intersection
                if(max(minimum_date, st) <= min(maximum_date, ed)):
                    results.append(result)
        else:
            return Response(status=400)
        return Response(results)
