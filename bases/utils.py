def check_data_key(key):
    if key == None:
        return False
    else:
        return True


def check_str_digit(numstr):
    if type(numstr) == str:
        if numstr.isdigit():
            return True
        else:
            return False
    elif type(numstr) == int:
        return True
    else:
        return False


def custom_list(queryset):
    list = []
    for i in queryset:
        i = {
            'id': i.id,
            'user': i.user,
            'image': i.image,
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
            'image': i.image,
            'title': i.title,
            'text': i.text,
            'created_at': i.created_at.strftime("%Y-%m-%d %H:%M"),
        }


def paginate(self, queryset):
    page = self.paginate_queryset(queryset)
    if page is not None:
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
