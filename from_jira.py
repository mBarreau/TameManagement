from jira import JIRA
import sqlite3
from tqdm import tqdm

jiraOptions = {"server": "https://***.atlassian.net/"}
jira = JIRA(
    server=jiraOptions,
    basic_auth=(
        "***@***.***",
        "***",
    ),
)

issues = []
i = 0
while True:
    chunk = jira.search_issues(
        jql_str="order by created DESC", startAt=i, maxResults=50
    )
    issues += chunk.iterable
    i += 50
    if i >= chunk.total:
        break

con = sqlite3.connect("time_management.db")
cur = con.cursor()
for issue in tqdm(issues):
    cur.execute(
        "INSERT INTO tasks(title, due_date, sp, description, status, sprint) VALUES (?, ?, ?, ?, ?, ?)",
        (
            issue.fields.summary,
            issue.fields.duedate,
            issue.fields.customfield_10035,
            issue.fields.description,
            issue.fields.status.name,
            False,
        ),
    )
con.commit()
