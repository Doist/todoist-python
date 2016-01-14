import time
import datetime
import os

import todoist


def cleanup(api_token):
    api = todoist.api.TodoistAPI(api_token)
    api.api_endpoint = 'https://local.todoist.com'
    api.sync(resource_types=['all'])
    for filter in api.state['Filters'][:]:
        filter.delete()
    api.commit()
    for label in api.state['Labels'][:]:
        label.delete()
    api.commit()
    for reminder in api.state['Reminders'][:]:
        reminder.delete()
    api.commit()
    for note in api.state['Notes'][:]:
        note.delete()
    api.commit()
    for note in api.state['ProjectNotes'][:]:
        note.delete()
    api.commit()
    for item in api.state['Items'][:]:
        item.delete()
    api.commit()
    for project in api.state['Projects'][:]:
        if project['name'] != 'Inbox':
            project.delete()
    api.commit()


def test_login(user_email, user_password, api_token):
    api = todoist.api.TodoistAPI()
    api.api_endpoint = 'https://local.todoist.com'
    response = api.login(user_email, user_password)
    assert 'api_token' in response
    assert response['api_token'] == api_token
    assert 'token' in response
    assert response['token'] == api_token
    response = api.user.sync()
    assert 'User' in response
    assert 'token' in response['User']
    assert response['User']['token'] == api_token


def test_register():
    api = todoist.api.TodoistAPI()
    api.api_endpoint = 'https://local.todoist.com'
    now = str(int(time.time()))
    email = 'user' + now + '@example.org'
    full_name = 'User' + now
    password = 'pass' + now
    response = api.register(email, full_name, password)
    assert 'email' in response
    assert 'full_name' in response
    assert response['email'] == email
    assert response['full_name'] == full_name
    response = api.delete_user(password)
    assert response == 'ok'


def test_link(api_token):
    api = todoist.api.TodoistAPI(api_token)
    api.api_endpoint = 'https://local.todoist.com'
    response = api.get_redirect_link()
    assert 'link' in response


def test_stats(api_token):
    api = todoist.api.TodoistAPI(api_token)
    api.api_endpoint = 'https://local.todoist.com'
    response = api.get_productivity_stats()
    assert 'days_items' in response
    assert 'week_items' in response
    assert 'karma_trend' in response
    assert 'karma_last_update' in response


def test_query(api_token):
    cleanup(api_token)

    api = todoist.api.TodoistAPI(api_token)
    api.api_endpoint = 'https://local.todoist.com'

    api.projects.sync()
    inbox = [p for p in api.state['Projects'] if p['name'] == 'Inbox'][0]
    item1 = api.items.add('Item1', inbox['id'], date_string='tomorrow')
    item2 = api.items.add('Item2', inbox['id'], priority=4)
    api.commit()

    response = api.query(['tomorrow', 'p1'])
    for query in response:
        if query['query'] == 'tomorrow':
            assert 'Item1' in [p['content'] for p in query['data']]
            assert 'Item2' not in [p['content'] for p in query['data']]
        if query['query'] == 'p1':
            assert 'Item1' not in [p['content'] for p in query['data']]
            assert 'Item2' in [p['content'] for p in query['data']]

    item1.delete()
    item2.delete()
    api.commit()


def test_user(api_token):
    api = todoist.api.TodoistAPI(api_token)
    api.api_endpoint = 'https://local.todoist.com'
    api.user.sync()
    date_format = api.state['User']['date_format']
    date_format_new = 1 - date_format
    api.user.update(date_format=date_format_new)
    api.commit()
    api.seq_no = 0
    api.user.sync()
    assert date_format_new == api.state['User']['date_format']
    api.user.update_goals(vacation_mode=1)
    api.commit()
    api.user.update_goals(vacation_mode=0)
    api.commit()


def test_project(api_token):
    cleanup(api_token)

    api = todoist.api.TodoistAPI(api_token)
    api.api_endpoint = 'https://local.todoist.com'

    project1 = api.projects.add('Project1')
    api.commit()
    response = api.projects.sync()
    assert response['Projects'][0]['name'] == 'Project1'
    assert 'Project1' in [p['name'] for p in api.state['Projects']]
    assert api.projects.get_by_id(project1['id']) == project1

    project1.archive()
    api.commit()
    response = api.projects.sync()
    assert response['Projects'][0]['name'] == 'Project1'
    assert response['Projects'][0]['is_archived'] == 1
    assert 'Project1' in [p['name'] for p in api.state['Projects']]

    project1.unarchive()
    api.commit()
    response = api.projects.sync()
    assert response['Projects'][0]['name'] == 'Project1'
    assert response['Projects'][0]['is_archived'] == 0
    assert 'Project1' in [p['name'] for p in api.state['Projects']]

    project1.update(name='UpdatedProject1')
    api.commit()
    response = api.projects.sync()
    assert response['Projects'][0]['name'] == 'UpdatedProject1'
    assert 'UpdatedProject1' in [p['name'] for p in api.state['Projects']]
    assert api.projects.get_by_id(project1['id']) == project1

    project2 = api.projects.add('Project2')
    api.commit()
    api.projects.sync()
    api.projects.update_orders_indents({project1['id']: [1, 2],
                                       project2['id']: [2, 3]})
    api.commit()
    response = api.projects.sync()
    for project in response['Projects']:
        if project['id'] == project1['id']:
            assert project['item_order'] == 1
            assert project['indent'] == 2
        if project['id'] == project2['id']:
            assert project['item_order'] == 2
            assert project['indent'] == 3

    project1.delete()
    api.commit()
    response = api.projects.sync()
    assert response['Projects'][0]['name'] == 'UpdatedProject1'
    assert response['Projects'][0]['is_deleted'] == 1
    assert 'UpdatedProject1' not in [p['name'] for p in api.state['Projects']]

    api.projects.archive(project2['id'])
    api.commit()
    response = api.projects.sync()
    assert response['Projects'][0]['name'] == 'Project2'
    assert response['Projects'][0]['is_archived'] == 1

    api.projects.unarchive(project2['id'])
    api.commit()
    response = api.projects.sync()
    assert response['Projects'][0]['name'] == 'Project2'
    assert response['Projects'][0]['is_archived'] == 0

    api.projects.update(project2['id'], name='UpdatedProject2')
    api.commit()
    response = api.projects.sync()
    assert response['Projects'][0]['name'] == 'UpdatedProject2'

    api.projects.delete([project2['id']])
    api.commit()
    response = api.projects.sync()
    assert response['Projects'][0]['name'] == 'UpdatedProject2'
    assert response['Projects'][0]['is_deleted'] == 1


def test_item(api_token):
    cleanup(api_token)

    api = todoist.api.TodoistAPI(api_token)
    api.api_endpoint = 'https://local.todoist.com'

    response = api.add_item('Item1')
    assert response['content'] == 'Item1'
    api.items.sync()
    assert 'Item1' in [p['content'] for p in api.state['Items']]
    item1 = [i for i in api.state['Items'] if i['content'] == 'Item1'][0]
    assert api.items.get_by_id(item1['id']) == item1
    item1.delete()
    api.commit()
    api.items.sync()

    api.projects.sync()
    inbox = [p for p in api.state['Projects'] if p['name'] == 'Inbox'][0]
    item1 = api.items.add('Item1', inbox['id'])
    api.commit()
    response = api.items.sync()
    assert response['Items'][0]['content'] == 'Item1'
    assert 'Item1' in [p['content'] for p in api.state['Items']]
    assert api.items.get_by_id(item1['id']) == item1

    item1.complete()
    api.commit()
    response = api.items.sync()
    assert response['Items'][0]['content'] == 'Item1'
    assert response['Items'][0]['checked'] == 1
    assert 'Item1' in [p['content'] for p in api.state['Items']]

    item1.uncomplete()
    api.commit()
    response = api.items.sync()
    assert response['Items'][0]['content'] == 'Item1'
    assert response['Items'][0]['checked'] == 0
    assert 'Item1' in [p['content'] for p in api.state['Items']]

    project1 = api.projects.add('Project1')
    api.commit()
    response = api.projects.sync()

    item1.move(project1['id'])
    api.commit()
    response = api.items.sync()
    assert response['Items'][0]['content'] == 'Item1'
    assert response['Items'][0]['project_id'] == project1['id']

    item1.update(content='UpdatedItem1')
    api.commit()
    response = api.items.sync()
    assert response['Items'][0]['content'] == 'UpdatedItem1'
    assert 'UpdatedItem1' in [p['content'] for p in api.state['Items']]
    assert api.items.get_by_id(item1['id']) == item1

    date_string = datetime.datetime(2038, 01, 19, 03, 14, 07)
    item2 = api.items.add('Item2', inbox['id'], date_string=date_string)
    api.commit()
    api.items.sync()

    api.items.uncomplete_update_meta(inbox['id'], {item1['id']: [0, 0, 1],
                                                   item2['id']: [0, 0, 2]})
    api.commit()
    response = api.items.sync()
    for item in response['Items']:
        if item['id'] == item1['id']:
            assert item['item_order'] == 1
        if item['id'] == item2['id']:
            assert item['item_order'] == 2

    now = time.time()
    tomorrow = time.gmtime(now + 24*3600)
    new_date_utc = time.strftime("%Y-%m-%dT%H:%M", tomorrow)
    api.items.update_date_complete(item1['id'], new_date_utc, 'every day', 0)
    api.commit()
    response = api.items.sync()
    assert response['Items'][0]['date_string'] == 'every day'

    api.items.update_orders_indents({item1['id']: [2, 2],
                                    item2['id']: [1, 3]})
    api.commit()
    response = api.items.sync()
    for item in response['Items']:
        if item['id'] == item1['id']:
            assert item['item_order'] == 2
            assert item['indent'] == 2
        if item['id'] == item2['id']:
            assert item['item_order'] == 1
            assert item['indent'] == 3

    api.items.update_day_orders({item1['id']: 1, item2['id']: 2})
    api.commit()
    response = api.items.sync()
    for item in response['Items']:
        if item['id'] == item1['id']:
            assert item['day_order'] == 1
        if item['id'] == item2['id']:
            assert item['day_order'] == 2

    item1.delete()
    api.commit()
    response = api.items.sync()
    assert response['Items'][0]['content'] == 'UpdatedItem1'
    assert response['Items'][0]['is_deleted'] == 1
    assert 'UpdatedItem1' not in [p['content'] for p in api.state['Items']]

    api.items.complete([item2['id']])
    api.commit()
    response = api.items.sync()
    assert response['Items'][0]['content'] == 'Item2'
    assert response['Items'][0]['checked'] == 1

    api.items.uncomplete(item2['project_id'], [item2['id']])
    api.commit()
    response = api.items.sync()
    assert response['Items'][0]['content'] == 'Item2'
    assert response['Items'][0]['checked'] == 0

    api.items.move({item2['project_id']: [item2['id']]}, project1['id'])
    api.commit()
    response = api.items.sync()
    assert response['Items'][0]['content'] == 'Item2'
    assert response['Items'][0]['project_id'] == project1['id']

    api.items.update(item2['id'], content='UpdatedItem2')
    api.commit()
    response = api.items.sync()
    assert response['Items'][0]['content'] == 'UpdatedItem2'

    api.items.delete([item2['id']])
    api.commit()
    response = api.items.sync()
    assert response['Items'][0]['content'] == 'UpdatedItem2'
    assert response['Items'][0]['is_deleted'] == 1

    project1.delete()
    api.commit()


def test_label(api_token):
    cleanup(api_token)

    api = todoist.api.TodoistAPI(api_token)
    api.api_endpoint = 'https://local.todoist.com'

    label1 = api.labels.add('Label1')
    api.commit()
    response = api.labels.sync()
    assert response['Labels'][0]['name'] == 'Label1'
    assert 'Label1' in [p['name'] for p in api.state['Labels']]
    assert api.labels.get_by_id(label1['id']) == label1

    label1.update(name='UpdatedLabel1')
    api.commit()
    response = api.labels.sync()
    assert response['Labels'][0]['name'] == 'UpdatedLabel1'
    assert 'UpdatedLabel1' in [p['name'] for p in api.state['Labels']]
    assert api.labels.get_by_id(label1['id']) == label1

    label2 = api.labels.add('Label2')
    api.commit()
    api.labels.sync()

    api.labels.update_orders({label1['id']: 1, label2['id']: 2})
    api.commit()
    response = api.labels.sync()
    for label in response['Labels']:
        if label['id'] == label1['id']:
            assert label['item_order'] == 1
        if label['id'] == label2['id']:
            assert label['item_order'] == 2

    label1.delete()
    api.commit()
    response = api.labels.sync()
    assert response['Labels'][0]['name'] == 'UpdatedLabel1'
    assert response['Labels'][0]['is_deleted'] == 1
    assert 'UpdatedLabel1' not in [p['name'] for p in api.state['Labels']]

    api.labels.update(label2['id'], name='UpdatedLabel2')
    api.commit()
    response = api.labels.sync()
    assert response['Labels'][0]['name'] == 'UpdatedLabel2'

    api.labels.delete(label2['id'])
    api.commit()
    response = api.labels.sync()
    assert response['Labels'][0]['name'] == 'UpdatedLabel2'
    assert response['Labels'][0]['is_deleted'] == 1


def test_note(api_token):
    cleanup(api_token)

    api = todoist.api.TodoistAPI(api_token)
    api.api_endpoint = 'https://local.todoist.com'

    api.projects.sync()
    inbox = [p for p in api.state['Projects'] if p['name'] == 'Inbox'][0]
    item1 = api.items.add('Item1', inbox['id'])
    api.commit()
    response = api.notes.sync()

    note1 = api.notes.add(item1['id'], 'Note1')
    api.commit()
    response = api.notes.sync()
    assert response['Notes'][0]['content'] == 'Note1'
    assert 'Note1' in [p['content'] for p in api.state['Notes']]
    assert api.notes.get_by_id(note1['id']) == note1

    note1.update(content='UpdatedNote1')
    api.commit()
    response = api.notes.sync()
    assert response['Notes'][0]['content'] == 'UpdatedNote1'
    assert 'UpdatedNote1' in [p['content'] for p in api.state['Notes']]
    assert api.notes.get_by_id(note1['id']) == note1

    note1.delete()
    api.commit()
    response = api.notes.sync()
    assert response['Notes'][0]['content'] == 'UpdatedNote1'
    assert response['Notes'][0]['is_deleted'] == 1
    assert 'UpdatedNote1' not in [p['content'] for p in api.state['Notes']]

    note2 = api.notes.add(item1['id'], 'Note2')
    api.commit()
    response = api.notes.sync()
    assert response['Notes'][0]['content'] == 'Note2'

    api.notes.update(note2['id'], content='UpdatedNote2')
    api.commit()
    response = api.notes.sync()
    assert response['Notes'][0]['content'] == 'UpdatedNote2'

    api.notes.delete(note2['id'])
    api.commit()
    response = api.notes.sync()
    assert response['Notes'][0]['content'] == 'UpdatedNote2'
    assert response['Notes'][0]['is_deleted'] == 1

    item1.delete()
    api.commit()


def test_projectnote(api_token):
    cleanup(api_token)

    api = todoist.api.TodoistAPI(api_token)
    api.api_endpoint = 'https://local.todoist.com'

    project1 = api.projects.add('Project1')
    api.commit()
    api.projects.sync()
    api.project_notes.sync()

    note1 = api.project_notes.add(project1['id'], 'Note1')
    api.commit()
    response = api.project_notes.sync()
    assert response['ProjectNotes'][0]['content'] == 'Note1'
    assert 'Note1' in [p['content'] for p in api.state['ProjectNotes']]
    assert api.project_notes.get_by_id(note1['id']) == note1

    note1.update(content='UpdatedNote1')
    api.commit()
    response = api.project_notes.sync()
    assert response['ProjectNotes'][0]['content'] == 'UpdatedNote1'
    assert 'UpdatedNote1' in [p['content'] for p in api.state['ProjectNotes']]
    assert api.project_notes.get_by_id(note1['id']) == note1

    note1.delete()
    api.commit()
    response = api.project_notes.sync()
    assert response['ProjectNotes'][0]['content'] == 'UpdatedNote1'
    assert response['ProjectNotes'][0]['is_deleted'] == 1
    assert 'UpdatedNote1' not in [p['content'] for p in api.state['ProjectNotes']]

    note2 = api.project_notes.add(project1['id'], 'Note2')
    api.commit()
    response = api.project_notes.sync()
    assert response['ProjectNotes'][0]['content'] == 'Note2'

    api.project_notes.update(note2['id'], content='UpdatedNote2')
    api.commit()
    response = api.project_notes.sync()
    assert response['ProjectNotes'][0]['content'] == 'UpdatedNote2'

    api.project_notes.delete(note2['id'])
    api.commit()
    response = api.project_notes.sync()
    assert response['ProjectNotes'][0]['content'] == 'UpdatedNote2'
    assert response['ProjectNotes'][0]['is_deleted'] == 1

    project1.delete()
    api.commit()


def test_filter(api_token):
    cleanup(api_token)

    api = todoist.api.TodoistAPI(api_token)
    api.api_endpoint = 'https://local.todoist.com'

    filter1 = api.filters.add('Filter1', 'no due date')
    api.commit()
    response = api.filters.sync()
    assert response['Filters'][0]['name'] == 'Filter1'
    assert 'Filter1' in [p['name'] for p in api.state['Filters']]
    assert api.filters.get_by_id(filter1['id']) == filter1

    filter1.update(name='UpdatedFilter1')
    api.commit()
    response = api.filters.sync()
    assert response['Filters'][0]['name'] == 'UpdatedFilter1'
    assert 'UpdatedFilter1' in [p['name'] for p in api.state['Filters']]
    assert api.filters.get_by_id(filter1['id']) == filter1

    filter2 = api.filters.add('Filter2', 'today')
    api.commit()
    api.filters.sync()

    api.filters.update_orders({filter1['id']: 2, filter2['id']: 1})
    api.commit()
    response = api.filters.sync()
    for filter in response['Filters']:
        if filter['id'] == filter1['id']:
            assert filter['item_order'] == 2
        if filter['id'] == filter2['id']:
            assert filter['item_order'] == 1

    filter1.delete()
    api.commit()
    response = api.filters.sync()
    assert response['Filters'][0]['name'] == 'UpdatedFilter1'
    assert response['Filters'][0]['is_deleted'] == 1
    assert 'UpdatedFilter1' not in [p['name'] for p in api.state['Filters']]

    api.filters.update(filter2['id'], name='UpdatedFilter2')
    api.commit()
    response = api.filters.sync()
    assert response['Filters'][0]['name'] == 'UpdatedFilter2'

    api.filters.delete(filter2['id'])
    api.commit()
    response = api.filters.sync()
    assert response['Filters'][0]['name'] == 'UpdatedFilter2'
    assert response['Filters'][0]['is_deleted'] == 1


def test_reminder(api_token):
    cleanup(api_token)

    api = todoist.api.TodoistAPI(api_token)
    api.api_endpoint = 'https://local.todoist.com'

    api.projects.sync()
    inbox = [p for p in api.state['Projects'] if p['name'] == 'Inbox'][0]
    item1 = api.items.add('Item1', inbox['id'], date_string='tomorrow')
    api.commit()
    api.items.sync()

    # relative
    reminder1 = api.reminders.add(item1['id'], minute_offset=30)
    api.commit()
    response = api.reminders.sync()
    assert response['Reminders'][0]['minute_offset'] == 30
    assert reminder1['id'] in [p['id'] for p in api.state['Reminders']]
    assert api.reminders.get_by_id(reminder1['id']) == reminder1

    reminder1.update(minute_offset=str(15))
    api.commit()
    response = api.reminders.sync()
    assert response['Reminders'][0]['minute_offset'] == 15
    assert reminder1['id'] in [p['id'] for p in api.state['Reminders']]
    assert api.reminders.get_by_id(reminder1['id']) == reminder1

    reminder1.delete()
    api.commit()
    response = api.reminders.sync()
    assert response['Reminders'][0]['minute_offset'] == 15
    assert response['Reminders'][0]['is_deleted'] == 1
    assert reminder1['id'] not in [p['id'] for p in api.state['Reminders']]

    # absolute
    now = time.time()
    tomorrow = time.gmtime(now + 24*3600)
    due_date_utc = time.strftime("%Y-%m-%dT%H:%M", tomorrow)
    due_date_utc_long = time.strftime("%a %d %b %Y %H:%M:00 +0000", tomorrow)
    reminder2 = api.reminders.add(item1['id'], due_date_utc=due_date_utc)
    api.commit()
    response = api.reminders.sync()
    tomorrow = time.gmtime(time.time() + 24*3600)
    assert response['Reminders'][0]['due_date_utc'] == due_date_utc_long
    assert reminder2['id'] in [p['id'] for p in api.state['Reminders']]
    assert api.reminders.get_by_id(reminder2['id']) == reminder2

    tomorrow = time.gmtime(now + 24*3600 + 60)
    due_date_utc = time.strftime("%Y-%m-%dT%H:%M", tomorrow)
    due_date_utc_long = time.strftime("%a %d %b %Y %H:%M:00 +0000", tomorrow)
    api.reminders.update(reminder2['id'], due_date_utc=due_date_utc)
    api.commit()
    response = api.reminders.sync()
    assert response['Reminders'][0]['due_date_utc'] == due_date_utc_long
    assert reminder2['id'] in [p['id'] for p in api.state['Reminders']]
    assert api.reminders.get_by_id(reminder2['id']) == reminder2

    api.reminders.delete(reminder2['id'])
    api.commit()
    response = api.reminders.sync()
    assert response['Reminders'][0]['due_date_utc'] == due_date_utc_long
    assert response['Reminders'][0]['is_deleted'] == 1
    assert reminder2['id'] not in [p['id'] for p in api.state['Reminders']]

    item1.delete()
    api.commit()


def test_locations(api_token):
    api = todoist.api.TodoistAPI(api_token)
    api.api_endpoint = 'https://local.todoist.com'

    api.locations.sync()
    api.locations.clear()
    api.commit()
    api.locations.sync()
    assert api.state['Locations'] == []


def test_live_notifications(api_token):
    api = todoist.api.TodoistAPI(api_token)
    api.api_endpoint = 'https://local.todoist.com'

    response = api.live_notifications.sync()
    api.live_notifications.mark_as_read(api.state['LiveNotificationsLastRead'])
    api.commit()
    response = api.live_notifications.sync()
    assert response['LiveNotificationsLastRead'] == \
        api.state['LiveNotificationsLastRead']


def test_share(api_token, api_token2):
    cleanup(api_token)
    cleanup(api_token2)

    api = todoist.api.TodoistAPI(api_token)
    api.api_endpoint = 'https://local.todoist.com'

    api2 = todoist.api.TodoistAPI(api_token2)
    api2.api_endpoint = 'https://local.todoist.com'

    # accept
    project1 = api.projects.add('Project1')
    api.commit()
    api.projects.sync()

    api2.user.sync()
    api.share_project(project1['id'], api2['User']['email'])
    api.commit()
    response = api.projects.sync()
    assert response['Projects'][0]['name'] == project1['name']
    assert response['Projects'][0]['shared']

    response2 = api2.live_notifications.sync()
    api.user.sync()
    assert response2['LiveNotifications'][0]['project_name'] == \
        project1['name']
    assert response2['LiveNotifications'][0]['from_user']['email'] == \
        api['User']['email']
    invitation = response2['LiveNotifications'][0]

    api2.invitations.accept(invitation['invitation_id'],
                            invitation['invitation_secret'])
    api2.commit()
    response2 = api2.live_notifications.sync()
    assert response2['LiveNotifications'][0]['invitation_id'] == \
        invitation['invitation_id']
    assert response2['LiveNotifications'][0]['state'] == 'accepted'
    response2 = api2.projects.sync()
    assert response2['Projects'][0]['shared']
    response2 = api2.collaborator_states.sync()
    assert api['User']['id'] in \
        [p['user_id'] for p in response2['CollaboratorStates']]
    assert api2['User']['id'] in \
        [p['user_id'] for p in response2['CollaboratorStates']]

    response = api.live_notifications.sync()
    assert response['LiveNotifications'][0]['invitation_id'] == \
        invitation['invitation_id']
    assert response['LiveNotifications'][0]['notification_type'] == \
        'share_invitation_accepted'
    response = api.projects.sync()
    assert response['Projects'][0]['shared']

    # ownership
    project1 = [p for p in api2.state['Projects']
                if p['name'] == 'Project1'][0]
    api2.take_ownership(project1['id'])
    api2.commit()
    api2.projects.sync()

    project1 = [p for p in api.state['Projects'] if p['name'] == 'Project1'][0]
    api.take_ownership(project1['id'])
    api.commit()
    api.projects.sync()

    api.delete_collaborator(project1['id'], api2['User']['email'])
    api.commit()
    api.collaborators.sync()
    api2.projects.sync()

    project1 = [p for p in api.state['Projects'] if p['name'] == 'Project1'][0]
    project1.delete()
    api.commit()
    api.projects.sync()

    # reject
    project2 = api.projects.add('Project2')
    api.commit()
    api.projects.sync()

    api.share_project(project2['id'], api2['User']['email'])
    api.commit()
    response = api.projects.sync()
    assert response['Projects'][0]['name'] == project2['name']
    assert response['Projects'][0]['shared']

    response2 = api2.live_notifications.sync()
    assert response2['LiveNotifications'][0]['project_name'] == \
        project2['name']
    assert response2['LiveNotifications'][0]['from_user']['email'] == \
        api['User']['email']
    invitation2 = response2['LiveNotifications'][0]

    api2.invitations.reject(invitation2['invitation_id'],
                            invitation2['invitation_secret'])
    api2.commit()
    response2 = api2.live_notifications.sync()
    assert response2['LiveNotifications'][0]['invitation_id'] == \
        invitation2['invitation_id']
    assert response2['LiveNotifications'][0]['state'] == 'rejected'
    response2 = api2.projects.sync()
    assert len(response2['Projects']) == 0
    response2 = api2.collaborator_states.sync()
    assert len(response2['CollaboratorStates']) == 0

    response = api.live_notifications.sync()
    assert response['LiveNotifications'][0]['invitation_id'] == \
        invitation2['invitation_id']
    assert response['LiveNotifications'][0]['notification_type'] == \
        'share_invitation_rejected'
    response = api.projects.sync()
    assert not response['Projects'][0]['shared']

    project2 = [p for p in api.state['Projects'] if p['name'] == 'Project2'][0]
    project2.delete()
    api.commit()
    api.projects.sync()

    # delete
    project3 = api.projects.add('Project3')
    api.commit()
    api.projects.sync()

    api.share_project(project3['id'], api2['User']['email'])
    api.commit()
    response = api.projects.sync()
    assert response['Projects'][0]['name'] == project3['name']
    assert response['Projects'][0]['shared']

    response2 = api2.live_notifications.sync()
    assert response2['LiveNotifications'][0]['project_name'] == \
        project3['name']
    assert response2['LiveNotifications'][0]['from_user']['email'] == \
        api['User']['email']
    invitation3 = response2['LiveNotifications'][0]

    api.invitations.delete(invitation3['invitation_id'])
    api.commit()

    project3 = [p for p in api.state['Projects'] if p['name'] == 'Project3'][0]
    project3.delete()
    api.commit()
    api.projects.sync()
