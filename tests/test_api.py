import datetime
import io
import time

import todoist


def test_stats(api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    response = api.completed.get_stats()
    assert 'days_items' in response
    assert 'week_items' in response
    assert 'karma_trend' in response
    assert 'karma_last_update' in response


def test_user(api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()
    date_format = api.state['user']['date_format']
    date_format_new = 1 - date_format
    api.user.update(date_format=date_format_new)
    api.commit()
    assert date_format_new == api.state['user']['date_format']
    api.user.update_goals(vacation_mode=1)
    api.commit()
    api.user.update_goals(vacation_mode=0)
    api.commit()


def test_project(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)

    api.sync()

    project1 = api.projects.add('Project1')
    response = api.commit()
    assert response['projects'][0]['name'] == 'Project1'
    assert 'Project1' in [p['name'] for p in api.state['projects']]
    assert api.projects.get_by_id(project1['id']) == project1

    project1.archive()
    response = api.commit()
    assert response['projects'][0]['name'] == 'Project1'
    assert response['projects'][0]['is_archived'] == 1
    assert 'Project1' in [p['name'] for p in api.state['projects']]
    assert 1 in [
        p['is_archived'] for p in api.state['projects']
        if p['id'] == project1['id']
    ]

    project1.unarchive()
    response = api.commit()
    assert response['projects'][0]['name'] == 'Project1'
    assert response['projects'][0]['is_archived'] == 0
    assert 0 in [
        p['is_archived'] for p in api.state['projects']
        if p['id'] == project1['id']
    ]

    project1.update(name='UpdatedProject1')
    response = api.commit()
    assert response['projects'][0]['name'] == 'UpdatedProject1'
    assert 'UpdatedProject1' in [p['name'] for p in api.state['projects']]
    assert api.projects.get_by_id(project1['id']) == project1

    project2 = api.projects.add('Project2')
    response = api.commit()
    assert response['projects'][0]['name'] == 'Project2'
    api.projects.update_orders_indents({
        project1['id']: [1, 2],
        project2['id']: [2, 3]
    })
    response = api.commit()
    for project in response['projects']:
        if project['id'] == project1['id']:
            assert project['item_order'] == 1
            assert project['indent'] == 2
        if project['id'] == project2['id']:
            assert project['item_order'] == 2
            assert project['indent'] == 3
    assert 1 in [
        p['item_order'] for p in api.state['projects']
        if p['id'] == project1['id']
    ]
    assert 2 in [
        p['indent'] for p in api.state['projects'] if p['id'] == project1['id']
    ]
    assert 2 in [
        p['item_order'] for p in api.state['projects']
        if p['id'] == project2['id']
    ]
    assert 3 in [
        p['indent'] for p in api.state['projects'] if p['id'] == project2['id']
    ]

    project1.delete()
    response = api.commit()
    assert response['projects'][0]['id'] == project1['id']
    assert response['projects'][0]['is_deleted'] == 1
    assert 'UpdatedProject1' not in [p['name'] for p in api.state['projects']]

    api.projects.archive(project2['id'])
    response = api.commit()
    assert response['projects'][0]['name'] == 'Project2'
    assert response['projects'][0]['is_archived'] == 1
    assert 1 in [
        p['is_archived'] for p in api.state['projects']
        if p['id'] == project2['id']
    ]

    api.projects.unarchive(project2['id'])
    response = api.commit()
    assert response['projects'][0]['name'] == 'Project2'
    assert response['projects'][0]['is_archived'] == 0
    assert 0 in [
        p['is_archived'] for p in api.state['projects']
        if p['id'] == project2['id']
    ]

    api.projects.update(project2['id'], name='UpdatedProject2')
    response = api.commit()
    assert response['projects'][0]['name'] == 'UpdatedProject2'
    assert 'UpdatedProject2' in [p['name'] for p in api.state['projects']]

    api.projects.delete([project2['id']])
    response = api.commit()
    assert response['projects'][0]['id'] == project2['id']
    assert response['projects'][0]['is_deleted'] == 1
    assert 'UpdatedProject2' not in [p['name'] for p in api.state['projects']]


def test_item(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)

    api.sync()

    response = api.add_item('Item1')
    assert response['content'] == 'Item1'
    api.sync()
    assert 'Item1' in [i['content'] for i in api.state['items']]
    item1 = [i for i in api.state['items'] if i['content'] == 'Item1'][0]
    assert api.items.get_by_id(item1['id']) == item1
    item1.delete()
    response = api.commit()

    inbox = [p for p in api.state['projects'] if p['name'] == 'Inbox'][0]
    item1 = api.items.add('Item1', inbox['id'])
    response = api.commit()
    assert response['items'][0]['content'] == 'Item1'
    assert 'Item1' in [i['content'] for i in api.state['items']]
    assert api.items.get_by_id(item1['id']) == item1

    item1.complete()
    response = api.commit()
    assert response['items'][0]['content'] == 'Item1'
    assert response['items'][0]['checked'] == 1
    assert 1 in [
        i['checked'] for i in api.state['items'] if i['id'] == item1['id']
    ]

    item1.uncomplete()
    response = api.commit()
    assert response['items'][0]['content'] == 'Item1'
    assert response['items'][0]['checked'] == 0
    assert 0 in [
        i['checked'] for i in api.state['items'] if i['id'] == item1['id']
    ]

    project1 = api.projects.add('Project1')
    response = api.commit()

    item1.move(project1['id'])
    response = api.commit()
    assert response['items'][0]['content'] == 'Item1'
    assert response['items'][0]['project_id'] == project1['id']
    assert project1['id'] in [
        i['project_id'] for i in api.state['items'] if i['id'] == item1['id']
    ]

    item1.update(content='UpdatedItem1')
    response = api.commit()
    assert response['items'][0]['content'] == 'UpdatedItem1'
    assert 'UpdatedItem1' in [i['content'] for i in api.state['items']]
    assert api.items.get_by_id(item1['id']) == item1

    date_string = datetime.datetime(2038, 1, 19, 3, 14, 7)
    item2 = api.items.add('Item2', inbox['id'], date_string=date_string)
    api.commit()

    now = time.time()
    tomorrow = time.gmtime(now + 24 * 3600)
    new_date_utc = time.strftime("%Y-%m-%dT%H:%M", tomorrow)
    api.items.update_date_complete(item1['id'], new_date_utc, 'every day', 0)
    response = api.commit()
    assert response['items'][0]['date_string'] == 'every day'
    assert 'every day' in [
        i['date_string'] for i in api.state['items'] if i['id'] == item1['id']
    ]

    api.items.update_orders_indents({item1['id']: [2, 2], item2['id']: [1, 3]})
    response = api.commit()
    for item in response['items']:
        if item['id'] == item1['id']:
            assert item['item_order'] == 2
            assert item['indent'] == 2
        if item['id'] == item2['id']:
            assert item['item_order'] == 1
            assert item['indent'] == 3
    assert 2 in [
        i['item_order'] for i in api.state['items'] if i['id'] == item1['id']
    ]
    assert 2 in [
        i['indent'] for i in api.state['items'] if i['id'] == item1['id']
    ]
    assert 1 in [
        i['item_order'] for i in api.state['items'] if i['id'] == item2['id']
    ]
    assert 3 in [
        i['indent'] for i in api.state['items'] if i['id'] == item2['id']
    ]

    api.items.update_day_orders({item1['id']: 1, item2['id']: 2})
    response = api.commit()
    for item in response['items']:
        if item['id'] == item1['id']:
            assert item['day_order'] == 1
        if item['id'] == item2['id']:
            assert item['day_order'] == 2
    assert 1 == api.state['day_orders'][str(item1['id'])]
    assert 2 == api.state['day_orders'][str(item2['id'])]

    item1.delete()
    response = api.commit()
    assert response['items'][0]['id'] == item1['id']
    assert response['items'][0]['is_deleted'] == 1
    assert 'UpdatedItem1' not in [i['content'] for i in api.state['items']]

    api.items.complete([item2['id']])
    response = api.commit()
    assert response['items'][0]['content'] == 'Item2'
    assert response['items'][0]['checked'] == 1
    assert 1 in [
        i['checked'] for i in api.state['items'] if i['id'] == item2['id']
    ]

    api.items.uncomplete([item2['id']])
    response = api.commit()
    assert response['items'][0]['content'] == 'Item2'
    assert response['items'][0]['checked'] == 0
    assert 0 in [
        i['checked'] for i in api.state['items'] if i['id'] == item2['id']
    ]

    api.items.move({item2['project_id']: [item2['id']]}, project1['id'])
    response = api.commit()
    assert response['items'][0]['content'] == 'Item2'
    assert response['items'][0]['project_id'] == project1['id']
    assert project1['id'] in [
        i['project_id'] for i in api.state['items'] if i['id'] == item2['id']
    ]

    api.items.update(item2['id'], content='UpdatedItem2')
    response = api.commit()
    assert response['items'][0]['content'] == 'UpdatedItem2'
    assert 'UpdatedItem2' in [i['content'] for i in api.state['items']]

    api.items.delete([item2['id']])
    response = api.commit()
    assert response['items'][0]['id'] == item2['id']
    assert response['items'][0]['is_deleted'] == 1
    assert 'UpdatedItem2' not in [i['content'] for i in api.state['items']]

    project1.delete()
    response = api.commit()


def test_label(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)

    api.sync()

    label1 = api.labels.add('Label1')
    response = api.commit()
    assert response['labels'][0]['name'] == 'Label1'
    assert 'Label1' in [l['name'] for l in api.state['labels']]
    assert api.labels.get_by_id(label1['id']) == label1

    label1.update(name='UpdatedLabel1')
    response = api.commit()
    assert response['labels'][0]['name'] == 'UpdatedLabel1'
    assert 'UpdatedLabel1' in [l['name'] for l in api.state['labels']]
    assert api.labels.get_by_id(label1['id']) == label1

    label2 = api.labels.add('Label2')
    response = api.commit()

    api.labels.update_orders({label1['id']: 1, label2['id']: 2})
    response = api.commit()
    for label in response['labels']:
        if label['id'] == label1['id']:
            assert label['item_order'] == 1
        if label['id'] == label2['id']:
            assert label['item_order'] == 2
    assert 1 in [
        l['item_order'] for l in api.state['labels'] if l['id'] == label1['id']
    ]
    assert 2 in [
        l['item_order'] for l in api.state['labels'] if l['id'] == label2['id']
    ]

    label1.delete()
    response = api.commit()
    assert response['labels'][0]['id'] == label1['id']
    assert response['labels'][0]['is_deleted'] == 1
    assert 'UpdatedLabel1' not in [l['name'] for l in api.state['labels']]

    api.labels.update(label2['id'], name='UpdatedLabel2')
    response = api.commit()
    assert response['labels'][0]['name'] == 'UpdatedLabel2'
    assert 'UpdatedLabel2' in [l['name'] for l in api.state['labels']]

    api.labels.delete(label2['id'])
    response = api.commit()
    assert response['labels'][0]['id'] == label2['id']
    assert response['labels'][0]['is_deleted'] == 1
    assert 'UpdatedLabel1' not in [l['name'] for l in api.state['labels']]


def test_note(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)

    api.sync()

    inbox = [p for p in api.state['projects'] if p['name'] == 'Inbox'][0]
    item1 = api.items.add('Item1', inbox['id'])
    api.commit()

    note1 = api.notes.add(item1['id'], 'Note1')
    response = api.commit()
    assert response['notes'][0]['content'] == 'Note1'
    assert 'Note1' in [n['content'] for n in api.state['notes']]
    assert api.notes.get_by_id(note1['id']) == note1

    note1.update(content='UpdatedNote1')
    response = api.commit()
    assert response['notes'][0]['content'] == 'UpdatedNote1'
    assert 'UpdatedNote1' in [n['content'] for n in api.state['notes']]
    assert api.notes.get_by_id(note1['id']) == note1

    note1.delete()
    response = api.commit()
    assert response['notes'][0]['id'] == note1['id']
    assert response['notes'][0]['is_deleted'] == 1
    assert 'UpdatedNote1' not in [n['content'] for n in api.state['notes']]

    note2 = api.notes.add(item1['id'], 'Note2')
    response = api.commit()
    assert response['notes'][0]['content'] == 'Note2'
    assert 'Note2' in [n['content'] for n in api.state['notes']]

    api.notes.update(note2['id'], content='UpdatedNote2')
    response = api.commit()
    assert response['notes'][0]['content'] == 'UpdatedNote2'
    assert 'UpdatedNote2' in [n['content'] for n in api.state['notes']]

    api.notes.delete(note2['id'])
    response = api.commit()
    assert response['notes'][0]['id'] == note2['id']
    assert response['notes'][0]['is_deleted'] == 1
    assert 'UpdatedNote2' not in [n['content'] for n in api.state['notes']]

    item1.delete()
    response = api.commit()


def test_projectnote(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)

    api.sync()

    project1 = api.projects.add('Project1')
    api.commit()

    note1 = api.project_notes.add(project1['id'], 'Note1')
    response = api.commit()
    assert response['project_notes'][0]['content'] == 'Note1'
    assert 'Note1' in [n['content'] for n in api.state['project_notes']]
    assert api.project_notes.get_by_id(note1['id']) == note1

    note1.update(content='UpdatedNote1')
    response = api.commit()
    assert response['project_notes'][0]['content'] == 'UpdatedNote1'
    assert 'UpdatedNote1' in [n['content'] for n in api.state['project_notes']]
    assert api.project_notes.get_by_id(note1['id']) == note1

    note1.delete()
    response = api.commit()
    assert response['project_notes'][0]['id'] == note1['id']
    assert response['project_notes'][0]['is_deleted'] == 1
    assert 'UpdatedNote1' not in [
        n['content'] for n in api.state['project_notes']
    ]

    note2 = api.project_notes.add(project1['id'], 'Note2')
    response = api.commit()
    assert response['project_notes'][0]['content'] == 'Note2'
    assert 'Note2' in [n['content'] for n in api.state['project_notes']]

    api.project_notes.update(note2['id'], content='UpdatedNote2')
    response = api.commit()
    assert response['project_notes'][0]['content'] == 'UpdatedNote2'
    assert 'UpdatedNote2' in [n['content'] for n in api.state['project_notes']]

    api.project_notes.delete(note2['id'])
    response = api.commit()
    assert response['project_notes'][0]['id'] == note2['id']
    assert response['project_notes'][0]['is_deleted'] == 1
    assert 'UpdatedNote2' not in [
        n['content'] for n in api.state['project_notes']
    ]

    project1.delete()
    response = api.commit()


def test_filter(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)

    api.sync()

    filter1 = api.filters.add('Filter1', 'no due date')
    response = api.commit()
    assert response['filters'][0]['name'] == 'Filter1'
    assert 'Filter1' in [f['name'] for f in api.state['filters']]
    assert api.filters.get_by_id(filter1['id']) == filter1

    filter1.update(name='UpdatedFilter1')
    response = api.commit()
    assert response['filters'][0]['name'] == 'UpdatedFilter1'
    assert 'UpdatedFilter1' in [f['name'] for f in api.state['filters']]
    assert api.filters.get_by_id(filter1['id']) == filter1

    filter2 = api.filters.add('Filter2', 'today')
    response = api.commit()

    api.filters.update_orders({filter1['id']: 2, filter2['id']: 1})
    response = api.commit()
    for filter in response['filters']:
        if filter['id'] == filter1['id']:
            assert filter['item_order'] == 2
        if filter['id'] == filter2['id']:
            assert filter['item_order'] == 1
    assert 2 in [
        f['item_order'] for f in api.state['filters']
        if f['id'] == filter1['id']
    ]
    assert 1 in [
        f['item_order'] for f in api.state['filters']
        if f['id'] == filter2['id']
    ]

    filter1.delete()
    response = api.commit()
    assert response['filters'][0]['id'] == filter1['id']
    assert response['filters'][0]['is_deleted'] == 1
    assert 'UpdatedFilter1' not in [p['name'] for p in api.state['filters']]

    api.filters.update(filter2['id'], name='UpdatedFilter2')
    response = api.commit()
    assert response['filters'][0]['name'] == 'UpdatedFilter2'
    assert 'UpdatedFilter2' in [f['name'] for f in api.state['filters']]

    api.filters.delete(filter2['id'])
    response = api.commit()
    assert response['filters'][0]['id'] == filter2['id']
    assert response['filters'][0]['is_deleted'] == 1
    assert 'UpdatedFilter2' not in [f['name'] for f in api.state['filters']]


def test_reminder(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)

    api.sync()

    inbox = [p for p in api.state['projects'] if p['name'] == 'Inbox'][0]
    item1 = api.items.add('Item1', inbox['id'], date_string='tomorrow 5pm')
    api.commit()

    # relative
    reminder1 = api.reminders.add(item1['id'], minute_offset=30)
    response = api.commit()
    assert response['reminders'][0]['minute_offset'] == 30
    assert reminder1['id'] in [p['id'] for p in api.state['reminders']]
    assert api.reminders.get_by_id(reminder1['id']) == reminder1

    reminder1.update(minute_offset=str(15))
    response = api.commit()
    assert response['reminders'][0]['minute_offset'] == 15
    assert reminder1['id'] in [p['id'] for p in api.state['reminders']]
    assert api.reminders.get_by_id(reminder1['id']) == reminder1

    reminder1.delete()
    response = api.commit()
    assert response['reminders'][0]['is_deleted'] == 1
    assert reminder1['id'] not in [p['id'] for p in api.state['reminders']]

    # absolute
    now = time.time()
    tomorrow = time.gmtime(now + 24 * 3600)
    due_date_utc = time.strftime("%Y-%m-%dT%H:%M", tomorrow)
    due_date_utc_long = time.strftime("%a %d %b %Y %H:%M:00 +0000", tomorrow)
    reminder2 = api.reminders.add(item1['id'], due_date_utc=due_date_utc)
    response = api.commit()
    assert response['reminders'][0]['due_date_utc'] == due_date_utc_long
    tomorrow = time.gmtime(time.time() + 24 * 3600)
    assert reminder2['id'] in [p['id'] for p in api.state['reminders']]
    assert api.reminders.get_by_id(reminder2['id']) == reminder2

    tomorrow = time.gmtime(now + 24 * 3600 + 60)
    due_date_utc = time.strftime("%Y-%m-%dT%H:%M", tomorrow)
    due_date_utc_long = time.strftime("%a %d %b %Y %H:%M:00 +0000", tomorrow)
    api.reminders.update(reminder2['id'], due_date_utc=due_date_utc)
    response = api.commit()
    assert response['reminders'][0]['due_date_utc'] == due_date_utc_long
    assert reminder2['id'] in [p['id'] for p in api.state['reminders']]
    assert api.reminders.get_by_id(reminder2['id']) == reminder2

    api.reminders.delete(reminder2['id'])
    response = api.commit()
    assert response['reminders'][0]['is_deleted'] == 1
    assert reminder2['id'] not in [p['id'] for p in api.state['reminders']]

    item1.delete()
    response = api.commit()


def test_locations(api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)

    api.sync()

    api.locations.clear()
    api.commit()

    assert api.state['locations'] == []


def test_live_notifications(api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)

    api.sync()

    api.live_notifications.set_last_read(
        api.state['live_notifications_last_read_id'])
    response = api.commit()
    assert response['live_notifications_last_read_id'] == \
        api.state['live_notifications_last_read_id']


def test_share(cleanup, cleanup2, api_endpoint, api_token, api_token2):

    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api2 = todoist.api.TodoistAPI(api_token2, api_endpoint)

    api.user.update(auto_invite_disabled=1)
    api.commit()
    api.sync()

    api2.user.update(auto_invite_disabled=1)
    api2.commit()
    api2.sync()

    # accept
    project1 = api.projects.add('Project1')
    api.commit()

    api.projects.share(project1['id'], api2.state['user']['email'])
    response = api.commit()
    assert response['projects'][0]['name'] == project1['name']
    assert response['projects'][0]['shared']

    response2 = api2.sync()
    invitation1 = next((ln for ln in response2['live_notifications']
                        if ln['notification_type'] == 'share_invitation_sent'),
                       None)
    assert invitation1 is not None
    assert invitation1['project_name'] == project1['name']
    assert invitation1['from_user']['email'] == api.state['user']['email']

    api2.invitations.accept(invitation1['id'],
                            invitation1['invitation_secret'])
    response2 = api2.commit()
    assert api2.state['user']['id'] in \
        [p['user_id'] for p in api2.state['collaborator_states']]

    # reject
    project2 = api.projects.add('Project2')
    api.commit()

    api.projects.share(project2['id'], api2.state['user']['email'])
    response = api.commit()
    assert response['projects'][0]['name'] == project2['name']
    assert response['projects'][0]['shared']

    response2 = api2.sync()
    invitation2 = next((ln for ln in response2['live_notifications']
                        if ln['notification_type'] == 'share_invitation_sent'),
                       None)
    assert invitation2 is not None
    assert invitation2['project_name'] == project2['name']
    assert invitation2['from_user']['email'] == api.state['user']['email']

    api2.invitations.reject(invitation2['id'],
                            invitation2['invitation_secret'])
    response2 = api2.commit()
    assert len(response2['projects']) == 0
    assert len(response2['collaborator_states']) == 0

    project2 = [p for p in api.state['projects'] if p['name'] == 'Project2'][0]
    project2.delete()
    api.commit()

    # delete
    project3 = api.projects.add('Project3')
    api.commit()

    api.projects.share(project3['id'], api2.state['user']['email'])
    response = api.commit()
    assert response['projects'][0]['name'] == project3['name']
    assert response['projects'][0]['shared']

    response2 = api2.sync()
    invitation3 = next((ln for ln in response2['live_notifications']
                        if ln['notification_type'] == 'share_invitation_sent'),
                       None)
    assert invitation3 is not None
    assert invitation3['project_name'] == project3['name']
    assert invitation3['from_user']['email'] == api.state['user']['email']

    api.invitations.delete(invitation3['id'])
    api.commit()

    project3 = [p for p in api.state['projects'] if p['name'] == 'Project3'][0]
    project3.delete()
    api.commit()


def test_templates(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)

    api.sync()

    project1 = api.projects.add('Project1')
    project2 = api.projects.add('Project2')
    api.commit()

    item1 = api.items.add('Item1', project1['id'])
    api.commit()

    template = api.templates.export_as_file(project1['id'])
    assert 'task,Item1,4,1' in template
    with io.open('/tmp/example.csv', 'w', encoding='utf-8') as example:
        example.write(template)

    result = api.templates.import_into_project(project1['id'],
                                               '/tmp/example.csv')
    assert result == {'status': u'ok'}

    item1.delete()
    project1.delete()
    project2.delete()
    api.commit()
