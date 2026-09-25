import os

# committee/position_list.html
with open('committee/templates/committee/position_list.html', 'w') as f:
    f.write('''{% extends 'base.html' %}
{% block title %}Committee Positions{% endblock %}
{% block page_title %}Committee Positions{% endblock %}
{% block content %}
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Positions</h3>
    <div class="card-tools">
      <a href="{% url 'committee:position_create' %}" class="btn btn-sm btn-primary">
        <i class="fas fa-plus"></i> Add Position
      </a>
    </div>
  </div>
  <div class="card-body p-0">
    <table class="table table-striped">
      <thead><tr><th>Title</th><th>Description</th><th>Actions</th></tr></thead>
      <tbody>
        {% for p in positions %}
        <tr>
          <td>{{ p.title }}</td>
          <td>{{ p.description }}</td>
          <td>
            <a href="{% url 'committee:position_update' p.pk %}" class="btn btn-xs btn-primary"><i class="fas fa-edit"></i></a>
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</div>
{% endblock %}''')

# committee/position_form.html
with open('committee/templates/committee/position_form.html', 'w') as f:
    f.write('''{% extends 'base.html' %}
{% block title %}{% if object %}Edit Position{% else %}Add Position{% endif %}{% endblock %}
{% block page_title %}{% if object %}Edit Position{% else %}Add Position{% endif %}{% endblock %}
{% block content %}
<div class="card card-primary">
  <form method="post">{% csrf_token %}
    <div class="card-body">{{ form.as_p }}</div>
    <div class="card-footer">
      <button type="submit" class="btn btn-primary">Save</button>
      <a href="{% url 'committee:position_list' %}" class="btn btn-default">Cancel</a>
    </div>
  </form>
</div>
{% endblock %}''')

# committee/assignment_list.html
with open('committee/templates/committee/assignment_list.html', 'w') as f:
    f.write('''{% extends 'base.html' %}
{% block title %}Committee Assignments{% endblock %}
{% block page_title %}Committee Assignments{% endblock %}
{% block content %}
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Assignments</h3>
    <div class="card-tools">
      <a href="{% url 'committee:assignment_create' %}" class="btn btn-sm btn-primary">
        <i class="fas fa-plus"></i> Add Assignment
      </a>
      <a href="{% url 'committee:position_list' %}" class="btn btn-sm btn-info">Manage Positions</a>
    </div>
  </div>
  <div class="card-body p-0">
    <table class="table table-striped">
      <thead><tr><th>Member</th><th>Position</th><th>Start Date</th><th>End Date</th><th>Actions</th></tr></thead>
      <tbody>
        {% for a in assignments %}
        <tr>
          <td>{{ a.member }}</td>
          <td>{{ a.position }}</td>
          <td>{{ a.start_date }}</td>
          <td>{{ a.end_date|default:"Present" }}</td>
          <td>
            <a href="{% url 'committee:assignment_update' a.pk %}" class="btn btn-xs btn-primary"><i class="fas fa-edit"></i></a>
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</div>
{% endblock %}''')

# committee/assignment_form.html
with open('committee/templates/committee/assignment_form.html', 'w') as f:
    f.write('''{% extends 'base.html' %}
{% block title %}{% if object %}Edit Assignment{% else %}Add Assignment{% endif %}{% endblock %}
{% block page_title %}{% if object %}Edit Assignment{% else %}Add Assignment{% endif %}{% endblock %}
{% block content %}
<div class="card card-primary">
  <form method="post">{% csrf_token %}
    <div class="card-body">{{ form.as_p }}</div>
    <div class="card-footer">
      <button type="submit" class="btn btn-primary">Save</button>
      <a href="{% url 'committee:assignment_list' %}" class="btn btn-default">Cancel</a>
    </div>
  </form>
</div>
{% endblock %}''')
