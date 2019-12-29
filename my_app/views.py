from django.shortcuts import render
from bs4 import BeautifulSoup
import requests
from requests.compat import quote_plus
from . import models

BASE_QUERY = 'https://toronto.craigslist.org/search/sss?query={}&sort=rel'
min_price_query = '&min_price={}'
max_price_query = '&max_price={}'
Image_URL = 'https://images.craigslist.org/{}_300x300.jpg'
# Create your views here.
def home(request):
    return render(request , 'base.html')

def new_search(request):
    #Get search object
    Search_text = request.POST.get('search')
    min_text = request.POST.get('min_price')
    max_text = request.POST.get('max_price')
    
    #save searchs in the table
    models.Search.objects.create(search = Search_text)
    #Format Query
    final_url =  BASE_QUERY.format(quote_plus(Search_text))
    if min_text != '' and max_text != '':
        final_url = final_url + min_price_query.format(min_text) + max_price_query.format(max_text)
    elif (min_text != '' and max_text == ''):
        final_url = final_url + min_price_query.format(min_text)
    elif (min_text == '' and max_text != ''):
        final_url = final_url + max_price_query.format(max_text)

    print(final_url)
    #Excute the query
    response = requests.get(final_url)
    #Reponse from query
    data = response.text
    #Clean up the results using beautiful soup
    soup = BeautifulSoup(data, features='html.parser')
    post_lists = soup.find_all( 'li',{'class' : 'result-row'})
    post_title = post_lists[0].find(class_  ='result-title hdrlnk').text
    post_link  = post_lists[0].find('a').get('href')
    post_cost  = post_lists[0].find(class_  = 'result-price').text

    final_posts =[]
    for post in post_lists:
        post_title = post.find(class_  ='result-title hdrlnk').text
        post_link  = post.find('a').get('href')

        if post.find(class_  = 'result-price'):
            post_cost  = post.find(class_  = 'result-price').text
        else:
            post_cost = 'NA'
        if post.find(class_ = 'result-image').get('data-ids'):
            post_image_URL = post.find(class_ = 'result-image').get('data-ids').split(',')[0].split(':')[1]
            post_image = Image_URL.format(post_image_URL)
        else:
            post_image = 'https://image.shutterstock.com/image-vector/no-image-available-icon-vector-260nw-1323742826.jpg'
        final_posts.append((post_title, post_link, post_cost,post_image ))
    search_dictionary ={
        'search' : Search_text,
         'final_posts' : final_posts,
    }
    return render(request , 'my_app/new_search.html',search_dictionary)