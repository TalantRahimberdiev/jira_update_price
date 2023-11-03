
from jira import JIRA
import pandas as pd

JIRA_OPTIONS = {'server': 'https://jirasd.saima.kg'}
JQL = 'project = CS AND issuetype = "[SUB] Новый абонент - ОАП: Монтаж" AND status in (Закрытый, "СОГЛАСОВАНИЕ ОАП", "НА УТОЧНЕНИИ У БРИГАДИРА") AND createdDate >= "2023/11/01" AND assignee in (trakhimberdiev)'

BLOCK_SIZE = 1000
SLOJNOST_LEVELS = {'0.0': 0, '1.0': 400, '2.0': 500,
                   '3.0': 600, '4.0': 800, '5.0': 1300}


def get_tickets(jira, jql, fields):

    block_num = 0
    has_more_tickets = True

    while has_more_tickets:
        start_idx = block_num * BLOCK_SIZE
        tickets = jira.search_issues(
            jql, fields=fields, startAt=start_idx, maxResults=BLOCK_SIZE)
        if not tickets:
            has_more_tickets = False
        else:
            for t in tickets:
                yield t
            block_num += 1


def calculate_update(jira, issue, custom_fields_categories):
    issue_dict = {
        'issue_num': 0,
        'brigadir': '',
        'router_quantity': 0,
        'pristavka_quantity': 0,
        'slojnost_podkluchenia': 0,
        'stoimost_podkluchenia': '',
        'total_sum': 0
    }
    issue_dict['issue_num'] = issue.key

    for fio in custom_fields_categories['brigadir']:
        if fio in issue.fields.__dict__:
            if (issue.fields.__dict__[fio] != None):
                tmp = issue.fields.__dict__[fio]
                issue_dict['brigadir'] = tmp.__dict__['displayName']

    for router in custom_fields_categories['routers']:
        if router in issue.fields.__dict__:
            if (issue.fields.__dict__[router] != None):
                issue_dict['router_quantity'] += issue.fields.__dict__[router]

    for pristavka in custom_fields_categories['pristavkas']:
        if pristavka in issue.fields.__dict__:
            if (issue.fields.__dict__[pristavka] != None):
                issue_dict['pristavka_quantity'] += issue.fields.__dict__[pristavka]

    for slojnost in custom_fields_categories['slojnost_podkluchenia']:
        if slojnost in issue.fields.__dict__:
            if issue.fields.__dict__[slojnost] != None:
                issue_dict['slojnost_podkluchenia'] = issue.fields.__dict__[
                    slojnost]

    for stoimost in custom_fields_categories['stoimost_podkluchenia']:
        if stoimost in issue.fields.__dict__:
            if issue.fields.__dict__[stoimost] != None:
                issue_dict['stoimost_podkluchenia'] = issue.fields.__dict__[
                    stoimost]

    pristavka_count = 1 if issue_dict['pristavka_quantity'] == 0 else issue_dict['pristavka_quantity']
    router_count = 1 if issue_dict['router_quantity'] == 0 else issue_dict['router_quantity']
    slojnost = SLOJNOST_LEVELS[
        str(float(issue_dict['slojnost_podkluchenia']))] if issue_dict['slojnost_podkluchenia'] else 0

    issue_dict['total_sum'] = int(200*(pristavka_count-1) + 200 *
                                  (router_count-1) + slojnost)

    return issue_dict


"""
    to_be_updated = jira.issue(issue_dict['issue_num'], fields=[
                               'customfield_10618'])
    to_be_updated.update(
        fields={'customfield_10618': str(issue_dict['total_sum'])})
"""


def main():
    jira = JIRA(options=JIRA_OPTIONS, basic_auth=(
        'trakhimberdiev', 'password'))

    custom_fields_categories = {
        'routers': ['customfield_11282', 'customfield_12607', 'customfield_13908', 'customfield_13909',
                    'customfield_11283', 'customfield_11300', 'customfield_13000', 'customfield_13700',
                    'customfield_13703', 'customfield_13704', 'customfield_13801', 'customfield_11284',
                    'customfield_12629', 'customfield_12630', 'customfield_12605', 'customfield_12606'],
        'pristavkas': ['customfield_11284', 'customfield_11285', 'customfield_11286', 'customfield_13702',
                       'customfield_12627', 'customfield_12628', 'customfield_11946'],
        'slojnost_podkluchenia': ['customfield_12631', 'customfield_11066'],
        'stoimost_podkluchenia': ['customfield_10618', 'customfield_12703'],
        'brigadir': ['customfield_10955']
    }

    all_customfields = sum(custom_fields_categories.values(), [])
    tickets = list(get_tickets(jira, JQL, all_customfields))

    issues_list = [calculate_update(jira,
                                    ticket, custom_fields_categories) for ticket in tickets]

    print('--------------------calculated_updated--------------------')

    for issue in issues_list:
        print(issue)
    print(len(issues_list))

    df = pd.DataFrame.from_dict(issues_list)
    df.to_excel('players.xlsx')


if __name__ == "__main__":
    main()
