from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
from .models import Seat, Movie, ShowTime, Screen

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'duration_mins')

@admin.register(Screen)
class ScreenAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

@admin.register(ShowTime)
class ShowTimeAdmin(admin.ModelAdmin):
    list_display = ('movie', 'screen', 'start_time', 'end_time', 'base_price')
    list_filter = ('movie', 'screen', 'start_time')


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('show_time', 'row_id', 'number', 'status', 'held_by')
    list_filter = ('show_time', 'status', 'row_id')
    search_fields = ('show_time__movie__title', 'row_id', 'held_by')
    
    change_list_template = "admin/seats_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('map/', self.admin_site.admin_view(self.theatre_map), name='theatre-map'),
        ]
        return custom_urls + urls

    def theatre_map(self, request):
        seats = Seat.objects.all().order_by('row_id', 'number')
        
        # Group seats by row for the grid
        rows = {}
        for seat in seats:
            if seat.row_id not in rows:
                rows[seat.row_id] = []
            rows[seat.row_id].append(seat)
            
        context = {
            **self.admin_site.each_context(request),
            'title': 'Theatre Seat Map',
            'rows': rows,
        }
        return render(request, 'admin/theatre_map.html', context)
