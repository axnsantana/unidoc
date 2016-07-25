# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html
    """
    import numpy as np
    import random

    #convert_names()

    total_gender = {}
    total_gender['Male'] = db(db.patient.sex == 'Male').count()
    total_gender['Female'] = db(db.patient.sex == 'Female').count()
    total_gender['Undeclared'] = db(db.patient.sex == 'Undeclared').count()

    groups = db(db.groups).select()
    freq_groups = {}
    grp_gender = {}
    for g in groups:
      freq_groups[g.code] = db(db.patient.groups.contains(g.id)).count()
      grp_gender[g.code] = {}
      grp_gender[g.code]['Male'] = db(db.patient.groups.contains(g.id) & (db.patient.sex == 'Male')).count()
      grp_gender[g.code]['Female'] = db(db.patient.groups.contains(g.id) & (db.patient.sex == 'Female')).count()
      grp_gender[g.code]['Undeclared'] = db(db.patient.groups.contains(g.id) & (db.patient.sex == 'Undeclared')).count()

    experiments = db(db.experiments).select()
    freq_experiments = {}
    exp_gender = {}
    for e in experiments:
      freq_experiments[e.code] = db(db.patient.experiments.contains(e.id)).count()
      exp_gender[e.code] = {}
      exp_gender[e.code]['Male'] = db(db.patient.experiments.contains(e.id) & (db.patient.sex == 'Male')).count()
      exp_gender[e.code]['Female'] = db(db.patient.experiments.contains(e.id) & (db.patient.sex == 'Female')).count()
      exp_gender[e.code]['Undeclared'] = db(db.patient.experiments.contains(e.id) & (db.patient.sex == 'Undeclared')).count()

    grp_exp = {}
    for e in experiments:
       grp_exp[e.code] = {}
       for g in groups:
          grp_exp[e.code][g.code] = db(db.patient.experiments.contains(e.id) & db.patient.groups.contains(g.id)).count()

    return dict(message=T('Pain Network: A web-based tool for diagnosis of the Chronic Pain.'),
                freq_gender=total_gender,freq_groups=freq_groups,freq_experiments=freq_experiments,
                exp_gender=exp_gender,grp_gender=grp_gender,grp_exp=grp_exp)

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())


@auth.requires_login()
def table_list(table,label,orderby,create=True):
   table.id.readable=False
   if auth.has_membership(group_id='administrators'):
      return dict(grid=SQLFORM.grid(table,create=create,
              orderby=orderby,maxtextlength=64, paginate=25),
              label=label)
   else:
      return dict(grid=SQLFORM.grid(table,
              create=False,deletable=False,editable=False,
              orderby=orderby,maxtextlength=64, paginate=25),
              label=label)

@auth.requires_login()
def patients_list():
   table=db.patient
   orderby=table.name
   label=T("Patients")
   #table.id.readable=False
   fields=[table.id,table.name]
   if auth.has_membership(group_id='administrators'):
      return dict(grid=SQLFORM.grid(table,fields=fields,
              orderby=orderby,maxtextlength=64, paginate=25),
              label=label)
   else:
      return dict(grid=SQLFORM.grid(table,fields=fields,
              create=False,deletable=False,editable=False,
              orderby=orderby,maxtextlength=64, paginate=25),
              label=label)

@auth.requires_login()
def researcher_list():
   table=db.researcher
   return table_list(table,T("Researchers"),table.name)

@auth.requires_login()
def groups_list():
   table=db.groups
   return table_list(table,T("Groups"),table.code)

@auth.requires_login()
def experiments_list():
   table=db.experiments
   return table_list(table,T("Experiments"),table.code)

@auth.requires_login()
def getFilesAnchor(row):
    anchor = ''
    try:
        examId = row['id']
    except:
        examId = 0
    if examId > 0:
        anchor = A(T('Files'),
                   _href=URL(c='default',f='exams_files',vars=dict(exam=examId),user_signature=False),
                   _class='button btn btn-default')
    return anchor

@auth.requires_login()
def exams_list():
   table=db.exams
   orderby=table.exam_date
   label=T("Exams")
   table.id.readable=False
   exportclass=dict(xml=False,html=False,csv_with_hidden_cols=False,tsv_with_hidden_cols=False,tsv=False,json=False)
   links = [lambda row: getFilesAnchor(row)]
   fields=[table.exam_date,table.patient_id,table.researcher_id,table.experiments_id,table.exams_type_id]
   if auth.has_membership(group_id='administrators'):
      return dict(grid=SQLFORM.grid(table,exportclasses=exportclass,fields=fields,
              orderby=orderby,maxtextlength=64, paginate=25,links=links),
              label=label)
   else:
      return dict(grid=SQLFORM.grid(table,exportclasses=exportclass,
              create=False,deletable=False,editable=False,
              orderby=orderby,maxtextlength=64, paginate=25,links=links),
              label=label)

@auth.requires_login()
def exams_files():
   examId=request.vars.exam
   request.post_vars.exam_id=examId
   exam = db.exams(examId)
   table=db.exam_files
   query=(table.exam_id==examId)
   orderby=table.filename
   title=T("Files")
   label=db.exams._format(exam)
   table.id.readable=False
   table.exam_id.readable=False
   if(('new' in request.args)or('edit' in request.args)):
      table.exam_id.default=examId
   else:
      table.exam_id.default=False
   if auth.has_membership(group_id='administrators'):
      grid=SQLFORM.grid(query,csv=False,orderby=orderby,maxtextlength=64, paginate=25)
      if(('new' in request.args)or('edit' in request.args)):
        grid.element('#exam_files_exam_id')['_disabled'] = True
      return dict(grid=grid,label=label,title=title)
   return dict(grid=SQLFORM.grid(query,csv=False,
              create=False,deletable=False,editable=False,
              orderby=orderby,maxtextlength=64, paginate=25),
              label=label,title=title)
