@auth.requires_login()
def experiments():
    experiments = db(db.experiments).select()
    search_widget=SQLFORM.factory(Field('search','list:reference experiments',label=T("Search"),
				  requires = IS_IN_DB(db, db.experiments, '%(code)s', multiple=True)),
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
