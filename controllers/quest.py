from pylimerc import PyLimeRc


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


@auth.requires_login()
def conn_lime():
    limeurl = myconf.get('lime.uri')
    limeuser = myconf.get('lime.usr')
    limepasswd = myconf.get('lime.passwd')
    lime = PyLimeRc(limeurl)
    lime.get_session_key(limeuser, limepasswd)
    return lime


@auth.requires_login()
def list_lime_surveys():
    lime = conn_lime()
    surveys_list = lime.list_surveys()
    lime.release_session_key()
    return surveys_list


@auth.requires_login()
def table_list(table, label, orderby):
    table.id.readable = False
    return dict(grid=SQLFORM.grid(table,
                orderby=orderby, maxtextlength=64, paginate=25),
                label=label)


@auth.requires_login()
def index():
    return dict(label=T("Statistics"))

@auth.requires_login()
def surveys():
    table=db.surveys
    orderby=(table.status|table.sid|table.title)
    label=T("Surveys")
    table.id.readable=False
    grid=SQLFORM.grid(table,csv=False,
              create=False,deletable=False,editable=True,
              orderby=orderby,maxtextlength=64, paginate=25)
    if('edit' in request.args):
        grid.element('#surveys_sid')['_disabled'] = True
        grid.element('#surveys_title')['_disabled'] = True
        grid.element('#surveys_status')['_disabled'] = True
    return dict(grid=grid,label=label)

@auth.requires_login()
def files():
    table = db.questionaries
    return table_list(table, T("Questionaries"), table.name)


@auth.requires_login()
def quest():
    table = db.questionaries
    return table_list(table, T("Questionaries"), table.name)


@auth.requires_login()
def vars_quest():
    table = db.questionaries_vars
    return table_list(table, T("Variables"), table.name)


@auth.requires_login()
def vars_dict():
    table = db.researcher_vars
    return table_list(table, T("Dictionary"), table.code)
