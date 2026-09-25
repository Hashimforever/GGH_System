import os

files = [
    'accounts/templates/accounts/user_list.html', 
    'accounts/templates/accounts/role_list.html', 
    'committee/templates/committee/position_list.html', 
    'committee/templates/committee/assignment_list.html', 
    'audit/templates/audit/auditlog_list.html',
    'loans/templates/loans/dashboard.html'
]

for f in files:
    try:
        with open(f, 'r') as file:
            content = file.read()
        content = content.replace('class="table table-striped"', 'class="table table-striped datatable"')
        content = content.replace('class="table table-striped table-sm"', 'class="table table-striped table-sm datatable"')
        with open(f, 'w') as file:
            file.write(content)
        print(f"Updated {f}")
    except Exception as e:
        print(f"Skipped {f}: {e}")
