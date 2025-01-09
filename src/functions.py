# display_name 으로 부터 닉네임#태그 만 불러오는 함수
def get_nickname_from_display_name(display_name):
    return display_name.split('/')[0].strip()