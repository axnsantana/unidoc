def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)

@auth.requires_login()
def table_list(table,label,orderby):
    table.id.readable=False
    return dict(grid=SQLFORM.grid(table,
            orderby=orderby,maxtextlength=64, paginate=25),
            label=label)

@auth.requires_login()
def index():
    table=db.questionaries
    return table_list(table,T("Questionaries"),table.name)

@auth.requires_login()
def quest():
    table=db.questionaries
    return table_list(table,T("Questionaries"),table.name)

@auth.requires_login()
def vars_quest():
    table=db.questionaries_vars
    return table_list(table,T("Variables"),table.name)

@auth.requires_login()
def vars_dict():
    table=db.researcher_vars
    return table_list(table,T("Dictionary"),table.code)
