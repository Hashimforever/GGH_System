import os

os.makedirs('accounts/templates/accounts', exist_ok=True)
os.makedirs('committee/templates/committee', exist_ok=True)
os.makedirs('audit/templates/audit', exist_ok=True)

# accounts/user_list.html
with open('accounts/templates/accounts/user_list.html', 'w') as f:
    f.write('''{% extends 'base.html' %}
{% block title %}Manage Users{% endblock %}
{% block page_title %}Manage Users{% endblock %}
{% block content %}
<div class="card">
  <div class="card-header">
    <h3 class="card-title">System Users</h3>
    <div class="card-tools">
      <a href="{% url 'accounts:user_create' %}" class="btn btn-sm btn-primary">
        <i class="fas fa-plus"></i> Add User
      </a>
    </div>
  </div>
  <div class="card-body p-0">
    <table class="table table-striped">
      <thead><tr><th>Username</th><th>Name</th><th>Email</th><th>Roles</th><th>Staff</th><th>Active</th><th>Actions</th></tr></thead>
      <tbody>
        {% for u in users %}
        <tr>
          <td>{{ u.username }}</td>
          <td>{{ u.get_full_name }}</td>
          <td>{{ u.email }}</td>
          <td>{% for r in u.roles.all %}<span class="badge badge-info">{{ r.name }}</span> {% endfor %}</td>
          <td>{% if u.is_staff %}<i class="fas fa-check text-success"></i>{% else %}<i class="fas fa-times text-danger"></i>{% endif %}</td>
          <td>{% if u.is_active %}<i class="fas fa-check text-success"></i>{% else %}<i class="fas fa-times text-danger"></i>{% endif %}</td>
          <td>
            <a href="{% url 'accounts:user_update' u.pk %}" class="btn btn-xs btn-primary"><i class="fas fa-edit"></i></a>
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</div>
{% endblock %}''')

# accounts/user_form.html
with open('accounts/templates/accounts/user_form.html', 'w') as f:
    f.write('''{% extends 'base.html' %}
{% block title %}{% if object %}Edit User{% else %}Add User{% endif %}{% endblock %}
{% block page_title %}{% if object %}Edit User: {{ object.username }}{% else %}Add User{% endif %}{% endblock %}
{% block content %}
<div class="card card-primary">
  <div class="card-header"><h3 class="card-title">User Details</h3></div>
  <form method="post">{% csrf_token %}
    <div class="card-body">
      {{ form.as_p }}
    </div>
    <div class="card-footer">
      <button type="submit" class="btn btn-primary">Save</button>
      <a href="{% url 'accounts:user_list' %}" class="btn btn-default">Cancel</a>
    </div>
  </form>
</div>
{% endblock %}''')

# accounts/role_list.html
with open('accounts/templates/accounts/role_list.html', 'w') as f:
    f.write('''{% extends 'base.html' %}
{% block title %}Manage Roles{% endblock %}
{% block page_title %}Manage Roles & Permissions{% endblock %}
{% block content %}
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Roles</h3>
    <div class="card-tools">
      <a href="{% url 'accounts:role_create' %}" class="btn btn-sm btn-primary">
        <i class="fas fa-plus"></i> Add Role
      </a>
    </div>
  </div>
  <div class="card-body p-0">
    <table class="table table-striped">
      <thead><tr><th>Name</th><th>Description</th><th>Users</th><th>Actions</th></tr></thead>
      <tbody>
        {% for r in roles %}
        <tr>
          <td>{{ r.name }}</td>
          <td>{{ r.description }}</td>
          <td>{{ r.users.count }}</td>
          <td>
            <a href="{% url 'accounts:role_update' r.pk %}" class="btn btn-xs btn-primary"><i class="fas fa-edit"></i></a>
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</div>
{% endblock %}''')

# accounts/role_form.html
with open('accounts/templates/accounts/role_form.html', 'w') as f:
    f.write('''{% extends 'base.html' %}
{% block title %}{% if object %}Edit Role{% else %}Add Role{% endif %}{% endblock %}
{% block page_title %}{% if object %}Edit Role: {{ object.name }}{% else %}Add Role{% endif %}{% endblock %}
{% block content %}
<div class="card card-primary">
  <div class="card-header"><h3 class="card-title">Role Details</h3></div>
  <form method="post">{% csrf_token %}
    <div class="card-body">
      {{ form.as_p }}
    </div>
    <div class="card-footer">
      <button type="submit" class="btn btn-primary">Save</button>
      <a href="{% url 'accounts:role_list' %}" class="btn btn-default">Cancel</a>
    </div>
  </form>
</div>
{% endblock %}''')
