from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import json
import requests


@csrf_exempt
def github_webhook(request):
    if request.method == 'POST':
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponseBadRequest('Invalid JSON payload')

        event = request.headers.get('X-GitHub-Event')
        if not event:
            return HttpResponseBadRequest('Missing X-GitHub-Event header')

        if event == 'issues' and payload['action'] == 'opened':
            issue_title = payload['issue']['title']
            issue_body = payload['issue']['body']
            issue_url = payload['issue']['html_url']

            send_slack_notification(issue_title, issue_body, issue_url)

            return JsonResponse({'status': 'success'})
        return JsonResponse({'status':'ignored'})
    else:
        return HttpResponseBadRequest('Only POST requests are allowed')

def send_slack_notification(title,body,url):
    webhook_url = 'https://hooks.slack.com/services/XXXXXXXXX/YYYYYYYYY/ZZZZZZZZZZZZZZZZZZZZZZZZ' ###

    slack_data = {
        'text': f'New GitHub Issue Created: *{title}*\n{body}\n<{url}|View Issue>'
    }

    # Отправляем POST-запрос на URL вебхука Slack с данными
    response = requests.post(webhook_url, json=slack_data)

    # Проверяем успешность отправки уведомления
    if response.status_code != 200:
        # Если запрос не успешен, выбрасываем исключение
        raise ValueError(
            f'Request to Slack returned an error {response.status_code}, the response is:\n{response.text}')
