from django.urls import path
from . import views

urlpatterns = [

    # -------------------- PUBLIC ROUTES --------------------
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard_redirect, name="dashboard"),
    path("appointments/book/", views.appointment_page, name="appointment_page"),


    path("appointment/", views.make_appointment, name="appointment"),
    path("signup/", views.signup, name="signup"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("pets/", views.pets_list, name="pets_list"),
    path("pet/<int:pet_id>/", views.pet_detail, name="pet_detail"),
    

    # -------------------- ADOPTER ROUTES --------------------
    path("adopter/dashboard/", views.adopter_dashboard, name="adopter_dashboard"),
    path("adopter/profile/", views.adopter_profile, name="adopter_profile"),
    path("adopter/adoptions/", views.adopter_adoptions, name="adopter_adoptions"),
    path("adopter/favorites/", views.adopter_favorites, name="adopter_favorites"),
    path("adopter/appointments/", views.adopter_appointments, name="adopter_appointments"),

    # Adoption action (adopter requesting adoption)
    path("adopt/<int:pet_id>/", views.send_adoption_request, name="send_adoption_request"),

    # -------------------- OWNER ROUTES --------------------
    path("owner/dashboard/", views.owner_dashboard, name="owner_dashboard"),
    path("owner/pets/", views.owner_pets, name="owner_pets"),
    path("owner/pets/add/", views.owner_add_pet, name="owner_add_pet"),
    path("owner/adoptions/", views.owner_adoptions, name="owner_adoptions"),
    path("owner/adoptions/approve/<int:req_id>/", views.owner_approve_request, name="owner_approve_request"),
    path("owner/adoptions/reject/<int:req_id>/", views.owner_reject_request, name="owner_reject_request"),
    path("owner/appointments/", views.owner_appointments, name="owner_appointments"),
    path("owner/profile/", views.owner_profile, name="owner_profile"),

    # Owned Pet Detail
    path("owned-pet/<int:pet_id>/", views.owned_pet_detail, name="owned_pet_detail"),

    # -------------------- SHELTER ROUTES --------------------
    path("shelter/signup/", views.shelter_signup, name="shelter_signup"),
    path("shelter/dashboard/", views.shelter_dashboard, name="shelter_dashboard"),
    path("shelter/profile/", views.shelter_profile, name="shelter_profile"),
    path("shelter/pets/", views.shelter_pets, name="shelter_pets"),
    path("shelter/pets/add/", views.shelter_add_pet, name="shelter_add_pet"),
    path("shelter/pets/edit/<int:pet_id>/", views.shelter_edit_pet, name="shelter_edit_pet"),
    path("shelter/pets/delete/<int:pet_id>/", views.shelter_delete_pet, name="shelter_delete_pet"),
    path("shelter/pets/list/<int:pet_id>/",views.shelter_mark_available,name="shelter_mark_available"),

    path("shelter/pets/unlist/<int:pet_id>/",views.shelter_mark_unavailable,name="shelter_mark_unavailable"),

    # Shelter adoption actions
    path("shelter/adoptions/", views.shelter_adoptions, name="shelter_adoptions"),
    path("shelter/adoptions/approve/<int:req_id>/", views.approve_request, name="approve_request"),
    path("shelter/adoptions/decline/<int:req_id>/", views.decline_request, name="decline_request"),
    path("chat/", views.chat, name="chat"),
    path("payments/", views.payment, name="payment"),
    path("owner/pets/list/<int:pet_id>/", views.owner_list_pet, name="owner_list_pet"),
    path("owner/pets/unlist/<int:pet_id>/", views.owner_unlist_pet, name="owner_unlist_pet"),
    path("adopt/owner/<int:pet_id>/",views.send_owner_adoption_request,name="send_owner_adoption_request"),

    path("owner/adoptions/approve/<int:req_id>/",views.owner_approve_request,name="owner_approve_request"),

    path("owner/adoptions/reject/<int:req_id>/",views.owner_reject_request,name="owner_reject_request"),
    path("superadmin/dashboard/",views.superadmin_dashboard,name="superadmin_dashboard"),
    path("superadmin/users/",views.superadmin_users,name="superadmin_users"),
    path("superadmin/orders/",views.superadmin_orders,name="superadmin_orders"),
    path("superadmin/analytics/",views.superadmin_analytics,name="superadmin_analytics"),
    path("superadmin/users/",views.superadmin_users,name="admin_users"),
    path( "superadmin/pets/",views.superadmin_pets,name="admin_pets"),
    path("superadmin/adoptions/",views.superadmin_adoptions,name="admin_adoptions"),
    path("superadmin/adoptions/<int:pk>/approve/",views.admin_approve_adoption,name="admin_approve_adoption"),
    path("superadmin/adoptions/<int:pk>/reject/",views.admin_reject_adoption,name="admin_reject_adoption"),
    path("my-services/",views.my_service_appointments,name="my_service_appointments"),
    path("appointments/book/", views.appointment_page, name="appointment_page"),
    path("chat/<int:request_id>/", views.chat_room, name="chat_room"),




]
