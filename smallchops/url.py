
from django.urls import path
from . import views
from .views import *



urlpatterns = [

    path('search/suggestions/', search_suggestions, name='search_suggestions'),
    
    path('', views.Index, name='index'),
    path('chops/', views.ChopsView, name='chops'),
    path('chops_detail/<int:product_id>/', views.ChopsDetail,name='chopsdetail'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('verify_order_payment/<str:ref>/', verify_order_payment, name='verify_order_payment'),
    path('update_item/', views.updateItem, name='update_item'),
    
    
    path('foodvideo/', FoodVideolist, name='foodvideolist'),
    path('liked/', like_unlike_video, name='like-post-view'),
    path('video/', videos_list, name='video_list'),
    path('video/<int:pk>/', videos_detail, name='video_detail'),
    
    path('foodvideo/<int:pk>/', FoodVideo_detail, name='foodvideo_detail'),
    path('video/new/', video_new, name='video_new'),
    path('video/<int:pk>/edit/', video_edit, name='video_edit'),
    path('video/<int:pk>/delete/', video_delete, name='video_delete'),
    
    path("dashboard/", views.adminD, name="home"),
    
    path("register/", views.registerPage, name="register"),
    path('activate/<uidb64>/<token>/', activate_account, name='activate'),
    path("orders/", views.userOrder, name="user_order"),
    path("profile/", views.ProfilePage, name="profile"),
    path('edit_profile/', edit_profile, name='edit_profile'),
    path("login/", views.loginPage, name="login"),
    path("logout/", views.logoutUser, name="logout"),
    path('about_us/', views.AboutUs, name='aboutus'),

    path("customer/<str:pk_test>/", views.customer, name="customer"),
    path('products/', product_list, name='product_list'),
    path('products/<int:pk>/', product_detail, name='product_detail'),
    path('products/create/', product_create, name='product_create'),
    path('products/<int:pk>/update/', product_update, name='product_update'),
    path('products/<int:pk>/delete/', product_delete, name='product_delete'),
    path('create_category/', create_category, name='create_category'),
    path('create_category/<int:category_id>/', create_category, name='create_category'),
    path("category/<category>/", views.product_category, name="product_category"),
    
    path('view_comments/', view_comments, name='view_comments'),
    path('submit_comment/', submit_comment, name='submit_comment'),
    path('approve_comment/<int:comment_id>/', approve_comment, name='approve_comment'),
    path('delete-comment/<int:comment_id>/', delete_comment, name='delete_comment'),

    path('update_order/<int:order_id>/', views.OrderDetail, name='update_order'),
    path('orders_by_date/', orders_by_date, name='orders_by_date'),
    
    path('deliveries/', delivery_list, name='delivery-list'),
    path('delivery/add/', delivery_create, name='delivery-add'),
    path('delivery/<int:pk>/', delivery_update, name='delivery-update'),
    path('delivery/<int:pk>/delete/', delivery_delete, name='delivery-delete'),

    path('daily-total/', daily_total_view, name='daily_total'),
    path('rate/<int:product_id>/', views.rate_product, name='rate'),
    path('shipping/', shipping_view, name='shipping_view'),
    
    # Password reset views
    path('change_password/', change_password_view, name='change_password'),
    

    #Event
    path('verify_event_payment/<str:ref>/', verify_event_payment, name='verify_event_payment'),
    path('evtproducts/', evtproduct_list, name='evtproduct_list'),
    path('event_items/<int:event_id>/', Events_details, name='events_detail'),
    path('evtproducts/<int:pk>/', evtproduct_detail, name='evtproduct_detail'),
    path('evtproducts/create/', evtproduct_create, name='evtproduct_create'),
    path('evtproducts/<int:pk>/update/', evtproduct_update, name='evtproduct_update'),
    path('evtproducts/<int:pk>/delete/', evtproduct_delete, name='evtproduct_delete'),
    path('event_form/', event_form, name='event_form'),
    path('review_page/<int:event_id>/', Event_review_page, name='review_page'),
    path('checkout/<int:event_id>/', Event_Checkout, name='checkout'),
    
    
    
    path('proxy', views.proxy_view, name='proxy'),

]