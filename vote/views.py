from itertools import zip_longest
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.db import models
from django.db.models import Count, Sum

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import FollowEvent, MessageEvent, PostbackEvent, TextSendMessage, FlexSendMessage
from .models import Candidate, Gender, Age, Area, User, Vote, Comment, History
import datetime
import json

# setup line API
line_bot_id = settings.LINE_BOT_ID
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

# create quick reply
quick_reply_option1 = { "items": [] }
quick_reply_option2 = { "items": [] }
quick_reply_option3 = { "items": [] }
for candidate in Candidate.objects.all().order_by('id'):
    name, id = candidate.name, str(candidate.id)
    option1 = { "type": "action", "action": { "type": "postback", "label": name, "data": "option1,"+id } }
    option2 = { "type": "action", "action": { "type": "postback", "label": name, "data": "option2,"+id } }
    option3 = { "type": "action", "action": { "type": "postback", "label": name, "data": "option3,"+id } }
    quick_reply_option1['items'].append(option1)
    quick_reply_option2['items'].append(option2)
    quick_reply_option3['items'].append(option3)

done = { "type": "action", "action": { "type": "postback", "label": "結束", "data": "done,0" } }
quick_reply_option1['items'].pop(3)
quick_reply_option1['items'].append(done)
quick_reply_option2['items'].append(done)
quick_reply_option3['items'].append(done)

quick_reply_gender = { "items": [] }
for gender in Gender.objects.all().order_by('id'):
    item = { "type": "action", "action": { "type": "postback", "label": gender.option, "data": "gender,"+str(gender.id) } }
    quick_reply_gender['items'].append(item)
quick_reply_gender['items'].append(done)

quick_reply_age = { "items": [] }
for age in Age.objects.all().order_by('id'):
    item = { "type": "action", "action": { "type": "postback", "label": age.option, "data": "age,"+str(age.id) } }
    quick_reply_age['items'].append(item)
quick_reply_age['items'].append(done)

quick_reply_area = { "items": [] }
for area in Area.objects.all().order_by('id'):
    item = { "type": "action", "action": { "type": "postback", "label": area.option, "data": "area,"+str(area.id) } }
    quick_reply_area['items'].append(item)
quick_reply_area['items'].append(done)

flexmsg = open('flexmsg.json')
flex_message_sum = json.load(flexmsg)
    

# set vote information to flex message
def set_vote_message(user, message):
    vote = user.vote
    header = message.contents.header
    header.contents[2].text += str(user.id)
    header.contents[3].text += vote.option1.name if vote.option1 is not None else "❓"
    header.contents[4].text += vote.option2.name if vote.option2 is not None else "❓"
    header.contents[5].text += vote.option3.name if vote.option3 is not None else "❓"
    header.contents[6].text += user.gender.option if user.gender is not None else "❓"
    header.contents[7].text += user.age.option if user.age is not None else "❓"
    header.contents[8].text += user.area.option if user.area is not None else "❓"
    return message


# linebot webhook
@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
 
        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()
 
        for event in events:
            # follow event
            if isinstance(event, FollowEvent):
                line_id = event.source.user_id
                profile = line_bot_api.get_profile(line_id)
                message = TextSendMessage(text="Hi "+profile.display_name+" 歡迎加入 !\n請點選下方 [選單] 開始投票喔 ~")
                line_bot_api.reply_message(event.reply_token, message)
                try:
                    user = User.objects.get(uid=line_id)
                except User.DoesNotExist:
                    user = User.objects.create(uid=line_id, name=profile.display_name, image=profile.picture_url, language=profile.language)
                    vote = Vote.objects.create(user=user)

            # postback event
            elif isinstance(event, PostbackEvent): 
                line_id = event.source.user_id
                key, value = (event.postback.data.split(",") + [None])[:2]
                # print("debug: line_id = ", line_id, ", data = ", key, value)
                if key == "vote":
                    message = TextSendMessage(text="請問您想投給誰 ? ", quick_reply=quick_reply_option1)
                    line_bot_api.reply_message(event.reply_token, message)

                elif key == "option1":
                    message = TextSendMessage(text="以下組合，您想投給誰 ? ", quick_reply=quick_reply_option2)
                    line_bot_api.reply_message(event.reply_token, message)
                    vote = Vote.objects.get(user__uid=line_id)
                    if vote.option1 is None or vote.option1.id != int(value):
                        vote.option1 = Candidate.objects.get(id=int(value))
                        vote.save()

                elif key == "option2":
                    message = TextSendMessage(text="請問您最不希望誰當選 ? ", quick_reply=quick_reply_option3)
                    line_bot_api.reply_message(event.reply_token, message)
                    vote = Vote.objects.get(user__uid=line_id)
                    if vote.option2 is None or vote.option2.id != int(value):
                        vote.option2 = Candidate.objects.get(id=int(value))
                        vote.save()

                elif key == "option3":
                    message = TextSendMessage(text="請問您的性別是 ? ", quick_reply=quick_reply_gender)
                    line_bot_api.reply_message(event.reply_token, message)
                    vote = Vote.objects.get(user__uid=line_id)
                    if vote.option3 is None or vote.option3.id != int(value):
                        vote.option3 = Candidate.objects.get(id=int(value))
                        vote.save()

                elif key == "gender":
                    message = TextSendMessage(text="請問您的年齡是 ? ", quick_reply=quick_reply_age)
                    line_bot_api.reply_message(event.reply_token, message)
                    user = User.objects.get(uid=line_id)
                    if user.gender is None or user.gender.id != int(value):
                        user.gender = Gender.objects.get(id=int(value))
                        user.save()

                elif key == "age":
                    message = TextSendMessage(text="請問您的戶籍地是 ? ", quick_reply=quick_reply_area)
                    line_bot_api.reply_message(event.reply_token, message)
                    user = User.objects.get(uid=line_id)
                    if user.age is None or user.age.id != int(value):
                        user.age = Age.objects.get(id=int(value))
                        user.save()

                elif key == "area":
                    user = User.objects.get(uid=line_id)
                    if user.area is None or user.area.id != int(value):
                        user.area = Area.objects.get(id=int(value))
                        user.save()
                    message = FlexSendMessage(alt_text='sum', contents=flex_message_sum)
                    set_vote_message(user, message)
                    line_bot_api.reply_message(event.reply_token, message)

                elif key == "done":
                    user = User.objects.get(uid=line_id)
                    message = FlexSendMessage(alt_text='sum', contents=flex_message_sum)
                    set_vote_message(user, message)
                    line_bot_api.reply_message(event.reply_token, message)

            # message event
            elif isinstance(event, MessageEvent):
                line_id = event.source.user_id
                user = User.objects.get(uid=line_id)
                name, comment = (event.message.text.split(":") + [None])[:2]
                # print("debug: line_id = ", line_id, ", name = ", name, ", comment = ", comment)
                if comment is not None:
                    if name == "開始投票":
                        message = TextSendMessage(text="請問您想投給誰 ? ", quick_reply=quick_reply_option1)
                        line_bot_api.reply_message(event.reply_token, message)

                    elif name == "意見回饋":
                        name = "尚未決定" 

                    try:
                        candidate = Candidate.objects.get(name=name)
                        Comment.objects.update_or_create(user=user, candidate=candidate, defaults={"content": comment})
                    except:
                        pass

        return HttpResponse()

    else:
        return HttpResponseBadRequest()


# record_list = [
#     [[35, 34, 40], [20, 13, 15], [18, 18, 11], [0, 12, 15]],
#     [[35, 35, 42], [19, 12, 15], [19, 17, 12], [0, 12, 18]],
#     [[36, 34, 38], [18, 13, 16], [22, 17, 12], [0, 11, 16]],
#     [[40, 36, 38], [25, 18, 13], [22, 16, 15], [0,  8, 20]],
#     [[39, 34, 38], [18, 13, 16], [23, 18, 12], [0, 10, 12]],
#     [[38, 36, 33], [20, 15, 14], [26, 20, 14], [0, 11, 15]],
#     [[38, 37, 36], [22, 17, 13], [24, 22, 10], [0, 12, 18]]
# ]
# i = len(record_list)
# for record in record_list:
#     history = History.objects.create(vote=record)
#     date = datetime.datetime.now() - datetime.timedelta(days=i)
#     history.date = date
#     history.save()
#     i -= 1

def index(request):
    candidate_list = Candidate.objects.all().order_by('id')[:4]
    for candidate in candidate_list:
        comment_list = Comment.objects.filter(candidate=candidate).order_by('-date')[:20]
        candidate.comments = comment_list.values_list('user__name', 'content')

    vote_list = list(Candidate.objects.annotate(cnt1=Count('option1', distinct=True), cnt2=Count('option2', distinct=True), 
            cnt3=Count('option3', distinct=True)).values_list('cnt1', 'cnt2', 'cnt3'))
    vote_list = list(map(list, zip(*vote_list)))

    # history_list = list(History.objects.annotate(date_=Cast('date', TextField())).values('date_', 'vote'))
    history_list = list(History.objects.values('date', 'vote'))
    
    context = {'line_bot_id': line_bot_id, 'candidate_list': candidate_list, 'vote_list': vote_list, 'history_list': json.dumps(history_list, default=str) }
    return render(request, 'vote.html', context)


def record(request):
    date = datetime.datetime.now()
    vote_list = list(Candidate.objects.annotate(cnt1=Count('option1', distinct=True), cnt2=Count('option2', distinct=True), 
            cnt3=Count('option3', distinct=True)).values_list('cnt1', 'cnt2', 'cnt3'))
    vote_list = list(map(list, vote_list))
    
    History.objects.update_or_create(date=date, defaults={"vote": vote_list})

    return HttpResponse(vote_list)


def detail(request):
    user_list = User.objects.all()
    candidate_list = Candidate.objects.all()
    gender_array = [list(Gender.objects.values_list('option', flat=True))]
    age_array = [list(Age.objects.values_list('option', flat=True))]
    area_array = [list(Area.objects.values_list('option', flat=True))]
    for candidate in candidate_list:
        gender_list = list(Gender.objects.annotate(c=Count('user', filter=models.Q(user__vote__option1=candidate), distinct=True)).values_list('c', flat=True))
        age_list = list(Age.objects.annotate(c=Count('user', filter=models.Q(user__vote__option1=candidate), distinct=True)).values_list('c', flat=True))
        area_list = list(Area.objects.annotate(c=Count('user', filter=models.Q(user__vote__option1=candidate), distinct=True)).values_list('c', flat=True))
        gender_array.append(gender_list)
        age_array.append(age_list)
        area_array.append(area_list)

    gender_array = list(map(list, zip(*gender_array)))
    age_array = list(map(list, zip(*age_array)))
    area_array = list(map(list, zip(*area_array)))

    context = {'user_list': user_list, 'candidate_list': candidate_list, 'gender_array': gender_array, 'age_array': age_array, 'area_array': area_array}
    return render(request, 'vote_detail.html', context)

