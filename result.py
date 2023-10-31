from jira import JIRA  # импортировать библиотеку

JIRA_OPTIONS = {'server': 'https://jirasd.saima.kg'}  # параметр для JIRA

# jql запрос для получения нужных заявок
JQL = 'project = CS AND issuetype = "[SUB] Новый абонент - ОАП: Монтаж" AND status in (Закрытый, "СОГЛАСОВАНИЕ ОАП", "НА УТОЧНЕНИИ У БРИГАДИРА") AND createdDate >= "2023/10/01"'


BLOCK_SIZE = 1000  # максимальный размер извлеченных заявок
SLOJNOST_LEVELS = {'0.0': 0, '1.0': 400, '2.0': 500,
                   '3.0': 600, '4.0': 800, '5.0': 1300}  # сложность подключения - стоимость в зависимости от ТМЦ


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

# get_tickets () ---> функция по извлечению заявок из jira.


# функция для вычисления сложности подк-я и обновления в jira заявок
def calculate_update(jira, issue, custom_fields_categories):
    issue_dict = {
        'issue_num': 0,
        'router_quantity': 0,
        'pristavka_quantity': 0,
        'slojnost_podkluchenia': 0,
        'stoimost_podkluchenia': '',
        'total_sum': 0
    }
    issue_dict['issue_num'] = issue.key

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

# цикл проходит по ТМЦ на их наличие в заявке, при условии если ТМЦ есть и ТМЦ не явл-ся null тогда вводится в словарь

    # назначется 1 если 0, чтобы не было отр.числа
    pristavka_count = 1 if issue_dict['pristavka_quantity'] == 0 else issue_dict['pristavka_quantity']
    # назначется 1 если 0, чтобы не было отр.числа
    router_count = 1 if issue_dict['router_quantity'] == 0 else issue_dict['router_quantity']
    slojnost = SLOJNOST_LEVELS[
        str(float(issue_dict['slojnost_podkluchenia']))] if issue_dict['slojnost_podkluchenia'] else 0  # вводим в переменную slojnost из SLOJNOST_LEVELS

    issue_dict['total_sum'] = int(200*(pristavka_count-1) + 200 *
                                  (router_count-1) + slojnost)

    to_be_updated = jira.issue(issue_dict['issue_num'], fields=[
                               'customfield_10618'])
    to_be_updated.update(
        fields={'customfield_10618': str(issue_dict['total_sum'])})

    return issue_dict
# ввод в словарь результат, 2. определяем заявку для обновления 3. обновляем заявку.


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
        'stoimost_podkluchenia': ['customfield_10618', 'customfield_12703']
    }

# 90 - 99 строки словарь из словарь состоящий из списков ТМЦ

    # конверитирует из словаря в список
    all_customfields = sum(custom_fields_categories.values(), [])
    # результат вызванной функции
    tickets = list(get_tickets(jira, JQL, all_customfields))

    issues_list = [calculate_update(jira,
                                    ticket, custom_fields_categories) for ticket in tickets]  # вызывается функция для вычисления и обновления заявок

    print('--------------------calculated_updated--------------------')

    for issue in issues_list:
        print(issue)
    print(len(issues_list))


if __name__ == "__main__":
    main()
