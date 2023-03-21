from django.shortcuts import render, HttpResponse
from .forms import *
from random import shuffle
from django.db import connection
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from .models import Movie, Myrating, MyList
from django.db.models import Q
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.db.models import Case, When
import pandas as pd
from django.views.decorators.csrf import csrf_protect
from .movie_recommend_operations import *
from .model import *
import time
import json
from django.http import JsonResponse
from .advanced_search import *
# Create your views here.
def index(request):
    movies = []
    urls = []
    ids = []
    titles = []
    genre_urls = []
    genre_ids = []
    genre_titles = []
    cursor = connection.cursor()
    # cursor.execute("SHOW COLUMNS FROM movie_info")
    # cursor.execute("SELECT poster_path FROM movie_info ORDER BY release_date DESC LIMIT 10")
    cursor.execute("SELECT id,backdrop_path,title FROM movie_info ORDER BY release_date DESC LIMIT 10")
    row = cursor.fetchall()
    for x in row:
        urls.append("https://image.tmdb.org/t/p/w500//" + x[1])
        ids.append(x[0])
        titles.append(x[2])
    genre = request.GET.get('genre')
    year = request.GET.get('year')
    rows = []
    print(genre)
    print(year)
    if not genre or genre == "All":
        if not year or year == "All":
            cursor.execute("SELECT * FROM movie_info LIMIT 30")

        else:
            if len(year) == 4:
                cursor.execute(
                    "SELECT * FROM movie_info WHERE  release_date LIKE '%" + str(
                        year) + "%' LIMIT 30")

            if len(year) == 7:
                cursor.execute("SELECT *  FROM movie_info WHERE release_date <= '2000' LIMIT 30")

            if len(year) == 9:
                if "2010" in year:
                    cursor.execute("SELECT *  FROM movie_info WHERE release_date NOT IN BETWEEN '2010' AND '2019' LIMIT 30")

                else:
                    cursor.execute("SELECT *  FROM movie_info WHERE release_date NOT IN BETWEEN '2000' AND '2009' LIMIT 30")
    else:
        if not year or year == "All":
            cursor.execute("SELECT * FROM movie_info WHERE genres Like '%" + str(genre) + "%' LIMIT 30")

        else:
            if len(year) == 4:
                cursor.execute(
                    "SELECT * FROM movie_info WHERE release_date LIKE %s AND genres LIKE %s LIMIT 30",
                    ('%{}%'.format(year), '%{}%'.format(genre))
                )

            if len(year) == 7:
                cursor.execute(
                    "SELECT * FROM movie_info WHERE release_date <='2000' AND genres LIKE %s LIMIT 30",
                    ('%{}%'.format(genre)))

            if len(year) == 9:
                if "2010" in year:
                    cursor.execute(
                        "SELECT * FROM movie_info WHERE release_date >= '2010' AND release_date <= '2019' AND genres LIKE %s LIMIT 30",
                        ('%{}%'.format(genre)))

                else:
                    cursor.execute(
                        "SELECT * FROM movie_info WHERE release_date >= '2000' AND release_date <= '2009' AND genres LIKE %s LIMIT 30",
                        ('%{}%'.format(genre)))

    rows = cursor.fetchall()

    for movie_info in rows:
        if movie_info[12]:
            movies.append(Movie_new(movie_info[0], movie_info[1], movie_info[2], movie_info[3],
                                movie_info[4], movie_info[5], movie_info[6], movie_info[7], movie_info[8],
                                movie_info[9], movie_info[10], movie_info[11], movie_info[12], movie_info[13],
                                movie_info[14]))
    context = {'ids': ids, 'urls': urls, 'titles': titles, 'movies': movies}
    cursor.close()
    return render(request, 'recommend/start.html', context)

def list(request):
    cursor = connection.cursor()
    query = request.GET.get('q')
    check = request.GET.get('watch')
    print(check)
    start = time.time()
    if check == "deeplearning":
        movies = mainSearch(dlsearch(query))
    else:
        movies = mainSearch(query)
    end = time.time()
    time_consume = end - start
    if movies == "No result":
        return render(request, 'recommend/list.html', {'time_consume': time_consume})

    movies_num = len(movies)
    if movies_num > 0:
        # 分页
        # 每页数据条数
        num = request.GET.get('num', 5)
        num = int(num)
        # 获取页码
        pindex = request.GET.get('page', 1)
        pindex = int(pindex)
        # 当前页码
        if pindex == 1:  # django中默认返回空值，所以加以判断，并设置默认值为1
            add_num = 1
            has_previous = False
        else:  # 如果有返回在值，把返回值转为整数型
            add_num = 1 + 10 * pindex
            has_previous = True
        # 页码总数
        num_pages = math.ceil(movies_num / num)
        # 当前页的内容
        start_index = (pindex - 1) * num  # 起始位置
        end_index = pindex * num  # 结束位置
        has_next = True
        if movies_num <= end_index:
            end_index = None
            has_next = False
        page = movies[start_index:end_index]
        print(start_index, end_index, len(page))
        # 设置前后可显示页码范围
        page_range_f = range(max(pindex - 3, 1), pindex)
        page_range_l = range(pindex, min(pindex + 3, num_pages) + 1)
        page_range = [*page_range_f] + [*page_range_l]
        # 添加省略号标记
        if (page_range[0] - 1 >= 2):
            page_range.insert(0, '...')
        if (num_pages - page_range[-1] >= 2):
            page_range.append('...')
        # 再将第一页与最后一页始终显示
        if (page_range[0] != 1):
            page_range.insert(0, 1)
        if (page_range[-1] != num_pages):
            page_range.append(num_pages)

        return render(request, 'recommend/list.html',
                      {'movies': page, 'q': query, 'num': num, 'has_previous': has_previous, 'has_next': has_next,
                       'add_num': add_num, 'pindex': pindex, 'page_range': page_range, 'time_consume': time_consume})
    urls = []
    ids = []
    titles = []
    cursor = connection.cursor()
    cursor.execute("SELECT id,backdrop_path,title FROM movie_info ORDER BY release_date DESC LIMIT 10")
    row = cursor.fetchall()
    for x in row:
        urls.append("https://image.tmdb.org/t/p/w500//" + x[1])
        ids.append(x[0])
        titles.append(x[2])
    cursor.close()
    context = {'ids': ids, 'urls': urls, 'titles': titles}
    return render(request, 'recommend/start.html', context)

def signUp(request):
    form = UserForm(request.POST or None)

    if form.is_valid():
        user = form.save(commit=False)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect("index")

    context = {'form': form}

    return render(request, 'recommend/signUp.html', context)


def Login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect("index")
            else:
                return render(request, 'recommend/login.html', {'error_message': 'Your account disable'})
        else:
            return render(request, 'recommend/login.html', {'error_message': 'Invalid Login'})

    return render(request, 'recommend/login.html')


# Logout user
def Logout(request):
    logout(request)
    return redirect("login")

def watch(request):
    cursor = connection.cursor()
    if not request.user.is_authenticated:
        return redirect("login")
    if not request.user.is_active:
        raise Http404
    mylist = show(request.user.id)
    mylist.reverse()
    movies = []
    if len(mylist)>0:
        sql = "SELECT * FROM movie_info WHERE "
        for i in range(len(mylist)):
            if i == len(mylist) - 1:
                sql += "id = " + str(mylist[i])
            else:
                sql += "id = " + str(mylist[i]) + " OR "
        cursor.execute(sql)
        data = cursor.fetchall()
        for id in mylist:
            for m_tuple in data:
                if m_tuple[1] == id:
                    movie_info = []
                    for column in m_tuple:
                        movie_info.append(column)
                    movies.append(Movie_new(movie_info[0], movie_info[1], movie_info[2], movie_info[3],
                                movie_info[4], movie_info[5], movie_info[6], movie_info[7], movie_info[8],
                                movie_info[9], movie_info[10], movie_info[11], movie_info[12], movie_info[13],
                                movie_info[14]))
    recmovies = []
    for i in movies:
        if (i.recommendations):
            rec = i.recommendations.split('-')
            for j in rec:
                recmovies.append(j)
    shuffle(recmovies)
    recmovies = recmovies[:20]
    recm = []
    if len(recmovies)>0:
        sql = "SELECT * FROM movie_info WHERE "
        for i in range(len(recmovies)):
            if i == len(recmovies) - 1:
                sql += "id = " + str(recmovies[i])
            else:
                sql += "id = " + str(recmovies[i]) + " OR "
        print(sql)
        cursor.execute(sql)
        data = cursor.fetchall()

        for m_tuple in data:
            movie_info = []
            if (m_tuple):
                for column in m_tuple:
                    movie_info.append(column)
                recm.append(Movie_new(movie_info[0], movie_info[1], movie_info[2], movie_info[3],
                                  movie_info[4], movie_info[5], movie_info[6], movie_info[7], movie_info[8],
                                  movie_info[9], movie_info[10], movie_info[11], movie_info[12], movie_info[13],
                                  movie_info[14]))
    else:
        cursor.execute(
            "SELECT * FROM movie_info WHERE id >= ( SELECT floor( RAND() * ( SELECT MAX( id ) FROM movie_info ) ) ) ORDER BY release_date DESC LIMIT 10")
        data = cursor.fetchall()

        for m_tuple in data:
            movie_info = []
            if (m_tuple):
                for column in m_tuple:
                    movie_info.append(column)
                recm.append(Movie_new(movie_info[0], movie_info[1], movie_info[2], movie_info[3],
                                      movie_info[4], movie_info[5], movie_info[6], movie_info[7], movie_info[8],
                                      movie_info[9], movie_info[10], movie_info[11], movie_info[12], movie_info[13],
                                      movie_info[14]))

    return render(request, 'recommend/watch.html', {'movies': movies,'recommend':recm})

def detail(request,m_id):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM movie_info WHERE id = " + str(m_id))
    m_tuple = cursor.fetchall()
    movie_info = []
    if request.user.is_authenticated:
        if 'watch' in request.POST:
            watch_flag = request.POST['watch']
            if watch_flag == 'on':
                insert(request.user.id, m_id)
            else:
                print("remove")
                delete(request.user.id, m_id)
        mylist = show(request.user.id)
        if int(m_id) in mylist:
            update = True
            for column in m_tuple[0]:
                movie_info.append(column)
            movies = Movie_new(movie_info[0], movie_info[1], movie_info[2], movie_info[3],
                               movie_info[4], movie_info[5], movie_info[6], movie_info[7], movie_info[8],
                               movie_info[9], movie_info[10], movie_info[11], movie_info[12], movie_info[13],
                               movie_info[14])
            return render(request, 'recommend/detail.html', {'movies': movies, 'update': update})
    for column in m_tuple[0]:
        movie_info.append(column)
    movies = Movie_new(movie_info[0], movie_info[1], movie_info[2], movie_info[3],
                       movie_info[4], movie_info[5], movie_info[6], movie_info[7], movie_info[8],
                       movie_info[9], movie_info[10], movie_info[11], movie_info[12], movie_info[13],
                       movie_info[14])
    return render(request, 'recommend/detail.html', {'movies': movies})



