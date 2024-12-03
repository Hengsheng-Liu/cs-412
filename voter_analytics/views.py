from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Voter

from django.db.models.functions import ExtractYear
from django.db.models import Count, Q
import plotly.graph_objs as go
import plotly.io as pio
class VoterListView(ListView):
    model = Voter
    template_name = 'voter_list.html'
    context_object_name = 'voters'
    paginate_by = 100

    def get_queryset(self):
        queryset = super().get_queryset()
        # Get filter parameters
        party_affiliation = self.request.GET.get('party_affiliation')
        min_dob = self.request.GET.get('min_dob')
        max_dob = self.request.GET.get('max_dob')
        voter_score = self.request.GET.get('voter_score')
        elections = self.request.GET.getlist('elections')

        # Apply filters
        if party_affiliation:
            queryset = queryset.filter(party_affiliation=party_affiliation)
        if min_dob:
            queryset = queryset.filter(date_of_birth__year__gte=int(min_dob))
        if max_dob:
            queryset = queryset.filter(date_of_birth__year__lte=int(max_dob))
        if voter_score:
            queryset = queryset.filter(voter_score=int(voter_score))
        if elections:
            for election in elections:
                filter_kwargs = {election: True}
                queryset = queryset.filter(**filter_kwargs)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Dropdown options
        context['party_affiliations'] = Voter.objects.values_list('party_affiliation', flat=True).distinct()
        context['years'] = sorted(set(Voter.objects.values_list('date_of_birth__year', flat=True)))
        context['voter_scores'] = sorted(set(Voter.objects.values_list('voter_score', flat=True)))
        context['elections'] = ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']
        return context

class VoterDetailView(DetailView):
    model = Voter
    template_name = 'voter_detail.html'
    context_object_name = 'voter'
class GraphsView(ListView):
    model = Voter
    template_name = 'graphs.html'
    context_object_name = 'voters'

    def get_queryset(self):
        queryset = super().get_queryset()
        # Apply filters if they exist in GET parameters
        party_affiliation = self.request.GET.get('party_affiliation')
        min_dob = self.request.GET.get('min_dob')
        max_dob = self.request.GET.get('max_dob')
        voter_score = self.request.GET.get('voter_score')
        elections = self.request.GET.getlist('elections')

        if party_affiliation:
            queryset = queryset.filter(party_affiliation=party_affiliation)
        if min_dob:
            queryset = queryset.filter(date_of_birth__year__gte=int(min_dob))
        if max_dob:
            queryset = queryset.filter(date_of_birth__year__lte=int(max_dob))
        if voter_score:
            queryset = queryset.filter(voter_score=int(voter_score))
        if elections:
            for election in elections:
                filter_kwargs = {election: True}
                queryset = queryset.filter(**filter_kwargs)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['party_affiliations'] = Voter.objects.values_list('party_affiliation', flat=True).distinct()
        context['years'] = sorted(set(Voter.objects.values_list('date_of_birth__year', flat=True)))
        context['voter_scores'] = sorted(set(Voter.objects.values_list('voter_score', flat=True)))
        context['elections'] = ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']
        # Histogram of Voters by Year of Birth
        voters_by_year = self.get_queryset().annotate(year=ExtractYear('date_of_birth')).values('year').annotate(count=Count('id')).order_by('year')
        years = [voter['year'] for voter in voters_by_year]
        counts = [voter['count'] for voter in voters_by_year]

        histogram = go.Figure([go.Bar(x=years, y=counts, marker=dict(color='blue'))])
        histogram.update_layout(title='Distribution of Voters by Year of Birth', xaxis_title='Year of Birth', yaxis_title='Count')

        # Pie Chart of Voters by Party Affiliation
        voters_by_party = self.get_queryset().values('party_affiliation').annotate(count=Count('id'))
        parties = [voter['party_affiliation'] for voter in voters_by_party]
        party_counts = [voter['count'] for voter in voters_by_party]

        pie_chart = go.Figure([go.Pie(labels=parties, values=party_counts)])
        pie_chart.update_layout(title='Distribution of Voters by Party Affiliation')

        # Histogram of Participation in Elections
        election_fields = ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']
        election_counts = {field: self.get_queryset().filter(**{field: True}).count() for field in election_fields}

        election_histogram = go.Figure([go.Bar(x=list(election_counts.keys()), y=list(election_counts.values()), marker=dict(color='green'))])
        election_histogram.update_layout(title='Voter Participation by Election', xaxis_title='Election', yaxis_title='Count')

        # Add graphs to context
        context['histogram'] = pio.to_html(histogram, full_html=False)
        context['pie_chart'] = pio.to_html(pie_chart, full_html=False)
        context['election_histogram'] = pio.to_html(election_histogram, full_html=False)

        return context