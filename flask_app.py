from flask import Flask, request, json
import vk
from keyboards import *
import sqlite3
app = Flask(__name__)
token='d43c1bf380e74fdd98468d2b0582229129eb3881d7de0d52e7f9498ea9884f60c40a5865310faf14c6df1'
log_token='cb6595109a837cb4985dbabcf8a9776c0a3f39107efc763ed78f037a0aff1029a04e20e5858d1ac4f3cec'
confirmation_token = 'b3f50448'
logs_confirmation_token = '5542c3ce'
# access_token = 'f686aa00f686aa00f686aa007cf6e13905ff686f686aa00aa9eb416c07043c515eceef1'
conn = sqlite3.connect('mysite/data.db')
c = conn.cursor()
f_sell=['sell','продать', 'продажа', 's', 'п']
f_buy=['buy','купить', 'покупка', 'b', 'к']
f_vyh=['exit','выход','выйти', 'меню','menu','main','главное']
f_help=['help','info','помощь','инфо', 'баг']
f_start=['здравствуйте','привет','hi','начать', 'start']
f_newbid=['bid','оффер', 'ставка']
f_my=['мои офферы','my', 'мое','мои','моё']
w_dell=['dell','удалить','d','у']
w_edit=['edit','изм','и','изменить','редактировать', 'e']
teste=['t32']
gr_id='175148859'
admins = ['59391112']
def log(msg):
    session = vk.Session()
    api = vk.API(session, v=5.0)
    for i in admins:
        api.messages.send(access_token=log_token, user_id=str(i), message=msg)
def otvet(uid,msg,kb="", att=""):
    session = vk.Session()
    api = vk.API(session, v=5.0)
    if kb == '':
        a = api.messages.send(access_token=token, user_id=str(uid), message=msg, attachment = att)
    else:
        a = api.messages.send(access_token=token, user_id=str(uid), message=msg, keyboard = kb, attachment = att)
    c.execute("UPDATE menu SET last_message_id='"+str(a)+"' WHERE id = '"+uid+"'")
    try:
        api.groups.enableOnline(access_token=token, group_id=gr_id)
    except:
        dfrtgedwe = None
def last_message_editor(uid,text,att=''):
    c.execute("SELECT last_message_id FROM menu WHERE id = '"+uid+"'")
    msg_id=c.fetchone()[0]
    session = vk.Session()
    api = vk.API(session, v=5.0)
    api.messages.edit(access_token=token, peer_id=str(uid), message=text, message_id=msg_id, attachment = att)
def offers(uid,msg,menu):
    #mn == 'a_sell' или mn == 'a_buy':
    if len(msg.split()) == 1:
        msg = msg.upper().replace(',','.')
        c.execute("SELECT item FROM menu WHERE id='" + uid + "'")
        item_id = c.fetchone()[0]
        c.execute("SELECT sizes, name, img FROM grails WHERE id='" + item_id + "'")
        a = c.fetchone(); sizes = a[0].split(); name = a[1];# img = a[2]
        # otvet(uid, msg)
        if msg in sizes:
            t = ['sell','продажу']
            if menu == 'a_sell':
                t = ['buy','покупку']
            c.execute("SELECT bid, vk_id FROM "+t[0]+" WHERE size = '"+msg+"' ORDER BY bid")
            a = c.fetchone(); tt = False; text = ''
            while a != None:
                tt = True
                text +='[id'+a[1]+'|₽'+a[0]+']\n'
                a = c.fetchone()
            if msg.isalpha():
                size = msg
            else:
                size = 'US'+msg
            if tt == True:
                if msg.isalpha():
                    size = msg
                else:
                    size = 'US'+msg
                text = 'Вот все офферы на '+t[1]+' '+size+'\n'+name+'\n'+text+'\n'
            else:
                #Такого размера нет
                text='Нет доступных офферов для размера\nВведи размер, чтобы посмотреть все офферы '+size+'\n'+name
            otvet(uid, text)
        else:
            otvet(uid,name+'\nТакого размера не существует\nВведи размер, чтобы посмотреть все офферы')
    else:
        otvet(uid,'В ответе больше одного слова.\nПопробуй снова')
def searcher(uid, msg):
    message = msg.split()
    c.execute("SELECT id FROM keys WHERE key='"+message[0]+"'")
    mas = c.fetchall()
    for word in range(1,len(message)):
        c.execute("SELECT id FROM keys WHERE key='" + message[word] + "'")
        mas1=c.fetchall()
        b=len(mas)
        i=0
        while i !=b:
            if mas[i] not in mas1:
                del mas[i]
                b-=1
            else:
                i+=1
        if len(mas)==0 or len(mas)==1:
            break
    c.execute("SELECT menu FROM menu WHERE id='"+uid+"'")
    mn = c.fetchone()[0]
    if mas == []:
        otvet(uid,'Такого у нас нет.. Для выхода пиши "выход".\nВсе доступные для взаимодействия вещи находятся тут', kb_v, 'wall-175148859_4')
    elif len(mas)==1:
        iid = mas[0][0]
        masiw = bestbids(mas[0][0], mn) #return(text, kb_v, img)
        if masiw[0] == None and not mn.endswith('offer'):
            otvet(uid,masiw[1]+'.\nГлавное меню.',kb,masiw[2])
            c.execute("UPDATE menu SET menu = 'menu' WHERE id = '"+uid+"'")
        else:
            if masiw[0] == None:#mn.endswith('offer') and
                del masiw[0]
            if mn.endswith('sell'): #if mn == 'sell':
                c.execute("UPDATE menu SET menu = 'a_sell', item = '"+iid+"' WHERE id = '"+uid+"'")
                masiw[0]+='Для просмотра всех офферов введи размер в US через точку'
            elif mn.endswith('buy'):
                c.execute("UPDATE menu SET menu = 'a_buy', item = '"+iid+"' WHERE id = '"+uid+"'")
                masiw[0]+='Для просмотра всех офферов введи размер в US через точку'
            elif mn.endswith('offer'):
                c.execute("UPDATE menu SET menu = 'a_offer', item = '"+iid+"' WHERE id = '"+uid+"'")
                masiw[0]+='\nТеперь введи свой оффер в формате:\n "продать(п)/купить(к) размер цена"\nНапример: п 9.5 21000\nИли вот так: купить 10 19000\nЦена - в рублях, размеры в US'
            otvet(uid,masiw[0],kb_v,masiw[1])
    elif len(mas)>9:
        otvet(uid,'Слишком много совпадений. Попробуй искать иначе.', kb_v)
    else:
        text = 'Поиск неоднозначный. Выберете нужную вещь:\n'
        images = ''
        itemm=''
        for i in range(0, len(mas)):
            c.execute("SELECT name,img FROM grails WHERE id='" + mas[i][0] + "' ORDER BY name")
            a = c.fetchall()
            text+=str(i+1)+'. '+str(a[0][0])+'\n'
            images+= str(a[0][1]) + ','
            itemm+=str(mas[i][0]+' ')
        otvet(uid,text, kb_c,images)
        if mn.endswith('sell'): #if mn == 'sell':
            c.execute("UPDATE menu SET menu = 's_sell', item = '"+itemm+"' WHERE id = '"+uid+"'")
        elif mn.endswith('buy'):
            c.execute("UPDATE menu SET menu = 's_buy', item = '"+itemm+"' WHERE id = '"+uid+"'")
        elif mn.endswith('offer'):
            c.execute("UPDATE menu SET menu = 's_offer', item = '"+itemm+"' WHERE id = '"+uid+"'")
def bestbids(id, menu):
    text = 'Вот лучшие предложения о '
    c.execute("SELECT name, img FROM grails WHERE id='" + id + "' ORDER BY name")
    a = c.fetchone()
    item = a[0];
    img = a[1]
    if menu.endswith('sell'):
        # продавец ищет покупателей
        text += 'покупке \n'
        text += item
        c.execute("SELECT size FROM buy WHERE id='" + id + "'")
    # elif menu.endswith('buy'):
    else:
        # покупатель ищет продавцов
        text += 'продаже \n'
        text += item
        c.execute("SELECT size FROM sell WHERE id='" + id + "'")
    sizes = [];
    text += '\n'
    a = c.fetchone()
    if a == None:
        text = 'Предложений о '+text[25:32]+' этого товара нет.\n'+item
        return [None,text,img]
    elif a[0].isalpha():
        while a != None:
            if a[0].upper() not in sizes:
                sizes.append(a[0].upper())
            a = c.fetchone()
    else:
        while a != None:
            if float(a[0]) not in sizes:
                sizes.append(float(a[0]))
            a = c.fetchone()
    sizes.sort()
    for i in sizes:
        if str(i).endswith('.0'):
            i = str(int(i))
        else:
            i = str(i)
        if menu.endswith('sell'):
            c.execute("SELECT bid, vk_id FROM buy WHERE id='" + id + "' and size = '" + i + "'")
            a = c.fetchone()
            bid = a[0]
            vk_id = a[1]
            while a != None:
                if a[0] > bid:
                    bid = a[0]
                a = c.fetchone()
        else:
            c.execute("SELECT bid, vk_id FROM sell WHERE id='" + id + "' and size = '" + i + "'")
            a = c.fetchone()
            bid = a[0]
            vk_id = a[1]
            while a != None:
                if a[0] < bid:
                    bid = a[0]
                a = c.fetchone()
        if i.isalpha():
            text += '[id'+vk_id+'| '+ i.upper() + ' | ₽'+ bid+']\n'
        else:
            text += '[id'+vk_id+'|US'+ i + ' | ₽'+ bid+']\n'
    return([text, img])
def myoffers(uid):
    text=''; x=0;cc=0
    perda = ['buy','sell']; slova = ['покупку','продажу']
    for b in range(0,2):
        c.execute("SELECT id, size, bid FROM "+perda[b]+" WHERE vk_id='"+uid+"' ORDER BY id")
        a=c.fetchall()
        for i in a:
            if x == 0:
                text+='\bНа '+slova[b]+':\n'
            x+=1
            c.execute("SELECT name FROM grails WHERE id='"+i[0]+"'")
            if i[1].isalpha():
                ji = str(i[1])
                text+=str(x+cc) + '. ' + str(c.fetchone()[0]) + ', ' + ji.upper() + ', ₽' + i[2] + '\n'
            else:
                text+=str(x+cc) + '. ' + str(c.fetchone()[0]) + ', US' + str(i[1]) + ', ₽' + i[2] + '\n'
        cc +=x
        x=0
        text+='\n'
    if cc == 0:
        text = 'У тебя нет размещенных офферов.\nГлавное меню.\n'
        c.execute("UPDATE menu SET menu = 'menu' WHERE id = '"+uid+"'")
    else:
        text ='Все твои офферы:\n\n'+text+'Если хочешь удалить оффер, введи: удалить(у) номер.\nЕсли хочешь поменять цену, введи: изменить(и) номер новая_цена.\nПримеры: 1)у 3 2)изменить 5 5500.\n'
    return(text)
def cabinet(uid):
    ki = myoffers(uid)
    if ki != 'У тебя нет размещенных офферов.\nГлавное меню.\n':
        otvet(uid,ki,kb_v)
        c.execute("UPDATE menu SET menu = 'r_offer' WHERE id = '"+uid+"'")
    else:
        otvet(uid,ki,kb)
def edit_offer(uid, message):
    msg = message.split()
    msg[0]=msg[0].lower()
    if len(msg) not in range(2,4) or (msg[0] not in w_dell and msg[0] not in w_edit) or not msg[1].isdigit():
        otvet(uid,'Неправильный вид запроса.\nЕсли хочешь удалить оффер, введи: удалить(у) номер.\nЕсли хочешь поменять цену, введи: изменить(и) номер новая_цена.\nПримеры: 1)у 3 2)изменить 5 5500')
    else:
        c.execute("SELECT id, size, bid FROM buy WHERE vk_id='"+uid+"' ORDER BY id")
        a_buy = c.fetchall()
        c.execute("SELECT id, size, bid FROM sell WHERE vk_id='"+uid+"' ORDER BY id")
        a_sell = c.fetchall()
        a=a_buy+a_sell
        if int(msg[1]) not in range(1,len(a)+1):
            otvet(uid,'Неправильный номер. У тебя всего '+str(len(a))+' офферов.\nВведи снова:')
        else:
            udalit = msg[0] in w_dell
            b = a[int(msg[1])-1]
            dei = 'sell'
            u = True
            if int(msg[1])<= len(a_buy):
                dei = 'buy'
            if udalit:
                c.execute("DELETE FROM "+dei+" WHERE vk_id='"+uid+"' AND id = '"+b[0]+"' AND size = '"+b[1]+"' AND bid = '"+b[2]+"'")
                dei = 'удалён'
            else:
                if msg[2].isdigit():
                    c.execute("UPDATE "+dei+" SET bid = '"+msg[2]+"' WHERE vk_id='"+uid+"' AND id = '"+b[0]+"' AND size = '"+b[1]+"' AND bid = '"+b[2]+"'")
                    dei = 'изменен'
                else:
                    u = False
                    otvet(uid,'Цена не является целым числом.\nВведите снова полный запрос:')
            if u:
                f = False
                if len(a)==1 and udalit:
                    f = True; t=''
                else:
                    t = 'Ты можешь отредактировать еще один оффер или написать "выход".\n'
                    last_message_editor(uid,myoffers(uid)+'Оффер успешно '+dei+'.\n'+t) #i8
                if f:
                    otvet(uid,'У тебя нет доступных офферов.\nГлавное меню.',kb)
@app.route('/', methods=['POST'])
def processing():
    data = json.loads(request.data)
    if 'type' not in data.keys():
        return 'not vk'
    elif data['type'] == 'confirmation':
        if data['group_id'] == int(gr_id):
            return confirmation_token
        else:
            return logs_confirmation_token
    elif data['type'] == 'group_join':
        #Добавить работу с БД
        uid = data['object']['user_id']
        c.execute("SELECT member FROM settings WHERE id = '" + uid + "'")
        u = c.fetchone()
        if u == None:
            new_user(uid,True)
        elif u == False:

        log('[id'+str(uid)+'|'+str(uid)+ ' вступил в сообщество]')
        return 'ok'
    elif data['type'] == 'group_leave':
        #Добавить работу с БД
        uid = data['object']['user_id']
        log('[id'+str(uid)+'|'+str(uid)+ ' покинул сообщество]')
        return 'ok'
    elif data['type'] == 'message_new' and data['group_id'] == int(gr_id) :
        nmes = str(data['object']['body']).lower()
        uid = str(data['object']['user_id'])
        c.execute("SELECT menu FROM menu WHERE id='"+uid+"'")
        mn = c.fetchone()
        if mn == None:
            c.execute("INSERT INTO menu VALUES ('"+uid+"', 'menu','','','')")
            conn.commit()
            mn = ['menu']
        mn = mn[0]
        # elif nmes not in keys and mn != 'buy' and mn != 'sell' and nmes!='начать':
        #     otvet(uid,'Чушь собачья..')
        if nmes in f_start:
            text='Привет. Я - бот для продажи/покупки лучших релизов.\nЯ буду помогать тебе находить покупателей и продавцов.\nСейчас я нахожусь на стадии альфа-тестирования, поэтому многого не умею\nДля взаимодействия со мной используй клавиатуру бота\nЕсли кнопки нет - используй официальный клиент ВК'
            otvet(uid,text,kb,'photo-175148859_456239042')
        elif nmes in f_vyh:
            c.execute("UPDATE menu SET menu = 'menu', item = '', size = '' WHERE id = '"+uid+"'")
            otvet(uid,'Главное меню', kb)
            conn.commit()
        elif nmes in f_help:
            otvet(uid,'По всем вопросам пиши [sntgl|сюда]')
        elif nmes in f_my:
            cabinet(uid)
        elif nmes in teste:
            tester(uid)
        elif mn == 's_sell' or mn == 's_buy' or mn == 's_offer':
            c.execute("SELECT item FROM menu WHERE id='"+uid+"'")
            itemm = c.fetchone()
            itemm = itemm[0]
            a = itemm.split()
            if nmes.isalpha()==False:
                if int(nmes) in range(0+1,len(a)+1):
                    masiw = bestbids(a[int(nmes)-1], mn)
                    if masiw[0] == None and not mn.endswith('offer'):
                        otvet(uid,masiw[1]+'.\nГлавное меню.',kb,masiw[2])
                        c.execute("UPDATE menu SET menu = 'menu' WHERE id = '"+uid+"'")
                    else:
                        if mn.endswith('offer'):
                            del masiw[0]
                        if mn == 's_sell':
                            c.execute("UPDATE menu SET menu = 'a_sell', item = '"+a[int(nmes)-1]+"' WHERE id = '"+uid+"'")
                            masiw[0]+='Для просмотра всех офферов введи размер в US через точку'
                        elif mn == 's_buy':
                            c.execute("UPDATE menu SET menu = 'a_buy', item = '"+a[int(nmes)-1]+"' WHERE id = '"+uid+"'")
                            masiw[0]+='Для просмотра всех офферов введи размер в US через точку'
                        elif mn == 's_offer':
                            c.execute("UPDATE menu SET menu = 'a_offer', item = '"+a[int(nmes)-1]+"' WHERE id = '"+uid+"'")
                            masiw[0] += 'Теперь введи свой оффер в формате:\n "продать(п)/купить(к)" размер цена".\nНапример: п 9.5 21000,\nИли вот так: купить 10 19000'
                        otvet(uid,masiw[0],kb_v,masiw[1])
                else:
                    otvet(uid,'Такой цифры нет')
            else:
                otvet(uid,'Это не цифра, введи номер нужного пункта')
        elif mn == 'r_offer':
            edit_offer(uid,nmes)
        elif mn == 'a_sell' or mn == 'a_buy':
            # otvet(uid,'Не работает')
            offers(uid,nmes,mn)
        elif mn == 'a_offer':
            #тут чел уже ввел оффер
            if len(nmes.split())!=3:
                otvet(uid,'Здесь более или менее трех слов.\nВведи свой оффер в формате:\n "продать(п)/купить(к) размер цена".\nНапример: п 9.5 21000,\nили вот так: купить 10 19000')
            elif not nmes.split()[2].isdigit():
                otvet(uid,'Третье слово - не цифра.\nВведи свой оффер в формате:\n "продать(п)/купить(к) размер цена".\nНапример: п 9.5 21000,\nили вот так: купить 10 19000')
            else:
                a = nmes.split()
                a[0]=a[0].lower()
                a[1]=a[1].replace(',','.').upper()
                if a[0] not in f_sell and a[0] not in f_buy:
                    otvet(uid,'Первым словом может быть только:\nПродать п sell s\nКупить к buy b\nВведи свой оффер в формате:\n "продать(п)/купить(к) размер цена".\nНапример: п 9.5 21000,\nили вот так: купить 10 19000')
                else:
                    c.execute("SELECT item FROM menu WHERE id='"+uid+"'")
                    item = str(c.fetchone()[0])
                    c.execute("SELECT sizes FROM grails WHERE id='"+item+"'")
                    aloha = c.fetchone()[0]
                    sizes = aloha.split()
                    #a[0] слово; a[1] размер; a[2] цена; uid id чела
                    if a[1].upper() in sizes:
                        if a[0] in f_sell:
                            c.execute("INSERT INTO sell VALUES ('"+item+"', '"+a[1]+"', '"+a[2]+"', '"+uid+"')")
                        else:
                            c.execute("INSERT INTO buy VALUES ('"+item+"', '"+a[1]+"', '"+a[2]+"', '"+uid+"')")
                        # c.execute("UPDATE menu SET menu = 'menu' WHERE id = '"+uid+"'")
                        otvet(uid,'Оффер успешно создан.\nМеню создания нового.\nДля выхода пиши "выход".', kb_v)
                    else:
                        otvet(uid,'Такого сайза не существует. Вот все размеры:\n'+aloha)
        elif mn == 'menu':
            if nmes in f_sell:
                otvet(uid,'Как называется вещь, которую ты хочешь продать?\nНе вводи здесь размер.', kb_v)
                c.execute("UPDATE menu SET menu = 'sell' WHERE id = '"+uid+"'")
            elif nmes in f_buy:
                otvet(uid,'Как называется вещь, которую ты хочешь купить?\nНе вводи здесь размер.', kb_v)
                c.execute("UPDATE menu SET menu = 'buy' WHERE id = '"+uid+"'")
            elif nmes in f_newbid:
                otvet(uid,'Меню создания нового оффера.\nКак называется нужная вещь?', kb_v)
                c.execute("UPDATE menu SET menu = 'offer' WHERE id = '"+uid+"'")
            else:
                otvet(uid,'Чушь собачья..')
        elif mn == 'buy' or mn == 'sell' or mn == 'offer':
            searcher(uid, nmes)
        else:
            otvet(uid,'Что-то пошло не так..')
        conn.commit()
        return 'ok'
    # elif data['type'] == 'message_new':
    # else:
        # otvet(data['object']['user_id'],'ошибка')
        # session = vk.Session()
        # api = vk.API(session, v=5.0)
        # api.messages.send(access_token=log_token, user_id=(data['object']['user_id']), message='Я не отвечаю на сообщения')
        # return 'ok'
        #     session = vk.Session()
        # api = vk.API(session, v=5.0)
        # api.messages.send(access_token=log_token, user_id=data['object']['user_id'], message='044')
        # return 'ok'
