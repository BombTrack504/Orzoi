# helper function for features


def detectUser(user):
    if user.role == 1:
        redirecturl = 'Restaurantdashboard'
        return redirecturl

    elif user.role == 2:
        redirecturl = 'Customerdashboard'
        return redirecturl

    elif user.role == None and user.is_superadmin:
        redirecturl = '/admin'
        return redirecturl
