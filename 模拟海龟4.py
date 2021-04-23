from tqsdk import TqApi, TqKq, TargetPosTask, TqAccount, TqAuth
# from 有用的.util_wechat import send_wx_msg
from string import digits
import json
import datetime
import time
from tqsdk.ta import ATR, MA
import math
from playsound import playsound
import asyncio

# 参数
k1 = 20
k2 = 10
k3 = "turtlemoni.json"
k4 = 55
k5 = 20

now1 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(now1, "-     开始连接账号")
# 连接api
api = TqApi(TqKq(), auth=TqAuth("苦集灭道9049", "kq221133"))  # 使用模拟帐号直连行情和交易服务器
now2 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(now2, "-     连接完成，开始计算主力合约，预计20秒")
now3 = datetime.datetime.now()

# 资金控制
# aa = (api.get_account().balance - api.get_account().float_profit) * (1-api.get_account().risk_ratio / 2.5)
aa = api.get_account().balance
ab = aa-500000
# if api.get_account().balance >= 4000000:
#     ab = aa-500000
# else:
#     ab = aa * aa / 4000000-500000

# ------------------------设置品种------------------------
lso = ['AP', 'CF', 'FG', 'MA', 'OI', 'SA', 'SR', 'TA', 'ZC', 'c', 'cs', 'eb', 'i', 'j', 'jd', 'jm', 'p', 'pp',
       'bc', 'nr', 'sc', 'ag', 'al', 'au', 'bu', 'cu', 'fu', 'hc', 'ni', 'pb', 'rb', 'ru', 'sp', 'zn']
lss = []  # lss是全部可交易合约
lss2 = []  # lss2存放非主力合约
lss3 = []  # lss3存放股指合约
for i in lso:
    ls = api.query_quotes(ins_class="FUTURE", product_id=i, expired=False)
    # ls是全部上市合约
    ls10000 = [10000]
    lsn = ['']
    for x in ls:
        if api.get_quote(x).pre_open_interest > ls10000[0]:
            # 持仓量筛选
            ls10000[0] = api.get_quote(x).pre_open_interest
            lsn[0] = x
    if lsn[0] != '':
        lss.append(lsn[0])
for i in api.get_position().keys():
    if i not in lss:
        lss2.append(i)
for i in api.get_position().keys():
    if i[:7] == "CFFEX.I":
        lss2.remove(i)
now4 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
now5 = datetime.datetime.now()
print(now4, "-     主力合约计算完成，耗时", (now5 - now3).seconds, "秒")
print("")
print(lss)
print(lss2)
print("")
print(now4, "-     开始主程序")

# ------------------------关联性问题------------------------


# 对相关性进行分组，分为check0，check4，check6，check10,checkall
# 玉米淀粉类
ls0 = ['DCE.c', 'DCE.cs']
# 能源类
ls1 = ['CZCE.TA', 'INE.lu', 'INE.sc', 'SHFE.fu']
# 压榨类
ls2 = ['CZCE.RM', 'DCE.b', 'DCE.m']
# 橡胶类
ls3 = ['INE.nr', 'SHFE.ru']
# 成材类
ls4 = ['SHFE.hc', 'SHFE.rb']
# 油脂类
ls5 = ['DCE.p', 'DCE.y']
# 棉花类
ls6 = ['CZCE.CF', 'CZCE.CY']
# 贵金属类
ls7 = ['SHFE.ag', 'SHFE.au']
# 塑料类
ls8 = ['DCE.l', 'DCE.pp']
# 股指类
ls9 = ['CFFEX.IH', 'CFFEX.IF', 'CFFEX.IC']
# 国债类
ls10 = ['CFFEX.TS', 'CFFEX.TF', 'CFFEX.T']
# -----------------------------------------------------------------------------------------
# 不锈板块
ls11 = ['SHFE.ni', 'SHFE.ss']
# 白色板块
ls12 = ['CZCE.CF', 'CZCE.CY', 'CZCE.PF', 'INE.nr', 'SHFE.ru']
# 有色板块
ls13 = ['SHFE.al', 'SHFE.cu', 'SHFE.sn', 'SHFE.zn', 'INE.bc']
# 黑色板块
ls14 = ['SHFE.hc', 'SHFE.rb', 'DCE.i', 'DCE.j']
# 化工板块
ls15 = ['CZCE.MA', 'CZCE.TA', 'DCE.eb', 'DCE.eg', 'DCE.l', 'DCE.pp', 'DCE.v', 'INE.lu', 'INE.sc', 'SHFE.bu', 'SHFE.fu']
# 油脂板块
ls16 = ['CZCE.OI', 'CZCE.RM', 'DCE.b', 'DCE.m', 'DCE.p', 'DCE.y']

lss6 = [ls0, ls1, ls2, ls3, ls4, ls5, ls6, ls7, ls8, ls9, ls10]
lss10 = [ls11, ls12, ls13, ls14, ls15, ls16]
lssjc = ["不锈板块", "白色板块", "有色板块", "黑色板块", "化工板块", "油脂板块", ]
# 农产品组
ls17 = ['DCE.c', 'DCE.cs', 'CZCE.RM', 'DCE.b', 'DCE.m', 'DCE.a', 'DCE.p', 'DCE.y', 'CZCE.OI']


# 定义函数simple_symbol，从symbol中提取出品种+到期月,用于发微信
def simple_symbol(c):
    d = (c[c.find('.') + 1:])
    return d


# 定义js，用于开平仓后的存储信息
def js(symbol, vt, vf, last_price):
    with open(k3, "r", encoding="utf-8") as g:
        data = json.load(g)
        data[symbol] = [vt, vf, last_price,0,0]
    with open(k3, "w", encoding="utf-8") as h:
        json.dump(data, h)


# 定义jd，用于删除json文件中的特定字段
def jd(symbol):
    with open(k3, "r", encoding="utf-8") as g:
        data = json.load(g)
        data.pop(symbol)
    with open(k3, "w", encoding="utf-8") as h:
        json.dump(data, h)


# 定义mancang，确定是否符合海龟描述的满仓
def mancang(symbol):
    with open(k3, "r", encoding="utf-8") as g:
        data = json.load(g)
    with open(k3, "w", encoding="utf-8") as h:
        json.dump(data, h)
    if abs(check4(symbol)) == 4:
        print("%-13s-----【自身】已经满仓4" % symbol)
        data[symbol][3] = 1
    elif abs(check6(symbol)) == 6:
        print("%-13s-----【同类】已经满仓6" % symbol)
    elif abs(check10(symbol)) == 8:
        print("%-13s-----【板块】已经满仓8" % symbol)
    elif abs(check12(symbol)) == 10:
        print("%-13s-----【同向】已经满仓10" % symbol)



def duomeimancang(symbol):
    return check4(symbol) < 4 and check6(symbol) < 6 and check10(symbol) < 8 and check12(symbol) < 10

def kongmeimancang(symbol):
    return check4(symbol) > -4 and check6(symbol) > -6 and check10(symbol) > -8 and check12(symbol) > -10

def duomeimancang2(symbol):
    return check4(symbol) < 4 and check6(symbol) < 6 and check10(symbol) < 8

def kongmeimancang2(symbol):
    return check4(symbol) > -4 and check6(symbol) > -6 and check10(symbol) > -8


# 定义yichangri，检查大振幅行情
def yichangri(symbol):
    with open(k3, "r", encoding="utf-8") as g:
        data = json.load(g)
        data[symbol][4] = 1
    with open(k3, "w", encoding="utf-8") as h:
        json.dump(data, h)


# 找持仓，检测unit
def checktf(symbol):
    with open(k3, "r", encoding="utf-8") as f:
        data = json.load(f)
        if symbol in data:
            a = data[symbol][1]
        else:
            a = 0
    return round(a,0)


def check4(symbol):
    with open(k3, "r", encoding="utf-8") as f:
        data = json.load(f)
        if symbol in data:
            a = data[symbol][0]
        else:
            a = 0
    return round(a,0)


def check6(symbol):
    cl1 = []
    for i in lss6:
        for j in i:
            if symbol.translate(str.maketrans('', '', digits)) in j:
                for k in lss:
                    for l in i:
                        if l.translate(str.maketrans('', '', digits)) == k.translate(str.maketrans('', '', digits)):
                            cl1.append(k)
    a = 0
    for m in cl1:
        with open(k3, "r", encoding="utf-8") as f:
            data = json.load(f)
            if m in data:
                a = data[m][0] + a
    return round(a,0)


def check10(symbol):
    cl1 = []
    for i in lss10:
        for j in i:
            if symbol.translate(str.maketrans('', '', digits)) in j:
                for k in lss:
                    for l in i:
                        if l.translate(str.maketrans('', '', digits)) == k.translate(str.maketrans('', '', digits)):
                            cl1.append(k)
    a = 0
    for m in cl1:
        with open(k3, "r", encoding="utf-8") as f:
            data = json.load(f)
            if m in data:
                a = data[m][0] + a
    return round(a,0)


def check12(symbol):
    with open(k3, "r", encoding="utf-8") as f:
        data = json.load(f)
        a = 0
        for m in data.keys():
            if m in data:
                a = data[m][0] + a
    return round(a,0)


# 下面2个定义simple_symbol2和ps，用于语音报单功能
def simple_symbol2(c):
    c = c.translate(str.maketrans('', '', digits))
    d = (c[c.find('.') + 1:])
    return d


async def ps(symbol, caozuo):
    p = 'C:\\Users\\admin\\PycharmProjects\\untitled1\\demo\\voice\\'
    playsound(p + simple_symbol2(symbol) + ".wav")
    playsound(p + caozuo + ".wav")


# 定义adj，检查json文件和期货公司持仓差距，并进行主力换月
async def adj():
    dt = list(time.localtime())
    hour = dt[3]
    dic2 = api.get_position()  # 账号持仓信息
    keys = []
    if hour == 9:
        keys = list(dic2.keys())  # 持仓品种列表
    else:
        for i in list(dic2.keys()):
            if api.get_quote(i).trading_time['night']:
                keys.append(i)
    print("-----检查持仓和换月开始-----")
    print(lss)
    print("-----------------------------")
    with open(k3, "r", encoding="utf-8") as f:
        data0 = json.load(f)
    for p in data0.keys():
        if p not in list(dic2.keys()):
            print(p, "json有持仓", "期货公司无持仓")
        if (not duomeimancang2(p) and data0[p][0] > 0) or (not kongmeimancang2(p) and data0[p][0] < 0):
            mancang(p)
            # task_list.append(asyncio.create_task(ps(p, "mancang")))
    for p in keys:
        klines = api.get_kline_serial(p, 24 * 60 * 60, data_length=100)
        b = api.get_position(p).pos
        if b != 0 and p not in data0:
            print(p, "期货公司有持仓，json无持仓")
        if ATR(klines, k1)["atr"].iloc[-1] <= 0.5 * ATR(klines, k1)["tr"].iloc[-1] \
                and api.get_position(p).pos != 0:
            yichangri(p)
        if p not in lss and api.get_position(p).pos != 0:
            for q in lss:
                if q.translate(str.maketrans('', '', digits)) == p.translate(str.maketrans('', '', digits)):
                    po = data0[p][2]
                    pvt = data0[p][0]
                    pvf = data0[p][1]
                    if po != 0:
                        TargetPosTask(api, p).set_target_volume(0)
                        TargetPosTask(api, q).set_target_volume(b)
                        js(q, pvt, pvf, round((po * api.get_quote(q).pre_settlement / api.get_quote(p).pre_settlement), 4))
                        jd(p)
                        print(now4, "-    ", p, "换月了,换成了", q)
                        print(now4, "-     js文件中，价格变化为：", p, po, "变为", q,
                              '%.4f' % (po * api.get_quote(q).pre_settlement / api.get_quote(p).pre_settlement))
                        print(now4, "-     换月后的持仓为", pvt, "个unit")
                        task_list.append(asyncio.create_task(ps(p, "yicanghuanyue")))
                        # send_wx_msg("%s 换月了,换成了%s" % (simple_symbol(p),  simple_symbol(q)))
    print("-----检查持仓和换月已完成-----")
    for p in range(0, 6):
        a = 0
        print("-----------仓位报告-----------")
        print(lssjc[p], ":")
        for i in list(dic2.keys()):
            if (i.translate(str.maketrans('', '', digits)) in lss10[p]) and (i in data0.keys()):
                print("%-13s%2s" % (i, data0[i][0]))
                a = data0[i][0] + a
        print("%-11s%2s" % ("总计:", a))
    print("----------------------------")


# 定义主要交易策略turtle
async def turtle(symbol):
    global quote, account, klines
    quote = api.get_quote(symbol)
    account = api.get_account()
    klines = api.get_kline_serial(symbol, 24 * 60 * 60, data_length=100)
    k1 = 20
    k2 = 10
    k3 = "turtlemoni.json"
    k4 = 55
    k5 = 20
    if symbol.translate(str.maketrans('', '', digits)) in ls17:
        k1 = k4
        k2 = k5
    donchian_channel_high = max(klines.high[-k1 - 1:-1])  # 唐奇安通道上轨
    donchian_channel_low = min(klines.low[-k1 - 1:-1])  # 唐奇安通道下轨
    target_pos = TargetPosTask(api, symbol)
    x = target_pos._trade_chan._queue

    ma1 = MA(klines, k1)["ma"].iloc[-1]
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 持仓为0,开始找开仓机会
    while api.get_position(symbol).pos == 0:
        if api.is_changing(klines.iloc[-1], "datetime"):  # 如果产生新k线,则重新计算唐奇安通道及买卖单位
            donchian_channel_high = max(klines.high[-k1 - 1:-1])  # 唐奇安通道上轨
            donchian_channel_low = min(klines.low[-k1 - 1:-1])  # 唐奇安通道下轨
        if api.is_changing(quote, "last_price"):
            n = ATR(klines, k1)["atr"].iloc[-1]
            if math.isnan((ab * 0.01) / (quote.volume_multiple * n)):  # 检查是否是nan
                unit = 0
            else:
                unit = int((ab * 0.01) / (quote.volume_multiple * n))
            # print(now,donchian_channel_high,"%-13s |持仓:%3.0f |最新价:%9.2f |" % (symbol, api.get_position(symbol).pos, quote.last_price))

            with open(k3, "r", encoding="utf-8") as g:  # 开始读取json数据
                data0 = json.load(g)
                # if symbol == "SHFE.sn2106":
                #     print(quote.last_price - donchian_channel_high)
                #     print(symbol not in data0.keys())
                #     print(duomeimancang(symbol))
                if symbol not in data0.keys():
                    if 0.5 * n > (quote.last_price - donchian_channel_high) > 0 and account.risk_ratio <= 0.9:
                        # 当前价>唐奇安通道上轨，买入1个Unit；(持多仓)
                        if duomeimancang(symbol):
                            if unit == 0:
                                print(symbol, "已到开多标准，但资金不足一手", round((ab * 0.01) / (quote.volume_multiple * n), 2))
                                lss.remove(symbol)
                                task_list.append(asyncio.create_task(ps(symbol, "zijinbuzu")))
                                print(lss)
                            else:
                                print("----------开仓:多 %d 手 %s,止损 %.4f----------" % (
                                    unit, symbol, quote.last_price - 2 * n))
                                target_pos.set_target_volume(api.get_position(symbol).pos + unit)
                                if x != 0:
                                    # send_wx_msg("开仓: 多 %d 手 %s" % (unit, simple_symbol(symbol)))
                                    js(symbol, 1, 1, quote.last_price)
                                    task_list.append(asyncio.create_task(ps(symbol, "kaiduo")))
                    elif 0 < donchian_channel_low - quote.last_price < 0.5 * n and account.risk_ratio <= 0.9:
                        # 当前价<唐奇安通道下轨，卖出1个Unit；(持空仓)
                        if kongmeimancang(symbol):
                            if unit == 0:
                                print(symbol, "已到开空标准，但资金不足一手", round((ab * 0.01) / (quote.volume_multiple * n), 2))
                                lss.remove(symbol)
                                task_list.append(asyncio.create_task(ps(symbol, "zijinbuzu")))
                                print(lss)
                            else:
                                print("----------开仓:空 %d 手 %s,止损 %.4f----------" % (
                                    unit, symbol, quote.last_price + 2 * n))
                                target_pos.set_target_volume(api.get_position(symbol).pos - unit)
                                if x != 0:
                                    # send_wx_msg("开仓: 空 %d 手 %s" % (unit, simple_symbol(symbol)))
                                    js(symbol, -1, -1, quote.last_price)
                                    task_list.append(asyncio.create_task(ps(symbol, "kaikong")))

        break
    # 持仓不为0，找加仓机会，或者平仓
    while api.get_position(symbol).pos != 0:
        if api.is_changing(quote, "last_price"):  # 价格波动

            if api.get_position(symbol).pos > 0:  # 持多单
                with open(k3, "r", encoding="utf-8") as g:  # 开始读取json数据
                    data1 = json.load(g)
                if symbol not in data1.keys():
                    pass
                    # json中没有该symbol的记录，那就用持仓代替，防止json文件漏掉记录的
                    # data1[symbol] = [api.get_position(symbol).pos, api.get_position(symbol).open_price_long, 0]
                    # with open(k3, "w", encoding="utf-8") as g:
                    #     json.dump(data1, g)
                else:
                    data = data1[symbol]  # symbol的记录在data里，分别试[unit，price，mancang，yichangri]
                    # n = ATR(klines, k1)["atr"].iloc[-1]
                    # print(now,"%-13s |持仓:%3.0f |最新价:%9.2f |浮盈:%5.2f*n" % (symbol, data[0], quote.last_price,
                    #                                                   (quote.last_price - data[1]) / n))
                    # 加仓策略: 如果是多仓且行情最新价在上次开仓价的基础上又上涨了1N，就再加一个Unit的多仓,并且风险度在设定范围内(以防爆仓)
                    # 加仓距离实际为1,2,1,1
                    if data[1] == 1:
                        length = 2.0
                    else:
                        length = 1.0
                    #  如果满足加仓条件
                    if quote.last_price >= data[2] + int(length) * ATR(klines, k1)["atr"].iloc[-1]:
                        n = ATR(klines, k1)["atr"].iloc[-1]
                        if account.risk_ratio <= 0.9 and duomeimancang(symbol):
                            unit = int((ab * 0.01) / (quote.volume_multiple * n))
                            add = 1
                        else:
                            unit = 0
                            add = 0
                        if abs(checktf(symbol)) < 4:
                            vf = 1
                        else:
                            vf = 0
                        # 检查是否满仓
                        if symbol not in lss2:
                            target_pos.set_target_volume(api.get_position(symbol).pos + unit)
                            print("----------加仓:多 %d 手 %s,止损 %.4f----------" % (unit, symbol, quote.last_price - 2 * n))
                            # send_wx_msg("加仓：多 %d 手 %s" % (unit, simple_symbol(symbol)))
                            task_list.append(asyncio.create_task(ps(symbol, "jiaduo")))
                            # 记录加仓信息
                            with open(k3, "r", encoding="utf-8") as f:
                                js(symbol, data[0] + add, data[1] + vf, quote.last_price)
                                # 加仓完毕后，再检查是否满仓，如果满仓在json中记录
                                if not duomeimancang(symbol):
                                    mancang(symbol)
                                    task_list.append(asyncio.create_task(ps(symbol, "mancang")))
                    # 止损策略: 如果是多仓且行情最新价在上次开仓价的基础上又下跌了2N，就卖出全部头寸止损
                    elif quote.last_price <= data[2] - 2 * ATR(klines, k1)["atr"].iloc[-1]:
                        target_pos.set_target_volume(0)
                        print("----------止损: 平%s全部头寸----------" % symbol)
                        jd(symbol)
                        task_list.append(asyncio.create_task(ps(symbol, "zhisun")))
                        # send_wx_msg("止损: 平%s全部头寸" % simple_symbol(symbol))
                    # 止盈策略: 如果是多仓且行情最新价跌破了10日唐奇安通道的下轨，,或者满仓时上穿均线，就清空所有头寸结束策略,离场
                    elif quote.last_price <= min(klines.low[-k2 - 1:-1]) or \
                            (quote.last_price <= ma1 and data[3] == 1 and data[4] == 1):
                        target_pos.set_target_volume(0)
                        print("----------止盈: 平%s全部头寸----------" % symbol)
                        # json中清除symbol数据
                        jd(symbol)
                        task_list.append(asyncio.create_task(ps(symbol, "zhiying")))
                        # send_wx_msg("止盈: 平%s全部头寸" % simple_symbol(symbol))
            elif api.get_position(symbol).pos < 0:  # 持空单
                with open(k3, "r", encoding="utf-8") as g:
                    data2 = json.load(g)
                if symbol not in data2.keys():
                    pass
                    # data2[symbol] = [api.get_position(symbol).pos, api.get_position(symbol).open_price_short]
                    # with open(k3, "w", encoding="utf-8") as g:
                    #     json.dump(data2, g)
                else:
                    data = data2[symbol]
                    # n= ATR(klines, k1)["atr"].iloc[-1]
                    # print(now,"%-13s |持仓:%3.0f |最新价:%9.2f |浮盈:%5.2f*n" % (symbol, data[0], quote.last_price,
                    #                                                   (data[1] - quote.last_price) / n))
                    # 加仓策略: 如果是空仓且行情最新价在上一次开仓价的基础上又下跌了1N，就再加一个Unit的空仓,并且风险度在设定范围内(以防爆仓)
                    # 加仓距离实际为1,2,1,1
                    if data[1] == -1:
                        length = 2.0
                    else:
                        length = 1.0
                    if quote.last_price <= data[2] - int(length) * ATR(klines, k1)["atr"].iloc[-1]:
                        n = ATR(klines, k1)["atr"].iloc[-1]
                        if account.risk_ratio <= 0.9 and kongmeimancang(symbol):
                            unit = int((ab * 0.01) / (quote.volume_multiple * n))
                            add = 1
                        else:
                            unit = 0
                            add = 0
                        if abs(checktf(symbol)) < 4:
                            vf = 1
                        else:
                            vf = 0
                        if symbol not in lss2:
                            target_pos.set_target_volume(api.get_position(symbol).pos - unit)
                            print("----------加仓:空 %d 手 %s,止损 %.4f----------" % (unit, symbol, quote.last_price + 2 * n))
                            # send_wx_msg("加仓：空 %d 手 %s" % (unit, simple_symbol(symbol)))
                            task_list.append(asyncio.create_task(ps(symbol, "jiakong")))
                            with open(k3, "r", encoding="utf-8") as f:
                                js(symbol, data[0] - add, data[1] - vf, quote.last_price)
                                if not kongmeimancang(symbol):
                                    mancang(symbol)
                                    task_list.append(asyncio.create_task(ps(symbol, "mancang")))
                    # 止损策略: 如果是空仓且行情最新价在上一次开仓均价的基础上又上涨了2N，就平仓止损
                    elif quote.last_price >= data[2] + 2 * ATR(klines, k1)["atr"].iloc[-1]:
                        target_pos.set_target_volume(0)
                        print("----------止损: 平%s全部头寸----------" % symbol)
                        jd(symbol)
                        task_list.append(asyncio.create_task(ps(symbol, "zhisun")))
                        # send_wx_msg("止损:平%s全部头寸" % simple_symbol(symbol))
                        # 止盈策略: 如果是空仓且行情最新价升破了10日唐奇安通道的上轨,或者满仓时上穿均线，就清空所有头寸结束策略,离场
                    elif quote.last_price >= max(klines.high[-k2 - 1:-1]) or \
                            (quote.last_price >= ma1 and data[3] == 1 and data[4] == 1):
                        target_pos.set_target_volume(0)
                        print("----------止盈: 平%s全部头寸----------" % symbol)
                        jd(symbol)
                        task_list.append(asyncio.create_task(ps(symbol, "zhiying")))
                        # send_wx_msg("止盈: 平%s全部头寸" % simple_symbol(symbol))
        break


# ------------------------循环------------------------
c = 0
task_list = []
while True:
    api.wait_update()
    for x in lss+lss2:
        api.create_task(turtle(x))
    dt = list(time.localtime())
    hour = dt[3]
    minute = dt[4]
    if ((hour == 9 and minute == 5) or (hour == 21 and minute == 5)) and c == 0:
        c = 1
        api.create_task(adj())
        lss2 = []
