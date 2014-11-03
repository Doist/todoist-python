import time
import os
import todoist


def cleanup(api):
    for filter in api.state['Filters']:
        filter.delete()
    api.commit()
    for item in api.state['Items']:
        item.delete()
    api.commit()
    for label in api.state['Labels']:
        label.delete()
    api.commit()
    for note in api.state['Notes']:
        note.delete()
    api.commit()
    for project in api.state['Projects']:
        if project['name'] != 'Inbox':
            project.delete()
    api.commit()
    for reminder in api.state['Reminders']:
        reminder.delete()
    api.commit()
    api.get()


def test_login(user_email, user_password):
    api = todoist.api.TodoistAPI()
    api.api_url = 'https://local.todoist.com/API/'
    api.sync_url = 'https://local.todoist.com/TodoistSync/v5.3/'
    response = api.login(user_email, user_password)
    assert 'api_token' in response
    response = api.get()
    assert 'Projects' in response
    assert 'Items' in response


def test_ping(api_token):
    api = todoist.api.TodoistAPI()
    api.api_url = 'https://local.todoist.com/API/'
    api.sync_url = 'https://local.todoist.com/TodoistSync/v5.3/'
    assert api.ping(api_token) == 'ok'


def test_timezones():
    api = todoist.api.TodoistAPI()
    api.api_url = 'https://local.todoist.com/API/'
    api.sync_url = 'https://local.todoist.com/TodoistSync/v5.3/'
    assert [u'UTC', u'(GMT+0000) UTC'] in api.get_timezones()


def test_stats(api_token):
    api = todoist.api.TodoistAPI(api_token)
    api.api_url = 'https://local.todoist.com/API/'
    api.sync_url = 'https://local.todoist.com/TodoistSync/v5.3/'
    response = api.get_productivity_stats(api_token)
    assert 'days_items' in response
    assert 'week_items' in response
    assert 'karma_trend' in response
    assert 'karma_last_update' in response


def test_query(api_token):
    api = todoist.api.TodoistAPI(api_token)
    api.api_url = 'https://local.todoist.com/API/'
    api.sync_url = 'https://local.todoist.com/TodoistSync/v5.3/'
    api.get()

    cleanup(api)

    inbox = api.project_get_by_name('Inbox')
    item1 = api.item_add('Item1', inbox['id'], date_string='tomorrow')
    item2 = api.item_add('Item2', inbox['id'], priority=4)
    api.commit()
    api.get()

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
    api.get()


def test_upload(api_token):
    api = todoist.api.TodoistAPI(api_token)
    api.api_url = 'https://local.todoist.com/API/'
    api.sync_url = 'https://local.todoist.com/TodoistSync/v5.3/'
    api.get()

    filename = '/tmp/example.txt'
    f = open(filename, 'w')
    f.write('testing\n')
    f.close()

    response = api.upload_file('/tmp/example.txt')
    assert response['file_name'] == 'example.txt'
    assert response['file_size'] == 8
    assert response['file_type'] == 'text/plain'

    os.remove(filename)


def test_user(api_token):
    api = todoist.api.TodoistAPI(api_token)
    api.api_url = 'https://local.todoist.com/API/'
    api.sync_url = 'https://local.todoist.com/TodoistSync/v5.3/'
    api.get()
    date_format = api.state['User']['date_format']
    date_format_new = 1 - date_format
    api.user_update(date_format=date_format_new)
    api.commit()
    api.seq_no = 0
    api.get()
    assert date_format_new == api.state['User']['date_format']


def test_get(api_token):
    api = todoist.api.TodoistAPI(api_token)
    api.api_url = 'https://local.todoist.com/API/'
    api.sync_url = 'https://local.todoist.com/TodoistSync/v5.3/'
    response = api.get()
    assert 'Projects' in response
    assert 'Items' in response


def test_project(api_token):
    api = todoist.api.TodoistAPI(api_token)
    api.api_url = 'https://local.todoist.com/API/'
    api.sync_url = 'https://local.todoist.com/TodoistSync/v5.3/'
    api.get()

    cleanup(api)

    project1 = api.project_add('Project1')
    api.commit()
    response = api.get()
    assert response['Projects'][0]['name'] == 'Project1'
    assert 'Project1' in [p['name'] for p in api.state['Projects']]
    assert api.project_get_by_id(project1['id']) == project1
    assert api.project_get_by_name(project1['name']) == project1

    project1.archive()
    api.commit()
    response = api.get()
    assert response['Projects'][0]['name'] == 'Project1'
    assert response['Projects'][0]['is_archived'] == 1
    assert 'Project1' in [p['name'] for p in api.state['Projects']]

    project1.unarchive()
    api.commit()
    response = api.get()
    assert response['Projects'][0]['name'] == 'Project1'
    assert response['Projects'][0]['is_archived'] == 0
    assert 'Project1' in [p['name'] for p in api.state['Projects']]

    project1.update(name='UpdatedProject1')
    api.commit()
    response = api.get()
    assert response['Projects'][0]['name'] == 'UpdatedProject1'
    assert 'UpdatedProject1' in [p['name'] for p in api.state['Projects']]
    assert api.project_get_by_id(project1['id']) == project1
    assert api.project_get_by_name(project1['name']) == project1

    project2 = api.project_add('Project2')
    api.commit()
    api.get()
    api.project_update_orders_indents({project1['id']: [1, 2],
                                       project2['id']: [2, 3]})
    api.commit()
    response = api.get()
    for project in response['Projects']:
        if project['id'] == project1['id']:
            assert project['item_order'] == 1
            assert project['indent'] == 2
        if project['id'] == project2['id']:
            assert project['item_order'] == 2
            assert project['indent'] == 3

    project1.delete()
    api.commit()
    response = api.get()
    assert response['Projects'][0]['name'] == 'UpdatedProject1'
    assert response['Projects'][0]['is_deleted'] == 1
    assert 'UpdatedProject1' not in [p['name'] for p in api.state['Projects']]

    project2.delete()
    api.commit()
    api.get()


def test_item(api_token):
    api = todoist.api.TodoistAPI(api_token)
    api.api_url = 'https://local.todoist.com/API/'
    api.sync_url = 'https://local.todoist.com/TodoistSync/v5.3/'
    api.get()

    cleanup(api)

    inbox = api.project_get_by_name('Inbox')
    item1 = api.item_add('Item1', inbox['id'])
    api.commit()
    response = api.get()
    assert response['Items'][0]['content'] == 'Item1'
    assert 'Item1' in [p['content'] for p in api.state['Items']]
    assert api.item_get_by_id(item1['id']) == item1
    assert api.item_get_by_content(item1['content']) == item1

    item1.complete()
    api.commit()
    response = api.get()
    assert response['Items'][0]['content'] == 'Item1'
    assert response['Items'][0]['checked'] == 1
    assert 'Item1' in [p['content'] for p in api.state['Items']]

    item1.uncomplete()
    api.commit()
    response = api.get()
    assert response['Items'][0]['content'] == 'Item1'
    assert response['Items'][0]['checked'] == 0
    assert 'Item1' in [p['content'] for p in api.state['Items']]

    project = api.project_add('Project1')
    api.commit()
    response = api.get()

    item1.move(project['id'])
    api.commit()
    response = api.get()
    assert response['Items'][0]['content'] == 'Item1'
    assert response['Items'][0]['project_id'] == project['id']

    item1.update(content='UpdatedItem1')
    api.commit()
    response = api.get()
    assert response['Items'][0]['content'] == 'UpdatedItem1'
    assert 'UpdatedItem1' in [p['content'] for p in api.state['Items']]
    assert api.item_get_by_id(item1['id']) == item1
    assert api.item_get_by_content(item1['content']) == item1

    item2 = api.item_add('Item2', inbox['id'])
    api.commit()
    api.get()

    api.item_uncomplete_update_meta(inbox['id'], {item1['id']: [0, 0, 1],
                                                  item2['id']: [0, 0, 2]})
    api.commit()
    response = api.get()
    for item in response['Items']:
        if item['id'] == item1['id']:
            assert item['item_order'] == 1
        if item['id'] == item2['id']:
            assert item['item_order'] == 2

    now = time.time()
    tomorrow = time.gmtime(now + 24*3600)
    new_date_utc = time.strftime("%Y-%m-%dT%H:%M", tomorrow)
    api.item_update_date_complete(item1['id'], new_date_utc, 'every day', 0)
    api.commit()
    response = api.get()
    assert response['Items'][0]['date_string'] == 'every day'

    api.item_update_orders_indents({item1['id']: [2, 2],
                                    item2['id']: [1, 3]})
    api.commit()
    response = api.get()
    for item in response['Items']:
        if item['id'] == item1['id']:
            assert item['item_order'] == 2
            assert item['indent'] == 2
        if item['id'] == item2['id']:
            assert item['item_order'] == 1
            assert item['indent'] == 3

    api.item_update_day_orders({item1['id']: 1, item2['id']: 2})
    api.commit()
    response = api.get()
    for item in response['Items']:
        if item['id'] == item1['id']:
            assert item['day_order'] == 1
        if item['id'] == item2['id']:
            assert item['day_order'] == 2

    item1.delete()
    api.commit()
    response = api.get()
    assert response['Items'][0]['content'] == 'UpdatedItem1'
    assert response['Items'][0]['is_deleted'] == 1
    assert 'UpdatedItem1' not in [p['content'] for p in api.state['Items']]

    project.delete()
    item2.delete()
    api.commit()
    api.get()


def test_label(api_token):
    api = todoist.api.TodoistAPI(api_token)
    api.api_url = 'https://local.todoist.com/API/'
    api.sync_url = 'https://local.todoist.com/TodoistSync/v5.3/'
    api.get()

    cleanup(api)

    label1 = api.label_register('Label1')
    api.commit()
    response = api.get()
    assert response['Labels'][0]['name'] == 'Label1'
    assert 'Label1' in [p['name'] for p in api.state['Labels']]
    assert api.label_get_by_id(label1['id']) == label1

    label1.update(name='UpdatedLabel1')
    api.commit()
    response = api.get()
    assert response['Labels'][0]['name'] == 'UpdatedLabel1'
    assert 'UpdatedLabel1' in [p['name'] for p in api.state['Labels']]
    assert api.label_get_by_id(label1['id']) == label1

    label1.delete()
    api.commit()
    response = api.get()
    assert response['Labels'][0]['name'] == 'UpdatedLabel1'
    assert response['Labels'][0]['is_deleted'] == 1
    assert 'UpdatedLabel1' not in [p['name'] for p in api.state['Labels']]


def test_note(api_token):
    api = todoist.api.TodoistAPI(api_token)
    api.api_url = 'https://local.todoist.com/API/'
    api.sync_url = 'https://local.todoist.com/TodoistSync/v5.3/'
    api.get()

    cleanup(api)

    inbox = api.project_get_by_name('Inbox')
    item = api.item_add('Item1', inbox['id'])
    api.commit()
    response = api.get()

    note1 = api.note_add(item['id'], 'Note1')
    api.commit()
    response = api.get()
    assert response['Notes'][0]['content'] == 'Note1'
    assert 'Note1' in [p['content'] for p in api.state['Notes']]
    assert api.note_get_by_id(note1['id']) == note1

    note1.update(content='UpdatedNote1')
    api.commit()
    response = api.get()
    assert response['Notes'][0]['content'] == 'UpdatedNote1'
    assert 'UpdatedNote1' in [p['content'] for p in api.state['Notes']]
    assert api.note_get_by_id(note1['id']) == note1

    note1.delete()
    api.commit()
    response = api.get()
    assert response['Notes'][0]['content'] == 'UpdatedNote1'
    assert response['Notes'][0]['is_deleted'] == 1
    assert 'UpdatedNote1' not in [p['content'] for p in api.state['Notes']]

    item.delete()
    api.commit()
    api.get()


def test_filter(api_token):
    api = todoist.api.TodoistAPI(api_token)
    api.api_url = 'https://local.todoist.com/API/'
    api.sync_url = 'https://local.todoist.com/TodoistSync/v5.3/'
    api.get()

    cleanup(api)

    filter1 = api.filter_add('Filter1', 'no due date')
    api.commit()
    response = api.get()
    assert response['Filters'][0]['name'] == 'Filter1'
    assert 'Filter1' in [p['name'] for p in api.state['Filters']]
    assert api.filter_get_by_id(filter1['id']) == filter1

    filter1.update(name='UpdatedFilter1')
    api.commit()
    response = api.get()
    assert response['Filters'][0]['name'] == 'UpdatedFilter1'
    assert 'UpdatedFilter1' in [p['name'] for p in api.state['Filters']]
    assert api.filter_get_by_id(filter1['id']) == filter1

    filter2 = api.filter_add('Filter2', 'today')
    api.commit()
    api.get()

    api.filter_update_orders({filter1['id']: 2, filter2['id']: 1})
    api.commit()
    response = api.get()
    for filter in response['Filters']:
        if filter['id'] == filter1['id']:
            assert filter['item_order'] == 2
        if filter['id'] == filter2['id']:
            assert filter['item_order'] == 1

    filter1.delete()
    api.commit()
    response = api.get()
    assert response['Filters'][0]['name'] == 'UpdatedFilter1'
    assert response['Filters'][0]['is_deleted'] == 1
    assert 'UpdatedFilter1' not in [p['name'] for p in api.state['Filters']]

    filter2.delete()
    api.commit()
    api.get()


def test_reminder(api_token):
    api = todoist.api.TodoistAPI(api_token)
    api.api_url = 'https://local.todoist.com/API/'
    api.sync_url = 'https://local.todoist.com/TodoistSync/v5.3/'
    api.get()

    cleanup(api)

    inbox = api.project_get_by_name('Inbox')
    item = api.item_add('Item1', inbox['id'], date_string='tomorrow')
    api.commit()
    api.get()

    # relative
    reminder = api.reminder_add(item['id'], minute_offset=30)
    api.commit()
    response = api.get()
    assert response['Reminders'][0]['minute_offset'] == 30
    assert reminder['id'] in [p['id'] for p in api.state['Reminders']]
    assert api.reminder_get_by_id(reminder['id']) == reminder

    reminder.update(minute_offset=str(15))
    api.commit()
    response = api.get()
    assert response['Reminders'][0]['minute_offset'] == 15
    assert reminder['id'] in [p['id'] for p in api.state['Reminders']]
    assert api.reminder_get_by_id(reminder['id']) == reminder

    reminder.delete()
    api.commit()
    response = api.get()
    assert response['Reminders'][0]['minute_offset'] == 15
    assert response['Reminders'][0]['is_deleted'] == 1
    assert reminder['id'] not in [p['id'] for p in api.state['Reminders']]

    # absolute
    now = time.time()
    tomorrow = time.gmtime(now + 24*3600)
    due_date_utc = time.strftime("%Y-%m-%dT%H:%M", tomorrow)
    due_date_utc_long = time.strftime("%a %d %b %Y %H:%M:00 +0000", tomorrow)
    reminder = api.reminder_add(item['id'], due_date_utc=due_date_utc)
    api.commit()
    response = api.get()
    tomorrow = time.gmtime(time.time() + 24*3600)
    assert response['Reminders'][0]['due_date_utc'] == due_date_utc_long
    assert reminder['id'] in [p['id'] for p in api.state['Reminders']]
    assert api.reminder_get_by_id(reminder['id']) == reminder

    tomorrow = time.gmtime(now + 24*3600 + 60)
    due_date_utc = time.strftime("%Y-%m-%dT%H:%M", tomorrow)
    due_date_utc_long = time.strftime("%a %d %b %Y %H:%M:00 +0000", tomorrow)
    reminder.update(due_date_utc=due_date_utc)
    api.commit()
    response = api.get()
    assert response['Reminders'][0]['due_date_utc'] == due_date_utc_long
    assert reminder['id'] in [p['id'] for p in api.state['Reminders']]
    assert api.reminder_get_by_id(reminder['id']) == reminder

    reminder.delete()
    api.commit()
    response = api.get()
    assert response['Reminders'][0]['due_date_utc'] == due_date_utc_long
    assert response['Reminders'][0]['is_deleted'] == 1
    assert reminder['id'] not in [p['id'] for p in api.state['Reminders']]

    item.delete()
    api.commit()
    api.get()


def test_live_notifications(api_token):
    api = todoist.api.TodoistAPI(api_token)
    api.api_url = 'https://local.todoist.com/API/'
    api.sync_url = 'https://local.todoist.com/TodoistSync/v5.3/'
    api.get()

    api.live_notifications_mark_as_read(api.state['LiveNotificationsLastRead'])
    api.commit()
    response = api.get()
    assert response['LiveNotificationsLastRead'] == \
        api.state['LiveNotificationsLastRead']


def test_share(api_token, api_token2):
    api = todoist.api.TodoistAPI(api_token)
    api.api_url = 'https://local.todoist.com/API/'
    api.sync_url = 'https://local.todoist.com/TodoistSync/v5.3/'
    api.get()

    cleanup(api)

    api2 = todoist.api.TodoistAPI(api_token2)
    api2.api_url = 'https://local.todoist.com/API/'
    api2.sync_url = 'https://local.todoist.com/TodoistSync/v5.3/'
    api2.get()

    cleanup(api2)

    # accept
    project1 = api.project_add('Project1')
    api.commit()
    api.get()

    api.share_project(project1['id'], api2['User']['email'])
    api.commit()
    response = api.get()
    assert response['Projects'][0]['name'] == project1['name']
    assert response['Projects'][0]['shared']

    response2 = api2.get()
    assert response2['LiveNotifications'][0]['project_name'] == \
        project1['name']
    assert response2['LiveNotifications'][0]['from_user']['email'] == \
        api['User']['email']
    invitation = response2['LiveNotifications'][0]

    api2.accept_invitation(invitation['invitation_id'],
                           invitation['invitation_secret'])
    api2.commit()
    response2 = api2.get()
    assert response2['LiveNotifications'][0]['invitation_id'] == \
        invitation['invitation_id']
    assert response2['LiveNotifications'][0]['state'] == 'accepted'
    assert response2['Projects'][0]['shared']
    assert api['User']['id'] in \
        [p['user_id'] for p in response2['CollaboratorStates']]
    assert api2['User']['id'] in \
        [p['user_id'] for p in response2['CollaboratorStates']]

    response = api.get()
    assert response['LiveNotifications'][0]['invitation_id'] == \
        invitation['invitation_id']
    assert response['LiveNotifications'][0]['notification_type'] == \
        'share_invitation_accepted'
    assert response['Projects'][0]['shared']

    # ownership
    project1 = api2.project_get_by_name('Project1')
    api2.take_ownership(project1['id'])
    api2.commit()
    api2.get()

    project1 = api.project_get_by_name('Project1')
    api.take_ownership(project1['id'])
    api.commit()
    api.get()

    api.delete_collaborator(project1['id'], api2['User']['email'])
    api.commit()
    api.get()

    api.project_get_by_name('Project1').delete()
    api.commit()
    api.get()

    # reject
    project2 = api.project_add('Project2')
    api.commit()
    api.get()

    api.share_project(project2['id'], api2['User']['email'])
    api.commit()
    response = api.get()
    assert response['Projects'][0]['name'] == project2['name']
    assert response['Projects'][0]['shared']

    response2 = api2.get()
    assert response2['LiveNotifications'][0]['project_name'] == \
        project2['name']
    assert response2['LiveNotifications'][0]['from_user']['email'] == \
        api['User']['email']
    invitation = response2['LiveNotifications'][0]

    api2.reject_invitation(invitation['invitation_id'],
                           invitation['invitation_secret'])
    api2.commit()
    response2 = api2.get()
    assert response2['LiveNotifications'][0]['invitation_id'] == \
        invitation['invitation_id']
    assert response2['LiveNotifications'][0]['state'] == 'rejected'
    assert len(response2['Projects']) == 0
    assert len(response2['CollaboratorStates']) == 0

    response = api.get()
    assert response['LiveNotifications'][0]['invitation_id'] == \
        invitation['invitation_id']
    assert response['LiveNotifications'][0]['notification_type'] == \
        'share_invitation_rejected'
    assert not response['Projects'][0]['shared']

    api.delete_invitation(invitation['invitation_id'])
    api.commit()
    api.get()

    api.project_get_by_name('Project2').delete()
    api.commit()
    api.get()
