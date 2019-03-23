from django.template.response import TemplateResponse

from rest_framework_mongoengine import viewsets
from rest_framework.response import Response

from epiwatch.custom_viewset import ListOnlyModelViewSet
from epiwatch.serializers import *
from epiwatch.models import Article
from rest_framework.filters import BaseFilterBackend
import coreapi
import datetime
from mongoengine.queryset.visitor import Q


class SimpleFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
                # queryset = Article.objects.all()
        location = request.query_params.get('location', None)
        if location is not None:
            # filter the queryset whose location matches location or country in reporteed  events
            location_filter = Q(
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
                keyterm_filter |= Q(reports__disease__iexact=keyterm)
                keyterm_filter |= Q(reports__syndrome__iexact=keyterm)
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


class ArticleViewSet(ListOnlyModelViewSet):

    serializer_class = ArticleSerializer

    filter_backends = (SimpleFilterBackend,)
    queryset = Article.objects.all()

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        # pagination
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
                cur_date = datetime.datetime.strptime(
                    result['date_of_publication'], '%Y-%m-%dT%H:%M:%S')
                if(st <= cur_date <= ed):
                    results.append(result)
        else:
            return Response(status=400)
        # return the final result, check if paginated
        return Response(results)
