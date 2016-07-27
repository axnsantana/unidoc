# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------
# This scaffolding model makes your app work on Google App Engine too
# File is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

if request.global_settings.web2py_version < "2.14.1":
    raise HTTP(500, "Requires web2py 2.13.3 or newer")

# -------------------------------------------------------------------------
# if SSL/HTTPS is properly configured and you want all HTTP requests to
# be redirected to HTTPS, uncomment the line below:
# -------------------------------------------------------------------------
# request.requires_https()

# -------------------------------------------------------------------------
# app configuration made easy. Look inside private/appconfig.ini
# -------------------------------------------------------------------------
from gluon.contrib.appconfig import AppConfig

# -------------------------------------------------------------------------
# once in production, remove reload=True to gain full speed
# -------------------------------------------------------------------------
myconf = AppConfig(reload=True)

def patient_tooltip(pid):
   import datetime
   ptt=db.patient[pid]
   # tip=[]
   # tip.append("Gender")
   # tip.append(ptt.sex)
   # tip2=": ".join(tip)
   # print type(T('Caixa').encode())
   birth_date=ptt.birth_date
   if(birth_date is None):
      birth_date='00/00/0000'
   else:
      birth_date=birth_date.strftime("%d/%m/%Y")
   phones='|'.join(ptt.phones)
   tip="; ".join([': '.join([T("Gender").encode(),ptt.sex]),
                ': '.join([T("Birth").encode(),birth_date]),
                ': '.join([T("Address").encode(),ptt.address]),
                ': '.join([T("E-mail").encode(),ptt.email]),
                ': '.join([T("Phones").encode(),phones]),
                ': '.join([T("Obs").encode(),ptt.observations])])
   return DIV(ptt.name,_title=tip)

if not request.env.web2py_runtime_gae:
    # ---------------------------------------------------------------------
    # if NOT running on Google App Engine use SQLite or other DB
    # ---------------------------------------------------------------------
    db = DAL(myconf.get('db.uri'),
             pool_size=myconf.get('db.pool_size'),
             migrate_enabled=myconf.get('db.migrate'),
             check_reserved=['all'])
    db.define_table('experiments',
       Field('code',length=255, unique=True,label=T("Code")),
       Field('name',length=255, unique=True,label=T("Name")),
       format = '%(code)s')

    db.define_table('groups',
       Field('code',length=255, unique=True,label=T("Code")),
       Field('name',length=255, unique=True,label=T("Name")),
       format = '%(code)s - %(name)s')

    db.define_table('patient',
       Field('name',label=T("Name"),unique=True,represent=lambda id, r: patient_tooltip(r.id)),
       Field('sex',label=T("Gender")),
       Field('birth_date','date',label=T("Birth Date")),
       Field('first_contact','date',label=T("First Contact")),
       Field('address',label=T("Address")),
       Field('city',label=T("City")),
       Field('country',label=T("Country")),
       Field('observations','text',label=T("Observations")),
       Field('email',label=T("E-mail")),
       Field('phones',type='list:string',label=T("Phones")),
       Field('old_codes',type='list:string',label=T("Old Codes")),
       Field('experiments', 'list:reference experiments',label=T("Experiments"),widget=SQLFORM.widgets.checkboxes.widget),
       Field('groups', 'list:reference groups',label=T("Groups"),widget=SQLFORM.widgets.checkboxes.widget),
       format = '%(name)s - P%(id)s')
    db.patient.name.requires=IS_NOT_EMPTY()
    db.patient.birth_date.requires=IS_NOT_EMPTY()
    db.patient.sex.requires=IS_IN_SET([T('Female'),T('Male'),T('Undeclared')],zero=T("Choose one"))
    db.patient.experiments.requires=IS_IN_DB(db,db.experiments,db.experiments._format,multiple=True)
    db.patient.groups.requires=IS_IN_DB(db,db.groups,db.groups._format,multiple=True)

    db.define_table('researcher',
       Field('name',length=255, unique=True,label=T("Name")),
       Field('r_active','boolean',label=T("Active")),
       format = '%(name)s')

    db.define_table('exams_type',
       Field('name',length=255, unique=True,label=T("Name")),
       format = '%(name)s')

    db.define_table('exams',
       Field('exam_date', 'datetime',label=T("Date")),
       Field('patient_id', 'reference patient',label=T("Patient")),
       Field('researcher_id', 'reference researcher',label=T("Examiner")),
       Field('experiments_id', 'reference experiments',label=T("Experiment")),
       Field('exams_type_id', 'reference exams_type',label=T("Type")),
       Field('description',type='text',label=T("Description")),
       format = lambda r: '[%s] %s [%s] %s : %s' % (db.exams_type(r.exams_type_id).name,
                                              db.patient(r.patient_id).name,
                                              db.experiments(r.experiments_id).code,
                                              db.researcher(r.researcher_id).name,
                                              r.exam_date))
    db.exams.patient_id.requires = IS_IN_DB(db, db.patient.id,db.patient._format,orderby=db.patient.name)
    db.exams.researcher_id.requires = IS_IN_DB(db, db.researcher.id, '%(name)s')
    db.exams.exams_type_id.requires = IS_IN_DB(db, db.exams_type.id, '%(name)s')
    db.exams.experiments_id.requires=IS_IN_DB(db,db.experiments,db.experiments._format)

    db.define_table('exam_files',
        Field('exam_id','reference exams',label=('Exam')),
        Field('filename', type='string', label=T('Filename')),
        Field('data_exam', 'upload',uploadfield='data_file',label=T("File")),
        Field('data_file','blob'),
        format = '%(filename)%')
    db.exam_files.exam_id.requires = IS_IN_DB(db,db.exams.id,db.exams._format)
    db.exam_files.data_exam.requires = IS_NOT_EMPTY()

    db.define_table('questionaries',
       Field('name',length=255, unique=True,label=T("Name")),
       Field('Description',type='text',label=T("Description")),
       Field('quest_source', 'upload',uploadfield='source_file',label=T("File")),
       Field('source_file','blob'),
       format = '%(name)s')
    db.questionaries.name.requires = IS_NOT_EMPTY()

    db.define_table('questionaries_vars',
       Field('questionary_id','reference questionaries',label=T("Questionary")),
       Field('name',length=255, unique=True,label=T("Name")),
       Field('Description',type='text',label=T("Description")),
       format = lambda r: '%s | %s' % (db.questionaries(r.questionary_id).name,r.name))
    db.questionaries_vars.name.requires = IS_NOT_EMPTY()
    db.questionaries_vars.questionary_id.requires = IS_IN_DB(db,db.questionaries.id,db.questionaries._format)

    db.define_table('researcher_vars',
       Field('code',length=255,label=T("Code")),
       Field('researcher_id','reference researcher', label=T('Researcher')),
       Field('var_id','reference questionaries_vars',label=T('Original Name')),
       format = lambda r: '%s | %s' % (r.code,db.researcher(r.researcher_id).name))
    db.researcher_vars.code.requires = IS_NOT_EMPTY()
    db.researcher_vars.var_id.requires = IS_IN_DB(db,db.questionaries_vars.id,db.questionaries_vars._format)
    db.researcher_vars.researcher_id.requires = IS_IN_DB(db,db.researcher.id,db.researcher._format)

else:
    # ---------------------------------------------------------------------
    # connect to Google BigTable (optional 'google:datastore://namespace')
    # ---------------------------------------------------------------------
    db = DAL('google:datastore+ndb')
    # ---------------------------------------------------------------------
    # store sessions and tickets there
    # ---------------------------------------------------------------------
    session.connect(request, response, db=db)
    # ---------------------------------------------------------------------
    # or store session in Memcache, Redis, etc.
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))
    # ---------------------------------------------------------------------

# -------------------------------------------------------------------------
# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
# -------------------------------------------------------------------------
response.generic_patterns = ['*'] if request.is_local else []
# -------------------------------------------------------------------------
# choose a style for forms
# -------------------------------------------------------------------------
response.formstyle = myconf.get('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.get('forms.separator') or ''

# -------------------------------------------------------------------------
# (optional) optimize handling of static files
# -------------------------------------------------------------------------
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

# -------------------------------------------------------------------------
# (optional) static assets folder versioning
# -------------------------------------------------------------------------
# response.static_version = '0.0.0'

# -------------------------------------------------------------------------
# Here is sample code if you need for
# - email capabilities
# - authentication (registration, login, logout, ... )
# - authorization (role based authorization)
# - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
# - old style crud actions
# (more options discussed in gluon/tools.py)
# -------------------------------------------------------------------------

from gluon.tools import Auth, Service, PluginManager

# host names must be a list of allowed host names (glob syntax allowed)
auth = Auth(db, host_names=myconf.get('host.names'))
service = Service()
plugins = PluginManager()

# -------------------------------------------------------------------------
# create all tables needed by auth if not custom tables
# -------------------------------------------------------------------------
auth.define_tables(username=False, signature=False)

# -------------------------------------------------------------------------
# configure email
# -------------------------------------------------------------------------
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else myconf.get('smtp.server')
mail.settings.sender = myconf.get('smtp.sender')
mail.settings.login = myconf.get('smtp.login')
mail.settings.tls = myconf.get('smtp.tls') or False
mail.settings.ssl = myconf.get('smtp.ssl') or False

# -------------------------------------------------------------------------
# configure auth policy
# -------------------------------------------------------------------------
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = True
auth.settings.reset_password_requires_verification = True

# -------------------------------------------------------------------------
# Define your tables below (or better in another model file) for example
#
# >>> db.define_table('mytable', Field('myfield', 'string'))
#
# Fields can be 'string','text','password','integer','double','boolean'
#       'date','time','datetime','blob','upload', 'reference TABLENAME'
# There is an implicit 'id integer autoincrement' field
# Consult manual for more options, validators, etc.
#
# More API examples for controllers:
#
# >>> db.mytable.insert(myfield='value')
# >>> rows = db(db.mytable.myfield == 'value').select(db.mytable.ALL)
# >>> for row in rows: print row.id, row.myfield
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
# after defining tables, uncomment below to enable auditing
# -------------------------------------------------------------------------
# auth.enable_record_versioning(db)
