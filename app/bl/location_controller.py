import app.data.repository.location_repo as lr


def get_location_by_place_name(place_name):
    return lr.search_location('Place', place_name)

if __name__ == '__main__':
    pass