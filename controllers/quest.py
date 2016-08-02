from pylimerc import PyLimeRc


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)

@auth.requires_login()
def table_list(table, label, orderby):
    table.id.readable = False
    return dict(grid=SQLFORM.grid(table,
                orderby=orderby, maxtextlength=64, paginate=25),
                label=label)


@auth.requires_login()
def index():
    return dict(label=T("Statistics"))

def conn_lime():
    limeurl = myconf.get('lime.uri')
    limeuser = myconf.get('lime.usr')
    limepasswd = myconf.get('lime.passwd')
    lime = PyLimeRc(limeurl)
    lime.get_session_key(limeuser, limepasswd)
    return lime

def update_surveys():
    lime = conn_lime()
    new_surveys_list = lime.list_surveys()
    old_sid_list = db(db.surveys).select(db.surveys.sid).as_list()
    for s in new_surveys_list:
        status = T("Active") if (s['active'] == 'Y') else T("Inactive")
        db.surveys.update_or_insert((db.surveys.sid==s['sid']),sid=s['sid'],title=s['surveyls_title'],status=status)
        sid={'sid':s['sid']}
        if sid in old_sid_list:
            old_sid_list.remove(sid)
    lime.release_session_key()
    for old in old_sid_list:
        db(db.surveys.sid==old['sid']).delete()
    db.commit()
    redirect(URL('quest','surveys'))
    return

@auth.requires_login()
def surveys():
    table=db.surveys
    orderby=(table.status|table.sid|table.title)
    label=T("Surveys")
    table.id.readable=False
    if('edit' in request.args):
        table.sid.writable = False
        table.title.writable = False
        table.status.writable = False
    grid=SQLFORM.grid(table,csv=False,
              create=False,deletable=False,editable=True,
              orderby=orderby,maxtextlength=64, paginate=25)
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
