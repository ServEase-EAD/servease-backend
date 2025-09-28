# URL Structure Comparison

## Authentication-Service Pattern (Target)
```python
# authentication_service/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('accounts.urls')),
]

# accounts/urls.py
urlpatterns = [
    path("register/", UserRegistrationAPIView.as_view(), name="register-user"),
    path("login/", UserLoginAPIView.as_view(), name="login-user"),
    path("logout/", UserLogoutAPIView.as_view(), name="logout-user"),
    # ... more explicit paths
]
```

## Customer-Service Pattern (Updated to Match)
```python
# customer_service/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/customers/', include('customers.urls')),
]

# customers/urls.py
urlpatterns = [
    path("", customer_viewset, name="customer-list"),
    path("<uuid:pk>/", customer_detail, name="customer-detail"),
    path("<uuid:pk>/dashboard/", customer_dashboard, name="customer-dashboard"),
    path("<uuid:pk>/verify/", customer_verify, name="customer-verify"),
    path("stats/", customer_stats, name="customer-stats"),
    path("by_user_id/", customer_by_user_id, name="customer-by-user-id"),
]
```

## Key Changes Made

### 1. Project URL Structure
- **Before**: `path('api/v1/', include('customers.urls'))`
- **After**: `path('api/v1/customers/', include('customers.urls'))`

### 2. App URL Structure
- **Before**: Router-generated URLs (`router.urls`)
- **After**: Explicit path mappings using ViewSet.as_view()

### 3. Benefits of New Structure
- ✅ **Consistency**: Matches authentication-service pattern
- ✅ **Explicit Control**: Clear URL-to-view mapping
- ✅ **Better Organization**: Each endpoint has a named URL pattern
- ✅ **Easier Debugging**: No router magic, direct path mapping
- ✅ **Custom Actions**: Easy to add custom endpoints

### 4. URL Endpoints Remain the Same
All endpoints work exactly the same as before:
- `GET /api/v1/customers/` - List customers
- `POST /api/v1/customers/` - Create customer
- `GET /api/v1/customers/{uuid}/` - Get customer
- `PUT/PATCH /api/v1/customers/{uuid}/` - Update customer
- `DELETE /api/v1/customers/{uuid}/` - Delete customer
- `GET /api/v1/customers/{uuid}/dashboard/` - Customer dashboard
- `POST /api/v1/customers/{uuid}/verify/` - Verify customer
- `GET /api/v1/customers/stats/` - Statistics
- `GET /api/v1/customers/by_user_id/?user_id=123` - Find by user ID