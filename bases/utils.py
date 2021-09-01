from haversine import haversine


def check_data_key(key):
    if key == None:
        return False
    else:
        return True


def check_str_digit(numstr):
    if not check_data_key(numstr):
        return False

    if type(numstr) == str:
        if numstr.isdigit():
            return True
        try:
            float(numstr)
            return True
        except ValueError:
            return False
    elif type(numstr) == int or type(numstr) == float:
        return True
    else:
        return False


def custom_list(queryset):
    list = []
    for i in queryset:
        i = {
            'id': i.id,
            'user': i.user,
            'username': i.user.username,
            'image1': i.image1,
            'title': i.title,
            'text': i.text,
            'created_at': i.created_at.strftime("%Y-%m-%d %H:%M"),
        }
        list.append(i)
    return list


def custom_dict(i):
    return {
        'id': i.id,
        'user': i.user,
        'username': i.user.username,
        'image1': i.image1,
        'title': i.title,
        'text': i.text,
        'created_at': i.created_at.strftime("%Y-%m-%d %H:%M"),
    }


def custom_theme_dict(i):
    return {
        'id': i.id,
        'image': i.image,
        'type': i.type,
        'address': i.address,
        'name': i.name,
        'phone': i.phone,
        'type': i.type,
    }


def paginate(self, queryset):
    page = self.paginate_queryset(queryset)
    if page is not None:
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


def check_distance(user_lat, user_lon, camp_lat, camp_lon):

    user_loc = (user_lat, user_lon)
    camp_loc = (float(camp_lat), float(camp_lon))

    distance = haversine(user_loc, camp_loc, unit='km')

    return round(distance, 2)
