
# Create your models here.
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User


# Create your models here.

class Movie(models.Model):
    my_movie_id = models.IntegerField()
    title = models.CharField(max_length=200)
    genre = models.CharField(max_length=100)
    overview = models.CharField(max_length=200000000)
    popularity = models.FloatField() or 0.0
    release_date = models.CharField(max_length=100)
    run_time = models.CharField(max_length=100)
    vote_average = models.FloatField() or 0.0
    vote_count = models.FloatField() or 0.0
    credits = models.CharField(max_length=100)
    keywords = models.CharField(max_length=10000)
    poster_path = models.CharField(max_length=500)
    backdrop_path = models.CharField(max_length=500)
    recommendations = models.CharField(max_length=500)

    def __str__(self):
        return self.title

class Movie_new( ):
    def __init__(self,index,id,title,genres,overview,popularity,release_date,runtime,vote_average,vote_count,credits,keywords,poster_path,backdrop_path,recommendations):
        self.index = index
        self.id = id
        self.title = title
        self.genres = genres
        self.overview = overview
        self.popularity = popularity
        self.release_date = release_date
        self.runtime = runtime
        self.vote_average = vote_average
        self.vote_count = vote_count
        self.credits = credits
        self.keywords = keywords
        self.poster_path = "https://image.tmdb.org/t/p/w500//" + str(poster_path)
        self.backdrop_path = "https://image.tmdb.org/t/p/w500//" + str(backdrop_path)
        self.recommendations = recommendations
class Myrating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0, validators=[MaxValueValidator(5), MinValueValidator(0)])

class MyList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    watch = models.BooleanField(default=False)

