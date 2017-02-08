@auth.requires_login()
def experiments():
    experiments = db(db.experiments).select()
    search_widget=SQLFORM.factory(Field('search','list:reference experiments',label=T("Search"),
				  requires = IS_IN_DB(db, db.experiments, '%(code)s', multiple=True)),
				  buttons=[])
    return dict(search=search_widget)

@auth.requires_login()
def groups():
    groups = db(db.groups).select()
    search_widget=SQLFORM.factory(Field('search','list:reference groups',label=T("Search"),
				  requires = IS_IN_DB(db, db.groups, '%(code)s : %(name)s', multiple=True)),
				  buttons=[])
    return dict(search=search_widget)

@auth.requires_login()
def patients_per_experiment():
    experiments = request.vars['expts[]']
    html="<table class='pure-table pure-table-bordered' style='table-layout: fixed; width: 100%'>"
    html+="<thead><th>%s</th><th>%s</th></thead>" % (T("Name"),T("Experiments"))
    patients = {}
    if experiments:
        if (not (type(experiments) is list)):
            experiments = [experiments]
        rows = db(db.patient.experiments.contains(experiments, all=True)).select(orderby=db.patient.name)
        for r in rows:
            html+="<tr><td>%s</td><td>%s</td></tr>" % (r.name, db.patient.experiments.represent(r.experiments))
    html+="</table>"
    return html

@auth.requires_login()
def patients_per_group():
    groups = request.vars['groups[]']
    html="<table class='pure-table pure-table-bordered' style='table-layout: fixed; width: 100%'>"
    html+="<thead><th>%s</th><th>%s</th><th>%s</th><th>%s</th></thead>" % (T("Name"),T("Groups"),T("E-mail"),T("Phone"))
    patients = {}
    if groups:
        if (not (type(groups) is list)):
            groups = [groups]
        rows = db(db.patient.groups.contains(groups, all=True)).select(orderby=db.patient.name)
        for r in rows:
            html+="<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" \
                    % (r.name, db.patient.groups.represent(r.groups),
                       r.email,", ".join(r.phones))
    html+="</table>"
    return html
