import io
import time

import todoist


def test_stats_get(api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    response = api.completed.get_stats()
    assert "days_items" in response
    assert "week_items" in response
    assert "karma_trend" in response
    assert "karma_last_update" in response


def test_user_update(api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()
    date_format = api.state["user"]["date_format"]
    date_format_new = 1 - date_format
    api.user.update(date_format=date_format_new)
    api.commit()
    assert date_format_new == api.state["user"]["date_format"]
    api.user.update_goals(vacation_mode=1)
    api.commit()
    api.user.update_goals(vacation_mode=0)
    api.commit()


def test_user_settings_update(api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()
    reminder_email = api.state["user_settings"]["reminder_email"]
    if reminder_email:
        reminder_email = False
    else:
        reminder_email = True
    api.user_settings.update(reminder_email=reminder_email)
    api.commit()
    assert reminder_email == api.state["user_settings"]["reminder_email"]


def test_project_add(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    project1 = api.projects.add("Project1")
    response = api.commit()
    assert response["projects"][0]["name"] == "Project1"
    assert "Project1" in [p["name"] for p in api.state["projects"]]
    assert api.projects.get_by_id(project1["id"]) == project1

    assert api.projects.get(project1["id"])["project"]["name"] == project1["name"]

    project1.delete()
    api.commit()


def test_project_delete(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    project1 = api.projects.add("Project1")
    api.commit()

    project1.delete()
    response = api.commit()
    assert response["projects"][0]["id"] == project1["id"]
    assert response["projects"][0]["is_deleted"] == 1
    assert "Project1" not in [p["name"] for p in api.state["projects"]]


def test_project_update(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    project1 = api.projects.add("Project1")
    api.commit()

    project1.update(name="UpdatedProject1")
    response = api.commit()
    assert response["projects"][0]["name"] == "UpdatedProject1"
    assert "UpdatedProject1" in [p["name"] for p in api.state["projects"]]
    assert api.projects.get_by_id(project1["id"]) == project1

    project1.delete()
    api.commit()


def test_project_archive(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    project1 = api.projects.add("Project1")
    api.commit()

    project1.archive()
    response = api.commit()
    assert response["projects"][0]["name"] == "Project1"
    assert response["projects"][0]["is_archived"] == 1
    assert "Project1" in [p["name"] for p in api.state["projects"]]
    assert 1 in [
        p["is_archived"] for p in api.state["projects"] if p["id"] == project1["id"]
    ]

    project1.delete()
    api.commit()


def test_project_unarchive(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    project1 = api.projects.add("Project1")
    api.commit()

    project1.archive()
    api.commit()

    project1.unarchive()
    response = api.commit()
    assert response["projects"][0]["name"] == "Project1"
    assert response["projects"][0]["is_archived"] == 0
    assert 0 in [
        p["is_archived"] for p in api.state["projects"] if p["id"] == project1["id"]
    ]

    project1.delete()
    api.commit()


def test_project_move_to_parent(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    project1 = api.projects.add("Project1")
    api.commit()

    project2 = api.projects.add("Project2")
    api.commit()

    project2.move(project1["id"])
    response = api.commit()
    assert response["projects"][0]["name"] == "Project2"
    assert response["projects"][0]["parent_id"] == project1["id"]
    assert project1["id"] in [
        i["parent_id"] for i in api.state["projects"] if i["id"] == project2["id"]
    ]

    project2.delete()
    api.commit()
    project1.delete()
    api.commit()


def test_project_reorder(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    project1 = api.projects.add("Project1")
    api.commit()

    project2 = api.projects.add("Project2")
    api.commit()

    api.projects.reorder(
        projects=[
            {"id": project1["id"], "child_order": 2},
            {"id": project2["id"], "child_order": 1},
        ]
    )
    response = api.commit()
    for project in response["projects"]:
        if project["id"] == project1["id"]:
            assert project["child_order"] == 2
        if project["id"] == project2["id"]:
            assert project["child_order"] == 1
    assert 2 in [
        p["child_order"] for p in api.state["projects"] if p["id"] == project1["id"]
    ]
    assert 1 in [
        p["child_order"] for p in api.state["projects"] if p["id"] == project2["id"]
    ]

    project1.delete()
    api.commit()
    project2.delete()
    api.commit()


def test_item_add(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    response = api.add_item("Item1")
    assert response["content"] == "Item1"
    api.sync()
    assert "Item1" in [i["content"] for i in api.state["items"]]
    item1 = [i for i in api.state["items"] if i["content"] == "Item1"][0]
    assert api.items.get_by_id(item1["id"]) == item1

    assert api.items.get(item1["id"])["item"]["content"] == item1["content"]

    item1.delete()
    api.commit()


def test_item_delete(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    item1 = api.items.add("Item1")
    api.sync()

    item1.delete()
    response = api.commit()
    assert response["items"][0]["id"] == item1["id"]
    assert response["items"][0]["is_deleted"] == 1
    assert "Item1" not in [i["content"] for i in api.state["items"]]


def test_item_update(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    item1 = api.items.add("Item1")
    api.commit()

    item1.update(content="UpdatedItem1")
    response = api.commit()
    assert response["items"][0]["content"] == "UpdatedItem1"
    assert "UpdatedItem1" in [i["content"] for i in api.state["items"]]
    assert api.items.get_by_id(item1["id"]) == item1

    item1.delete()
    api.commit()


def test_item_complete(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    item1 = api.items.add("Item1")
    api.commit()
    item2 = api.items.add("Item2", parent_id=item1["id"])
    api.commit()

    item2.complete()
    response = api.commit()
    assert response["items"][0]["content"] == "Item2"
    assert response["items"][0]["checked"] == 1
    assert 1 in [i["checked"] for i in api.state["items"] if i["id"] == item2["id"]]

    item1.delete()
    api.commit()
    item2.delete()
    api.commit()


def test_item_uncomplete(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    item1 = api.items.add("Item1")
    api.commit()
    item2 = api.items.add("Item2", parent_id=item1["id"])
    api.commit()
    item2.complete()
    api.commit()

    item2.uncomplete()
    response = api.commit()
    assert response["items"][0]["content"] == "Item2"
    assert response["items"][0]["checked"] == 0
    assert 0 in [i["checked"] for i in api.state["items"] if i["id"] == item1["id"]]

    item1.delete()
    api.commit()
    item2.delete()
    api.commit()


def test_item_archive(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    item1 = api.items.add("Item1")
    api.commit()
    item2 = api.items.add("Item2", parent_id=item1["id"])
    api.commit()
    item2.complete()
    api.commit()

    item2.archive()
    response = api.commit()
    assert response["items"][0]["content"] == "Item2"
    assert response["items"][0]["in_history"] == 1
    assert 1 in [i["in_history"] for i in api.state["items"] if i["id"] == item2["id"]]

    item1.delete()
    api.commit()
    item2.delete()
    api.commit()


def test_item_unarchive(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    item1 = api.items.add("Item1")
    api.commit()
    item2 = api.items.add("Item2", parent_id=item1["id"])
    api.commit()
    item2.complete()
    api.commit()
    item2.archive()
    api.commit()

    item2.unarchive()
    response = api.commit()
    assert response["items"][0]["content"] == "Item2"
    assert response["items"][0]["in_history"] == 0
    assert 0 in [i["in_history"] for i in api.state["items"] if i["id"] == item2["id"]]

    item1.delete()
    api.commit()
    item2.delete()
    api.commit()


def test_item_move_to_project(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    item1 = api.items.add("Item1")
    api.commit()
    project1 = api.projects.add("Project1")
    api.commit()

    item1.move(project_id=project1["id"])
    response = api.commit()
    assert response["items"][0]["content"] == "Item1"
    assert response["items"][0]["project_id"] == project1["id"]
    assert project1["id"] in [
        i["project_id"] for i in api.state["items"] if i["id"] == item1["id"]
    ]

    item1.delete()
    api.commit()
    project1.delete()
    api.commit()


def test_item_move_to_section(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    item1 = api.items.add("Item1")
    api.commit()
    section1 = api.sections.add("Section1", api.state["user"]["inbox_project"])
    api.commit()

    item1.move(section_id=section1["id"])
    response = api.commit()
    assert response["items"][0]["content"] == "Item1"
    assert response["items"][0]["section_id"] == section1["id"]
    assert section1["id"] in [
        i["section_id"] for i in api.state["items"] if i["id"] == item1["id"]
    ]

    item1.delete()
    api.commit()
    section1.delete()
    api.commit()


def test_item_move_to_parent(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    item1 = api.items.add("Item1")
    api.commit()
    item2 = api.items.add("Item2")
    api.commit()

    item2.move(parent_id=item1["id"])
    response = api.commit()
    assert response["items"][0]["content"] == "Item2"
    assert response["items"][0]["parent_id"] == item1["id"]
    assert item1["id"] in [
        i["parent_id"] for i in api.state["items"] if i["id"] == item2["id"]
    ]

    item1.delete()
    api.commit()
    item2.delete()
    api.commit()


def test_item_update_date_complete(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    item1 = api.items.add("Item1", due={"string": "every day"})
    api.commit()

    now = time.time()
    tomorrow = time.gmtime(now + 24 * 3600)
    new_date_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", tomorrow)
    due = {
        "date": new_date_utc,
        "string": "every day",
    }
    api.items.update_date_complete(item1["id"], due=due)
    response = api.commit()
    assert response["items"][0]["due"]["string"] == "every day"
    assert "every day" in [
        i["due"]["string"] for i in api.state["items"] if i["id"] == item1["id"]
    ]

    item1.delete()
    api.commit()


def test_item_reorder(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    item1 = api.items.add("Item1")
    api.commit()
    item2 = api.items.add("Item2")
    api.commit()

    api.items.reorder(
        items=[
            {"id": item1["id"], "child_order": 2},
            {"id": item2["id"], "child_order": 1},
        ]
    )
    response = api.commit()
    for item in response["items"]:
        if item["id"] == item1["id"]:
            assert item["child_order"] == 2
        if item["id"] == item2["id"]:
            assert item["child_order"] == 1
    assert 2 in [p["child_order"] for p in api.state["items"] if p["id"] == item1["id"]]
    assert 1 in [p["child_order"] for p in api.state["items"] if p["id"] == item2["id"]]

    item1.delete()
    api.commit()
    item2.delete()
    api.commit()


def test_item_update_day_orders(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    item1 = api.items.add("Item1")
    api.commit()
    item2 = api.items.add("Item2")
    api.commit()

    api.items.update_day_orders({item1["id"]: 1, item2["id"]: 2})
    response = api.commit()
    for item in response["items"]:
        if item["id"] == item1["id"]:
            assert item["day_order"] == 1
        if item["id"] == item2["id"]:
            assert item["day_order"] == 2
    assert 1 == api.state["day_orders"][str(item1["id"])]
    assert 2 == api.state["day_orders"][str(item2["id"])]

    item1.delete()
    api.commit()

    item2.delete()
    api.commit()


def test_label_add(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    label1 = api.labels.add("Label1")
    response = api.commit()
    assert response["labels"][0]["name"] == "Label1"
    assert "Label1" in [l["name"] for l in api.state["labels"]]
    assert api.labels.get_by_id(label1["id"]) == label1

    assert api.labels.get(label1["id"])["label"]["name"] == label1["name"]

    label1.delete()
    api.commit()


def test_label_delete(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    label1 = api.labels.add("Label1")
    api.commit()

    label1.delete()
    response = api.commit()
    assert response["labels"][0]["id"] == label1["id"]
    assert response["labels"][0]["is_deleted"] == 1
    assert "UpdatedLabel1" not in [l["name"] for l in api.state["labels"]]


def test_label_update(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    label1 = api.labels.add("Label1")
    api.commit()

    label1.update(name="UpdatedLabel1")
    response = api.commit()
    assert response["labels"][0]["name"] == "UpdatedLabel1"
    assert "UpdatedLabel1" in [l["name"] for l in api.state["labels"]]
    assert api.labels.get_by_id(label1["id"]) == label1

    label1.delete()
    api.commit()


def test_label_update_orders(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    label1 = api.labels.add("Label1")
    api.commit()
    label2 = api.labels.add("Label2")
    api.commit()

    api.labels.update_orders({label1["id"]: 1, label2["id"]: 2})
    response = api.commit()
    for label in response["labels"]:
        if label["id"] == label1["id"]:
            assert label["item_order"] == 1
        if label["id"] == label2["id"]:
            assert label["item_order"] == 2
    assert 1 in [
        l["item_order"] for l in api.state["labels"] if l["id"] == label1["id"]
    ]
    assert 2 in [
        l["item_order"] for l in api.state["labels"] if l["id"] == label2["id"]
    ]

    label1.delete()
    api.commit()
    label2.delete()
    api.commit()


def test_note_add(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    item1 = api.items.add("Item1")
    api.commit()

    note1 = api.notes.add(item1["id"], "Note1")
    response = api.commit()
    assert response["notes"][0]["content"] == "Note1"
    assert "Note1" in [n["content"] for n in api.state["notes"]]
    assert api.notes.get_by_id(note1["id"]) == note1

    assert api.notes.get(note1["id"])["note"]["content"] == note1["content"]

    note1.delete()
    api.commit()
    item1.delete()
    api.commit()


def test_note_delete(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    item1 = api.items.add("Item1")
    api.commit()
    note1 = api.notes.add(item1["id"], "Note1")
    api.commit()

    note1.delete()
    response = api.commit()
    assert response["notes"][0]["id"] == note1["id"]
    assert response["notes"][0]["is_deleted"] == 1
    assert "UpdatedNote1" not in [n["content"] for n in api.state["notes"]]

    note1.delete()
    api.commit()
    item1.delete()
    api.commit()


def test_note_update(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    item1 = api.items.add("Item1")
    api.commit()
    note1 = api.notes.add(item1["id"], "Note1")
    api.commit()

    note1.update(content="UpdatedNote1")
    response = api.commit()
    assert response["notes"][0]["content"] == "UpdatedNote1"
    assert "UpdatedNote1" in [n["content"] for n in api.state["notes"]]
    assert api.notes.get_by_id(note1["id"]) == note1

    note1.delete()
    api.commit()
    item1.delete()
    api.commit()


def test_projectnote_add(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    project1 = api.projects.add("Project1")
    api.commit()

    note1 = api.project_notes.add(project1["id"], "Note1")
    response = api.commit()
    assert response["project_notes"][0]["content"] == "Note1"
    assert "Note1" in [n["content"] for n in api.state["project_notes"]]
    assert api.project_notes.get_by_id(note1["id"]) == note1

    assert api.project_notes.get(note1["id"])["note"]["content"] == note1["content"]

    note1.delete()
    api.commit()
    project1.delete()
    api.commit()


def test_projectnote_delete(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    project1 = api.projects.add("Project1")
    api.commit()
    note1 = api.project_notes.add(project1["id"], "Note1")
    api.commit()

    note1.delete()
    response = api.commit()
    assert response["project_notes"][0]["id"] == note1["id"]
    assert response["project_notes"][0]["is_deleted"] == 1
    assert "UpdatedNote1" not in [n["content"] for n in api.state["project_notes"]]

    project1.delete()
    api.commit()


def test_projectnote_update(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    project1 = api.projects.add("Project1")
    api.commit()
    note1 = api.project_notes.add(project1["id"], "Note1")
    api.commit()

    note1.update(content="UpdatedNote1")
    response = api.commit()
    assert response["project_notes"][0]["content"] == "UpdatedNote1"
    assert "UpdatedNote1" in [n["content"] for n in api.state["project_notes"]]
    assert api.project_notes.get_by_id(note1["id"]) == note1

    note1.delete()
    api.commit()
    project1.delete()
    api.commit()


def test_section_add(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    response = api.sections.add("Section1", api.state["user"]["inbox_project"])
    assert response["name"] == "Section1"
    api.commit()
    assert "Section1" in [i["name"] for i in api.state["sections"]]
    section1 = [i for i in api.state["sections"] if i["name"] == "Section1"][0]
    assert api.sections.get_by_id(section1["id"]) == section1

    assert api.sections.get(section1["id"])["section"]["name"] == section1["name"]

    section1.delete()
    api.commit()


def test_section_delete(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    section1 = api.sections.add("Section1", api.state["user"]["inbox_project"])
    api.commit()

    section1.delete()
    response = api.commit()
    assert response["sections"][0]["id"] == section1["id"]
    assert response["sections"][0]["is_deleted"] == 1
    assert "Section1" not in [i["name"] for i in api.state["sections"]]


def test_section_update(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    section1 = api.sections.add("Section1", api.state["user"]["inbox_project"])
    api.commit()

    section1.update(name="UpdatedSection1")
    response = api.commit()
    assert response["sections"][0]["name"] == "UpdatedSection1"
    assert "UpdatedSection1" in [i["name"] for i in api.state["sections"]]
    assert api.sections.get_by_id(section1["id"]) == section1

    section1.delete()
    api.commit()


def test_section_archive(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    section1 = api.sections.add("Section1", api.state["user"]["inbox_project"])
    api.commit()

    section1.archive()
    response = api.commit()
    assert response["sections"][0]["name"] == "Section1"
    assert response["sections"][0]["is_archived"] == 1

    section1.delete()
    api.commit()


def test_section_unarchive(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    section1 = api.sections.add("Section1", api.state["user"]["inbox_project"])
    api.commit()

    section1.unarchive()
    response = api.commit()
    assert response["sections"][0]["name"] == "Section1"
    assert response["sections"][0]["is_archived"] == 0

    section1.delete()
    api.commit()


def test_section_move_to_project(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    section1 = api.sections.add("Section1", api.state["user"]["inbox_project"])
    api.commit()
    project1 = api.projects.add("Project1")
    api.commit()

    section1.move(project_id=project1["id"])
    response = api.commit()
    assert response["sections"][0]["name"] == "Section1"
    assert response["sections"][0]["project_id"] == project1["id"]
    assert project1["id"] in [
        i["project_id"] for i in api.state["sections"] if i["id"] == section1["id"]
    ]

    section1.delete()
    api.commit()
    project1.delete()
    api.commit()


def test_section_reorder(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    section1 = api.sections.add("Section1", api.state["user"]["inbox_project"])
    api.commit()
    section2 = api.sections.add("Section2", api.state["user"]["inbox_project"])
    api.commit()

    api.sections.reorder(
        sections=[
            {"id": section1["id"], "section_order": 2},
            {"id": section2["id"], "section_order": 1},
        ]
    )
    response = api.commit()
    for section in response["sections"]:
        if section["id"] == section1["id"]:
            assert section["section_order"] == 2
        if section["id"] == section2["id"]:
            assert section["section_order"] == 1
    assert 2 in [
        p["section_order"] for p in api.state["sections"] if p["id"] == section1["id"]
    ]
    assert 1 in [
        p["section_order"] for p in api.state["sections"] if p["id"] == section2["id"]
    ]

    section1.delete()
    api.commit()
    section2.delete()
    api.commit()


def test_filter_add(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    filter1 = api.filters.add("Filter1", "no due date")
    response = api.commit()
    assert response["filters"][0]["name"] == "Filter1"
    assert "Filter1" in [f["name"] for f in api.state["filters"]]
    assert api.filters.get_by_id(filter1["id"]) == filter1
    assert api.filters.get(filter1["id"])["filter"]["name"] == filter1["name"]

    filter1.delete()
    api.commit()


def test_filter_delete(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    filter1 = api.filters.add("Filter1", "no due date")
    api.commit()

    filter1.delete()
    response = api.commit()
    assert response["filters"][0]["id"] == filter1["id"]
    assert response["filters"][0]["is_deleted"] == 1
    assert "Filter1" not in [p["name"] for p in api.state["filters"]]


def test_filter_update(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    filter1 = api.filters.add("Filter1", "no due date")
    api.commit()

    filter1.update(name="UpdatedFilter1")
    response = api.commit()
    assert response["filters"][0]["name"] == "UpdatedFilter1"
    assert "UpdatedFilter1" in [f["name"] for f in api.state["filters"]]
    assert api.filters.get_by_id(filter1["id"]) == filter1

    filter1.delete()
    api.commit()


def test_filter_update_orders(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    filter1 = api.filters.add("Filter1", "no due date")
    api.commit()

    filter2 = api.filters.add("Filter2", "today")
    api.commit()

    api.filters.update_orders({filter1["id"]: 2, filter2["id"]: 1})
    response = api.commit()
    for filter in response["filters"]:
        if filter["id"] == filter1["id"]:
            assert filter["item_order"] == 2
        if filter["id"] == filter2["id"]:
            assert filter["item_order"] == 1
    assert 2 in [
        f["item_order"] for f in api.state["filters"] if f["id"] == filter1["id"]
    ]
    assert 1 in [
        f["item_order"] for f in api.state["filters"] if f["id"] == filter2["id"]
    ]

    filter1.delete()
    api.commit()
    filter2.delete()
    api.commit()


def test_reminder_relative_add(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    item1 = api.items.add("Item1", due={"string": "tomorrow 5pm"})
    api.commit()

    reminder1 = api.reminders.add(item1["id"], minute_offset=30)
    response = api.commit()
    assert response["reminders"][0]["minute_offset"] == 30
    assert reminder1["id"] in [p["id"] for p in api.state["reminders"]]
    assert api.reminders.get_by_id(reminder1["id"]) == reminder1
    assert api.reminders.get(reminder1["id"])["reminder"]["due"] == reminder1["due"]

    reminder1.delete()
    api.commit()
    item1.delete()
    api.commit()


def test_reminder_relative_delete(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    item1 = api.items.add("Item1", due={"string": "tomorrow 5pm"})
    api.commit()
    reminder1 = api.reminders.add(item1["id"], minute_offset=30)
    api.commit()

    reminder1.delete()
    response = api.commit()
    assert response["reminders"][0]["is_deleted"] == 1
    assert reminder1["id"] not in [p["id"] for p in api.state["reminders"]]

    item1.delete()
    api.commit()


def test_reminder_relative_update(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    item1 = api.items.add("Item1", due={"string": "tomorrow 5pm"})
    api.commit()
    reminder1 = api.reminders.add(item1["id"], minute_offset=30)
    api.commit()

    reminder1.update(minute_offset=str(15))
    response = api.commit()
    assert response["reminders"][0]["minute_offset"] == 15
    assert reminder1["id"] in [p["id"] for p in api.state["reminders"]]
    assert api.reminders.get_by_id(reminder1["id"]) == reminder1

    reminder1.delete()
    api.commit()
    item1.delete()
    api.commit()


def test_reminder_absolute_add(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    item1 = api.items.add("Item1", due={"string": "tomorrow 5pm"})
    api.commit()

    now = time.time()
    tomorrow = time.gmtime(now + 24 * 3600)
    due_date_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", tomorrow)
    reminder1 = api.reminders.add(item1["id"], due={"date": due_date_utc})
    response = api.commit()
    assert response["reminders"][0]["due"]["date"] == due_date_utc
    tomorrow = time.gmtime(time.time() + 24 * 3600)
    assert reminder1["id"] in [p["id"] for p in api.state["reminders"]]
    assert api.reminders.get_by_id(reminder1["id"]) == reminder1
    assert api.reminders.get(reminder1["id"])["reminder"]["due"] == reminder1["due"]

    reminder1.delete()
    api.commit()
    item1.delete()
    api.commit()


def test_reminder_absolute_delete(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    item1 = api.items.add("Item1", due={"string": "tomorrow 5pm"})
    api.commit()

    now = time.time()
    tomorrow = time.gmtime(now + 24 * 3600)
    due_date_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", tomorrow)
    reminder1 = api.reminders.add(item1["id"], due={"date": due_date_utc})
    api.commit()

    api.reminders.delete(reminder1["id"])
    response = api.commit()
    assert response["reminders"][0]["is_deleted"] == 1
    assert reminder1["id"] not in [p["id"] for p in api.state["reminders"]]

    item1.delete()
    response = api.commit()


def test_reminder_absolute_update(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api.sync()

    item1 = api.items.add("Item1", due={"string": "tomorrow 5pm"})
    api.commit()

    now = time.time()
    tomorrow = time.gmtime(now + 24 * 3600)
    due_date_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", tomorrow)
    reminder1 = api.reminders.add(item1["id"], due={"date": due_date_utc})
    api.commit()

    tomorrow = time.gmtime(now + 24 * 3600 + 60)
    due_date_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", tomorrow)
    api.reminders.update(reminder1["id"], due_date_utc=due_date_utc)
    response = api.commit()
    assert response["reminders"][0]["due"]["date"] == due_date_utc
    assert reminder1["id"] in [p["id"] for p in api.state["reminders"]]
    assert api.reminders.get_by_id(reminder1["id"]) == reminder1

    reminder1.delete()
    api.commit()
    item1.delete()
    api.commit()


def test_locations(api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)

    api.sync()

    api.locations.clear()
    api.commit()

    assert api.state["locations"] == []


def test_live_notifications(api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)

    api.sync()

    api.live_notifications.set_last_read(api.state["live_notifications_last_read_id"])
    response = api.commit()
    assert (
        response["live_notifications_last_read_id"]
        == api.state["live_notifications_last_read_id"]
    )


def test_share_accept(cleanup, cleanup2, api_endpoint, api_token, api_token2):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api2 = todoist.api.TodoistAPI(api_token2, api_endpoint)

    api.user.update(auto_invite_disabled=1)
    api.commit()
    api.sync()

    api2.user.update(auto_invite_disabled=1)
    api2.commit()
    api2.sync()

    project1 = api.projects.add("Project1")
    api.commit()

    api.projects.share(project1["id"], api2.state["user"]["email"])
    response = api.commit()
    assert response["projects"][0]["name"] == project1["name"]
    assert response["projects"][0]["shared"]

    response2 = api2.sync()
    invitation1 = next(
        (
            ln
            for ln in response2["live_notifications"]
            if ln["notification_type"] == "share_invitation_sent"
        ),
        None,
    )
    assert invitation1 is not None
    assert invitation1["project_name"] == project1["name"]
    assert invitation1["from_user"]["email"] == api.state["user"]["email"]

    api2.invitations.accept(invitation1["id"], invitation1["invitation_secret"])
    response2 = api2.commit()
    assert api2.state["user"]["id"] in [
        p["user_id"] for p in api2.state["collaborator_states"]
    ]

    api.sync()
    project1 = [p for p in api.state["projects"] if p["name"] == "Project1"][0]
    project1.delete()
    api.commit()


def test_share_reject(cleanup, cleanup2, api_endpoint, api_token, api_token2):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api2 = todoist.api.TodoistAPI(api_token2, api_endpoint)

    api.user.update(auto_invite_disabled=1)
    api.commit()
    api.sync()

    api2.user.update(auto_invite_disabled=1)
    api2.commit()
    api2.sync()

    project1 = api.projects.add("Project1")
    api.commit()

    api.projects.share(project1["id"], api2.state["user"]["email"])
    response = api.commit()
    assert response["projects"][0]["name"] == project1["name"]
    assert response["projects"][0]["shared"]

    response2 = api2.sync()
    invitation2 = next(
        (
            ln
            for ln in response2["live_notifications"]
            if ln["notification_type"] == "share_invitation_sent"
        ),
        None,
    )
    assert invitation2 is not None
    assert invitation2["project_name"] == project1["name"]
    assert invitation2["from_user"]["email"] == api.state["user"]["email"]

    api2.invitations.reject(invitation2["id"], invitation2["invitation_secret"])
    response2 = api2.commit()
    assert len(response2["projects"]) == 0
    assert len(response2["collaborator_states"]) == 0

    project1 = [p for p in api.state["projects"] if p["name"] == "Project1"][0]
    project1.delete()
    api.commit()


def test_share_delete(cleanup, cleanup2, api_endpoint, api_token, api_token2):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)
    api2 = todoist.api.TodoistAPI(api_token2, api_endpoint)

    api.user.update(auto_invite_disabled=1)
    api.commit()
    api.sync()

    api2.user.update(auto_invite_disabled=1)
    api2.commit()
    api2.sync()

    project1 = api.projects.add("Project1")
    api.commit()

    api.projects.share(project1["id"], api2.state["user"]["email"])
    response = api.commit()
    assert response["projects"][0]["name"] == project1["name"]
    assert response["projects"][0]["shared"]

    response2 = api2.sync()
    invitation3 = next(
        (
            ln
            for ln in response2["live_notifications"]
            if ln["notification_type"] == "share_invitation_sent"
        ),
        None,
    )
    assert invitation3 is not None
    assert invitation3["project_name"] == project1["name"]
    assert invitation3["from_user"]["email"] == api.state["user"]["email"]

    api.invitations.delete(invitation3["id"])
    api.commit()

    project1 = [p for p in api.state["projects"] if p["name"] == "Project1"][0]
    project1.delete()
    api.commit()


def test_items_archive(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)

    # Create and complete five tasks
    project = api.projects.add("Project")
    items = [
        api.items.add("task{}".format(i), project_id=project["id"]) for i in range(5)
    ]
    for i, item in enumerate(items):
        date_completed = "2019-01-01T00:00:0{}Z".format(i)
        api.items.complete(item_id=item["id"], date_completed=date_completed)
    api.commit()

    # Create an archive manager to iterate over them
    manager = api.items_archive.for_project(project["id"])
    item_ids = [item["id"] for item in manager.items()]
    assert item_ids == [item["id"] for item in items[::-1]]

    # tear down
    project.delete()
    api.commit()


def test_sections_archive(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)

    # Create and complete five sections
    project = api.projects.add("Project")
    sections = [
        api.sections.add("s{}".format(i), project_id=project["id"]) for i in range(5)
    ]
    for i, section in enumerate(sections):
        date_archived = "2019-01-01T00:00:0{}Z".format(i)
        api.sections.archive(section_id=section["id"], date_archived=date_archived)
    api.commit()

    # Create an archive manager to iterate over them
    manager = api.sections_archive.for_project(project["id"])
    section_ids = [section["id"] for section in manager.sections()]
    assert section_ids == [section["id"] for section in sections[::-1]]

    # tear down
    project.delete()
    api.commit()


def test_templates(cleanup, api_endpoint, api_token):
    api = todoist.api.TodoistAPI(api_token, api_endpoint)

    api.sync()

    project1 = api.projects.add("Project1")
    project2 = api.projects.add("Project2")
    api.commit()

    item1 = api.items.add("Item1", project_id=project1["id"])
    api.commit()

    template = api.templates.export_as_file(project1["id"])
    assert "task,Item1,4,1" in template
    with io.open("/tmp/example.csv", "w", encoding="utf-8") as example:
        example.write(template)

    result = api.templates.import_into_project(project1["id"], "/tmp/example.csv")
    assert result == {"status": u"ok"}

    item1.delete()
    api.commit()
    project1.delete()
    api.commit()
    project2.delete()
    api.commit()
