# TODO can we do a client connection w/o a calendar?
def get_client(calendar):
    cal_client_url_templ = conf['caldav']['client_url']
    client_url = cal_client_url_templ.format(
        cal_user=conf['auth']['user'],
        cal_user_pw=conf['auth']['password'],
        calendar=calendar
    )
    return caldav.DAVClient(client_url)


def get_user(req):
    auth_url = conf['auth']['url']
    cookie_name = conf['auth']['cookie_name']
    try:
        session_cookie = req.cookies[conf['auth']['cookie_name']]
    except:
        app.logger.debug('No session cookie in request.')
        return None
    cookies = {cookie_name: session_cookie}
    response = requests.get(auth_url, cookies=cookies)
    app.logger.debug('Got user {} for session cookie {}.'.format(
        session_cookie, response))
    return response.content


# TODO cal name in model
def check_permission(cal, user, want):
    # TODO implicit unsafety, like Jinja2
    permission_url_templ = conf['permissions']['url_templ']
    cal_qt = urllib.quote_plus(cal)
    user_qt = urllib.quote_plus(user)
    permission_url = permission_url_templ.format(user=user_qt, calendar=cal_qt)
    resp = requests.get(permission_url)
    app.logger.debug('Got permission {} for user {} wanting {}.'.format(
        resp, user, want))
    return want in resp.content


def check_user_permission(cal, req, want):
    try:
        user = get_user(req)
        if user is None:
            return False
        app.logger.debug('Got user {} from auth backend.'.format(user))
        return check_permission(cal, user, want)
    except:
        return False


def get_cal_path(cal_user, cal_name):
    cal_path_templ = conf['caldav']['calendar_path']
    return cal_path_templ.format(cal_user=cal_user, calendar=cal_name)


def get_system_cal(cal_name):
    # TODO custom context to hold client and calendar
    client = get_client(cal_name)
    cal_path = get_cal_path(conf['auth']['user'], cal_name)
    return caldav.Calendar(client, cal_path)
