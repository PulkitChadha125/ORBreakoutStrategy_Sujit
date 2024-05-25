import pandas as pd
import AngelIntegration,XtsIntegrationAcAgarwal
from datetime import datetime, timedelta
import time
import traceback

# xts integration call
XtsIntegrationAcAgarwal.login()
XtsIntegrationAcAgarwal.get_mastercontract_xts()

def custom_round(price, symbol):
    rounded_price = None
    if symbol == "NIFTY":
        last_two_digits = price % 100
        if last_two_digits < 25:
            rounded_price = (price // 100) * 100
        elif last_two_digits < 75:
            rounded_price = (price // 100) * 100 + 50
        else:
            rounded_price = (price // 100 + 1) * 100
            return rounded_price

    elif symbol == "BANKNIFTY":
        last_two_digits = price % 100
        if last_two_digits < 50:
            rounded_price = (price // 100) * 100
        else:
            rounded_price = (price // 100 + 1) * 100
        return rounded_price

    else:
        pass

    return rounded_price
def write_to_order_logs(message):
    with open('OrderLog.txt', 'a') as file:  # Open the file in append mode
        file.write(message + '\n')


def delete_file_contents(file_name):
    try:
        # Open the file in write mode, which truncates it (deletes contents)
        with open(file_name, 'w') as file:
            file.truncate(0)
        print(f"Contents of {file_name} have been deleted.")
    except FileNotFoundError:
        print(f"File {file_name} not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

result_dict={}


def get_user_settings():
    global result_dict
    # Symbol,lotsize,Stoploss,Target1,Target2,Target3,Target4,Target1Lotsize,Target2Lotsize,Target3Lotsize,Target4Lotsize,BreakEven,ReEntry
    try:
        csv_path = 'TradeSettings.csv'
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()
        result_dict = {}
        # Symbol,EMA1,EMA2,EMA3,EMA4,lotsize,Stoploss,Target,Tsl
        for index, row in df.iterrows():
            # Create a nested dictionary for each symbol
            symbol_dict = {
                'Symbol': row['Symbol'],'Stoploss':float(row['Stoploss']),'EntryBuffer': float(row['EntryBuffer']),
                "lotsize": int(row['lotsize']),"Target1": float(row['Target1']),"Target2": float(row['Target2']),
                "Target3": float(row['Target3']),"Target4": float(row['Target4']),"Target1Lotsize": int(row['Target1Lotsize']),
                "Target2Lotsize": int(row['Target2Lotsize']),"Target3Lotsize": int(row['Target3Lotsize']),"Target4Lotsize": int(row['Target4Lotsize']),
                "BreakEven": float(row['BreakEven']),"ReEntry": int(row['ReEntry']),"Expiery": str(row['Expiery']),
                "BaseSymbol":str(row['BaseSymbol']),"strike":None,
                "runonce":False,
                "BuyPrice": None,
                "SellPrice": None,
                "TradeType":None,
                "tgt1":None,
                "tgt2": None,
                "tgt3": None,
                "tgt4": None,
                "sl": None,
                "brkevn": None,
                "optionSymbol":None,
                "optionSymbolToken": None,
                "optionSymbolltp": None,
                "underlyinfltp":None,
                "remaining":None,"slexecuted":False,"targetexecuted":False,"TradeExecuted":None,
                "runtime": datetime.now(),"previousclose":None,"count":0,"TradeExpiery":str(row['Expiery']),"tradeltp":None
            }
            result_dict[row['Symbol']] = symbol_dict
        print("result_dict: ", result_dict)
    except Exception as e:
        print("Error happened in fetching symbol", str(e))

def get_api_credentials():
    credentials = {}
    delete_file_contents("OrderLog.txt")
    try:
        df = pd.read_csv('Credentials.csv')
        for index, row in df.iterrows():
            title = row['Title']
            value = row['Value']
            credentials[title] = value
    except pd.errors.EmptyDataError:
        print("The CSV file is empty or has no data.")
    except FileNotFoundError:
        print("The CSV file was not found.")
    except Exception as e:
        print("An error occurred while reading the CSV file:", str(e))

    return credentials

get_user_settings()
credentials_dict = get_api_credentials()
api_key=credentials_dict.get('apikey')
username=credentials_dict.get('USERNAME')
pwd=credentials_dict.get('pin')
totp_string=credentials_dict.get('totp_string')
AngelIntegration.login(api_key=api_key,username=username,pwd=pwd,totp_string=totp_string)
AngelIntegration.symbolmpping()
def round_down_to_interval(dt, interval_minutes):
    remainder = dt.minute % interval_minutes
    minutes_to_current_boundary = remainder
    rounded_dt = dt - timedelta(minutes=minutes_to_current_boundary)
    rounded_dt = rounded_dt.replace(second=0, microsecond=0)
    return rounded_dt
def get_token(symbol):
    df= pd.read_csv("Instrument.csv")
    row = df.loc[df['symbol'] == symbol]
    if not row.empty:
        token = row.iloc[0]['token']
        return token

def main_strategy():
    global result_dict
    try:
        for symbol, params in result_dict.items():
            symbol_value = params['Symbol']
            timestamp = datetime.now()
            timestamp = timestamp.strftime("%d/%m/%Y %H:%M:%S")
            if isinstance(symbol_value, str):
                if params['runonce']==False:
                    params['runonce'] = True
                    print(params["Expiery"])
                    date_obj = datetime.strptime(params["Expiery"], "%d-%b-%y")
                    formatted_date = date_obj.strftime("%Y-%m-%d")
                    params["Expiery"] = formatted_date
                    bigdata=AngelIntegration.get_historical_data(symbol=params['Symbol'],
                                                                          timeframe="FIFTEEN_MINUTE",
                                                                       token=get_token(params['Symbol']),segment="NFO")
                    Big_last_three_rows = bigdata.tail(3)
                    Bigrow1 = Big_last_three_rows.iloc[2]
                    fifteenclose=Bigrow1['close']
                    print(Big_last_three_rows)
                    print("Bigrow1: ",Bigrow1)

                    smalldata=AngelIntegration.get_historical_data(symbol=params['Symbol'],
                                                                          timeframe="FIVE_MINUTE",
                                                                       token=get_token(params['Symbol']),segment="NFO")

                    Small_last_three_rows = smalldata.tail(3)
                    Smallrow1 = Small_last_three_rows.iloc[1]
                    fiveclose = Smallrow1['close']
                    print(Small_last_three_rows)
                    print("Smallrow1: ", Smallrow1)

                    if fifteenclose>fiveclose:
                        params["BuyPrice"]= fifteenclose + params["EntryBuffer"]
                        params["SellPrice"]= fiveclose - params["EntryBuffer"]
                        orderlog = (
                            f"{timestamp} Range created Buy Price={params['BuyPrice']} , sell price {params['SellPrice']}")
                        write_to_order_logs(orderlog)
                        print(orderlog)

                    else:
                        params["BuyPrice"] =  fiveclose + params["EntryBuffer"]
                        params["SellPrice"] = fifteenclose - params["EntryBuffer"]
                        orderlog = (
                            f"{timestamp} Range created Buy Price={params['BuyPrice']} , sell price {params['SellPrice']}")
                        write_to_order_logs(orderlog)
                        print(orderlog)


                if datetime.now() >= params["runtime"]:
                    smalldata = AngelIntegration.get_historical_data(symbol=params['Symbol'],
                                                                     timeframe="FIVE_MINUTE",
                                                                     token=get_token(params['Symbol']), segment="NFO")
                    Small_last_three_rows = smalldata.tail(3)
                    Smallrow1 = Small_last_three_rows.iloc[1]
                    params['previousclose'] = Smallrow1['close']
                    next_specific_part_time = datetime.now() + timedelta(seconds=5 * 60)
                    next_specific_part_time = round_down_to_interval(next_specific_part_time,5)
                    print("Next datafetch time = ", next_specific_part_time)
                    params['runtime'] = next_specific_part_time


                if params['optionSymbol'] is not None:
                    params["optionSymbolltp"] = AngelIntegration.get_ltp(segment="NFO", symbol=params['optionSymbol'],
                                                                         token=get_token(params['optionSymbol']))
                ltp=AngelIntegration.get_ltp(segment="NFO", symbol=params['Symbol'],
                                                                         token=get_token(params['Symbol']))


                # reseting price in range


                if (
                        (params["slexecuted"] == True or params["targetexecuted"] == True)  and
                        (params["TradeType"] == "BUYPE" or params["TradeType"] == "BUYCE" ) and
                        params["TradeExecuted"] == False and
                        params['previousclose']<params["BuyPrice"] and
                        params['previousclose']>params["SellPrice"]
                ):
                    params["TradeType"] = None

                # reentry code BUYPE i have doubts

                if (
                        params["count"] <= params["ReEntry"] and
                        params["slexecuted"] == True and
                        ltp < params["SellPrice"] and
                        params["TradeType"] == "BUYPE" and
                        params["optionSymbolltp"] >= params["tradeltp"]
                ):
                    params["count"] = params["count"] + 1
                    params["TradeType"] = "BUYPE"
                    params["underlyinfltp"] = ltp
                    params["TradeExecuted"] = True
                    params["slexecuted"] = False
                    params["targetexecuted"] =False

                    if params["StrikeSelectionType"] == "ATM":
                        strike = custom_round(int(float(ltp)), params['BaseSymbol'])
                        putstrike = strike
                        params["strike"] = putstrike
                    if params["StrikeSelectionType"] == "ITM":
                        strike = custom_round(int(float(ltp)), params['BaseSymbol'])
                        putstrike = int(strike) + int(params["StrikeDistance"])
                        params["strike"] = putstrike
                    if params["StrikeSelectionType"] == "OTM":
                        strike = custom_round(int(float(ltp)), params['BaseSymbol'])
                        putstrike = int(strike) - int(params["StrikeDistance"])
                        params["strike"] = putstrike
                    params["remaining"] = params['lotsize']
                    date_obj = datetime.strptime(params["TradeExpiery"], "%d-%b-%y")
                    formatted_date = date_obj.strftime("%d%b%y").upper()
                    print(formatted_date)
                    params["optionSymbol"] = f"{params['BaseSymbol']}{formatted_date}{params['strike']}CE"
                    print(params["optionSymbol"])
                    params["optionSymbolltp"] = AngelIntegration.get_ltp(segment="NFO", symbol=params['optionSymbol'],
                                                                         token=get_token(params['optionSymbol']))
                    params["tradeltp"] = params["optionSymbolltp"]
                    params["tgt1"] = params["optionSymbolltp"] - params["Target1"]
                    params["tgt2"] = params["optionSymbolltp"] - params["Target2"]
                    params["tgt3"] = params["optionSymbolltp"] - params["Target3"]
                    params["tgt4"] = params["optionSymbolltp"] - params["Target4"]
                    params["sl"] = params["optionSymbolltp"] + params["Stoploss"]
                    params["brkevn"] = params["optionSymbolltp"] - params["BreakEven"]
                    # XtsIntegrationAcAgarwal.Buyorderplacement(lotsize=params['lotsize'], expiery=params["Expiery"],
                    #                                           strike=params["strike"],
                    #                                           basesymbol=params['BaseSymbol'], contract=4)
                    orderlog = (
                        f"{timestamp} Buy order executed PUT side @ {params['BaseSymbol']}@ {ltp} ,CONTRACT= {params['optionSymbol']} "
                        f"@{params['optionSymbolltp']} @ lotsize={params['lotsize']}, tp1={params['tgt1']},"
                        f"tp2={params['tgt2']},tp3={params['tgt3']},tp4={params['tgt4']},sl={params['sl']},brkeven={params['brkevn']}")
                    write_to_order_logs(orderlog)
                    print(orderlog)
                # reentry code BUYCE

                if (
                        params["count"] <= params["ReEntry"] and
                        params["slexecuted"] == True and ltp>params["BuyPrice"]  and
                        params["TradeType"] == "BUYCE" and
                        params["optionSymbolltp"]>=params["tradeltp"]
                ):

                    params["TradeType"] = "BUYCE"
                    params["underlyinfltp"] = ltp
                    params["TradeExecuted"] = True
                    params["slexecuted"] = False
                    params["targetexecuted"] = False
                    params["count"] = params["count"] + 1
                    if params["StrikeSelectionType"] == "ATM":
                        strike = custom_round(int(float(ltp)), params['BaseSymbol'])
                        callstrike = strike
                        params["strike"] = callstrike
                    if params["StrikeSelectionType"] == "ITM":
                        strike = custom_round(int(float(ltp)), params['BaseSymbol'])
                        callstrike = int(strike) - int(params["StrikeDistance"])
                        params["strike"] = callstrike
                    if params["StrikeSelectionType"] == "OTM":
                        strike = custom_round(int(float(ltp)), params['BaseSymbol'])
                        callstrike = int(strike) + int(params["StrikeDistance"])
                        params["strike"] = callstrike

                    date_obj = datetime.strptime(params["TradeExpiery"], "%d-%b-%y")
                    formatted_date = date_obj.strftime("%d%b%y").upper()
                    print(formatted_date)
                    params["optionSymbol"] = f"{params['BaseSymbol']}{formatted_date}{params['strike']}CE"
                    print(params["optionSymbol"])
                    params["remaining"] = params['lotsize']
                    params["optionSymbolltp"] = AngelIntegration.get_ltp(segment="NFO", symbol=params['optionSymbol'],
                                                                         token=get_token(params['optionSymbol']))
                    params["tradeltp"] = params["optionSymbolltp"]
                    params["tgt1"] = params["optionSymbolltp"] + params["Target1"]
                    params["tgt2"] = params["optionSymbolltp"] + params["Target2"]
                    params["tgt3"] = params["optionSymbolltp"] + params["Target3"]
                    params["tgt4"] = params["optionSymbolltp"] + params["Target4"]
                    params["sl"] = params["optionSymbolltp"] - params["Stoploss"]
                    params["brkevn"] = params["optionSymbolltp"] + params["BreakEven"]
                    # XtsIntegrationAcAgarwal.Buyorderplacement(lotsize=params['lotsize'], expiery=params["Expiery"],
                    #                                           strike=params["strike"],
                    #                                           basesymbol=params['BaseSymbol'], contract=3)

                    orderlog = (
                        f"{timestamp} Buy order executed call side @ {params['BaseSymbol']}@ {ltp} ,CONTRACT= {params['optionSymbol']}"
                        f" @{params['optionSymbolltp']} @ lotsize={params['lotsize']}, tp1={params['tgt1']},"
                        f"tp2={params['tgt2']},tp3={params['tgt3']},tp4={params['tgt4']},sl={params['sl']},brkeven={params['brkevn']}")
                    write_to_order_logs(orderlog)
                    print(orderlog)

                # if (
                #         params["slexecuted"] == True and ltp<params["BuyPrice"] and  ltp>params["BuyPrice"]  and params["TradeType"] == "BUYCE"
                # ):
                #     params["TradeType"] =None

                #  mainentry

                if (
                        params["count"]<=params["ReEntry"] and
                        params['previousclose']>=params["BuyPrice"]  and
                        params["BuyPrice"] >0 and params['previousclose']>0 and
                        (params["TradeType"] is None or params["TradeType"] == "BUYPE")
                ):

                    if params["TradeType"] == "BUYPE":
                        # XtsIntegrationAcAgarwal.Sellorderplacement(lotsize=params['remaining'],
                        #                                            expiery=params["Expiery"],
                        #                                            strike=params["strike"],
                        #                                            basesymbol=params['BaseSymbol'], contract=4)
                        orderlog = (
                            f"{timestamp} Signal Switch to BUY CALL  @ {ltp}, remaining qty exit = {params['remaining']}")
                        write_to_order_logs(orderlog)
                        print(orderlog)

                    params["TradeType"]= "BUYCE"
                    params["TradeExecuted"]= True
                    params["underlyinfltp"]=ltp
                    params["count"]=params["count"]+1
                    if params["StrikeSelectionType"] == "ATM":
                        strike = custom_round(int(float(ltp)), params['BaseSymbol'])
                        callstrike = strike
                        params["strike"]=callstrike
                    if params["StrikeSelectionType"] == "ITM":
                        strike = custom_round(int(float(ltp)), params['BaseSymbol'])
                        callstrike = int(strike) - int(params["StrikeDistance"])
                        params["strike"] = callstrike
                    if params["StrikeSelectionType"] == "OTM":
                        strike = custom_round(int(float(ltp)), params['BaseSymbol'])
                        callstrike = int(strike) + int(params["StrikeDistance"])
                        params["strike"] = callstrike
                    params["remaining"] = params['lotsize']
                    date_obj = datetime.strptime(params["TradeExpiery"], "%d-%b-%y")
                    formatted_date = date_obj.strftime("%d%b%y").upper()
                    print(formatted_date)
                    params["optionSymbol"]=f"{params['BaseSymbol']}{formatted_date}{params['strike']}CE"
                    print(params["optionSymbol"])
                    params["remaining"]=params['lotsize']
                    params["optionSymbolltp"] = AngelIntegration.get_ltp(segment="NFO", symbol=params['optionSymbol'],
                                                                         token=get_token(params['optionSymbol']))
                    params["tradeltp"] = params["optionSymbolltp"]
                    params["tgt1"] = params["optionSymbolltp"] + params["Target1"]
                    params["tgt2"] = params["optionSymbolltp"] + params["Target2"]
                    params["tgt3"] = params["optionSymbolltp"] + params["Target3"]
                    params["tgt4"] = params["optionSymbolltp"] + params["Target4"]
                    params["sl"] = params["optionSymbolltp"] - params["Stoploss"]
                    params["brkevn"] = params["optionSymbolltp"] + params["BreakEven"]
                    # XtsIntegrationAcAgarwal.Buyorderplacement(lotsize=params['lotsize'], expiery=params["Expiery"],
                    #                                           strike=params["strike"],
                    #                                           basesymbol=params['BaseSymbol'], contract=3)

                    orderlog=(f"{timestamp} Buy order executed call side @ {params['BaseSymbol']}@ {ltp} ,CONTRACT= {params['optionSymbol']}"
                              f" @{params['optionSymbolltp']} @ lotsize={params['lotsize']}, tp1={params['tgt1']},"
                              f"tp2={params['tgt2']},tp3={params['tgt3']},tp4={params['tgt4']},sl={params['sl']},brkeven={params['brkevn']}")
                    write_to_order_logs(orderlog)
                    print(orderlog)

                if (
                        params["count"]<=params["ReEntry"] and
                        params['previousclose']<=params["SellPrice"]  and
                        params["SellPrice"] >0 and params['previousclose']>0 and
                        (params["TradeType"] is None or params["TradeType"] == "BUYCE")
                ):
                    if params["TradeType"] == "BUYCE":
                        # XtsIntegrationAcAgarwal.Sellorderplacement(lotsize=params['remaining'],
                        #                                            expiery=params["Expiery"],
                        #                                            strike=params["strike"],
                        #                                            basesymbol=params['BaseSymbol'], contract=4)
                        orderlog = (
                            f"{timestamp} Signal Switch to BUY PUT  @ {ltp}, remaining qty exit = {params['remaining']}")
                        write_to_order_logs(orderlog)
                        print(orderlog)
                    params["count"] = params["count"] + 1
                    params["TradeType"]= "BUYPE"
                    params["underlyinfltp"] = ltp
                    params["TradeExecuted"] = True

                    if params["StrikeSelectionType"] == "ATM":
                        strike = custom_round(int(float(ltp)), params['BaseSymbol'])
                        putstrike = strike
                        params["strike"] = putstrike
                    if params["StrikeSelectionType"] == "ITM":
                        strike = custom_round(int(float(ltp)), params['BaseSymbol'])
                        putstrike = int(strike) + int(params["StrikeDistance"])
                        params["strike"] = putstrike
                    if params["StrikeSelectionType"] == "OTM":
                        strike = custom_round(int(float(ltp)), params['BaseSymbol'])
                        putstrike = int(strike) - int(params["StrikeDistance"])
                        params["strike"] = putstrike
                    params["remaining"]=params['lotsize']
                    date_obj = datetime.strptime(params["TradeExpiery"], "%d-%b-%y")
                    formatted_date = date_obj.strftime("%d%b%y").upper()
                    print(formatted_date)
                    params["optionSymbol"] = f"{params['BaseSymbol']}{formatted_date}{params['strike']}CE"
                    print(params["optionSymbol"])
                    params["optionSymbolltp"] = AngelIntegration.get_ltp(segment="NFO", symbol=params['optionSymbol'],
                                                                         token=get_token(params['optionSymbol']))
                    params["tradeltp"] = params["optionSymbolltp"]
                    params["tgt1"] = params["optionSymbolltp"] - params["Target1"]
                    params["tgt2"] = params["optionSymbolltp"] - params["Target2"]
                    params["tgt3"] = params["optionSymbolltp"] - params["Target3"]
                    params["tgt4"] = params["optionSymbolltp"] - params["Target4"]
                    params["sl"] = params["optionSymbolltp"] + params["Stoploss"]
                    params["brkevn"] = params["optionSymbolltp"] - params["BreakEven"]
                    # XtsIntegrationAcAgarwal.Buyorderplacement(lotsize=params['lotsize'],expiery=params["Expiery"],strike=params["strike"],
                    #                                           basesymbol=params['BaseSymbol'],contract=4)
                    orderlog = (
                        f"{timestamp} Buy order executed PUT side @ {params['BaseSymbol']}@ {ltp} ,CONTRACT= {params['optionSymbol']} "
                        f"@{params['optionSymbolltp']} @ lotsize={params['lotsize']}, tp1={params['tgt1']},"
                        f"tp2={params['tgt2']},tp3={params['tgt3']},tp4={params['tgt4']},sl={params['sl']},brkeven={params['brkevn']}")
                    write_to_order_logs(orderlog)
                    print(orderlog)

                if params["TradeType"]== "BUYCE" and params['optionSymbol']  is not None and params["optionSymbolltp"]is not None:
                    if params["optionSymbolltp"]>=params["tgt1"] and params["tgt1"]>0:
                        params["tgt1"]=0
                        params["remaining"]= params['remaining']-params['Target1Lotsize']
                        # XtsIntegrationAcAgarwal.Sellorderplacement(lotsize=params['Target1Lotsize'], expiery=params["Expiery"],
                        #                                           strike=params["strike"],
                        #                                           basesymbol=params['BaseSymbol'], contract=3)
                        orderlog = (f"{timestamp} Target 1 executed BUY CALL @ {ltp}, partial qty exit = {params['Target1Lotsize']}")
                        write_to_order_logs(orderlog)
                        print(orderlog)
                    if params["optionSymbolltp"]>=params["tgt2"] and params["tgt2"]>0:
                        params["tgt2"] = 0
                        params["remaining"] = params['remaining'] - params['Target2Lotsize']
                        # XtsIntegrationAcAgarwal.Sellorderplacement(lotsize=params['Target2Lotsize'],
                        #                                            expiery=params["Expiery"],
                        #                                            strike=params["strike"],
                        #                                            basesymbol=params['BaseSymbol'], contract=3)
                        orderlog = (f"{timestamp} Target 2 executed BUY CALL  @ {ltp}, partial qty exit = {params['Target2Lotsize']}")
                        write_to_order_logs(orderlog)
                        print(orderlog)
                    if params["optionSymbolltp"]>=params["tgt3"] and params["tgt3"]>0:
                        params["tgt3"] = 0
                        params["remaining"] = params['remaining'] - params['Target3Lotsize']
                        # XtsIntegrationAcAgarwal.Sellorderplacement(lotsize=params['Target3Lotsize'],
                        #                                            expiery=params["Expiery"],
                        #                                            strike=params["strike"],
                        #                                            basesymbol=params['BaseSymbol'], contract=3)
                        orderlog = (f"{timestamp} Target 3 executed BUY CALL  @ {ltp}, partial qty exit = {params['Target3Lotsize']}")
                        write_to_order_logs(orderlog)
                        print(orderlog)
                    if params["optionSymbolltp"]>=params["tgt4"] and params["tgt4"]>0:
                        params["tgt4"] = 0
                        params["remaining"] = 0
                        params["targetexecuted"] = True
                        params["TradeExecuted"] = False
                        # XtsIntegrationAcAgarwal.Sellorderplacement(lotsize=params['Target4Lotsize'],
                        #                                            expiery=params["Expiery"],
                        #                                            strike=params["strike"],
                        #                                            basesymbol=params['BaseSymbol'], contract=3)
                        orderlog = (f"{timestamp} Target 4 executed BUY CALL  @ {ltp}, partial qty exit = {params['Target4Lotsize']}")
                        write_to_order_logs(orderlog)
                        print(orderlog)
                    if params["optionSymbolltp"]>=params["brkevn"] and params["brkevn"]>0:
                        params["sl"]=params["tradeltp"]
                        params["brkevn"] = 0
                        orderlog = (f"{timestamp} Breakeven executed BUY CALL  @ {ltp}, Sl moved to cost= {params['sl']}")
                        write_to_order_logs(orderlog)
                        print(orderlog)

                    if params["optionSymbolltp"]<=params["sl"] and params["sl"]>0:
                        params["sl"]=0

                        params["slexecuted"]= True
                        params["TradeExecuted"] = False
                        # XtsIntegrationAcAgarwal.Sellorderplacement(lotsize=params['remaining'],
                        #                                            expiery=params["Expiery"],
                        #                                            strike=params["strike"],
                        #                                            basesymbol=params['BaseSymbol'], contract=3)
                        orderlog = (f"{timestamp} stoploss executed BUY CALL  @{ltp}")
                        write_to_order_logs(orderlog)
                        print(orderlog)
                        params["remaining"] = 0

                if params["TradeType"]== "BUYPE" and params['optionSymbol']  is not None and params["optionSymbolltp"]is not None:
                    if params["optionSymbolltp"]<=params["tgt1"] and params["tgt1"]>0:
                        params["tgt1"]=0
                        params["remaining"] = params['remaining'] - params['Target1Lotsize']
                        # XtsIntegrationAcAgarwal.Sellorderplacement(lotsize=params['Target1Lotsize'],
                        #                                            expiery=params["Expiery"],
                        #                                            strike=params["strike"],
                        #                                            basesymbol=params['BaseSymbol'], contract=4)
                        orderlog = (f"{timestamp} Target 1 executed BUY PUT@ {ltp}, partial qty exit = {params['Target1Lotsize']}")
                        write_to_order_logs(orderlog)
                        print(orderlog)
                    if params["optionSymbolltp"]<=params["tgt2"] and params["tgt2"]>0:
                        params["tgt2"] = 0
                        params["remaining"] = params['remaining'] - params['Target2Lotsize']
                        # XtsIntegrationAcAgarwal.Sellorderplacement(lotsize=params['Target2Lotsize'],
                        #                                            expiery=params["Expiery"],
                        #                                            strike=params["strike"],
                        #                                            basesymbol=params['BaseSymbol'], contract=4)
                        orderlog = (f"{timestamp} Target 2 executed BUY PUT  @ {ltp}, partial qty exit = {params['Target2Lotsize']}")
                        write_to_order_logs(orderlog)
                        print(orderlog)
                    if params["optionSymbolltp"]<=params["tgt3"] and params["tgt3"]>0:
                        params["tgt3"] = 0
                        params["remaining"] = params['remaining'] - params['Target3Lotsize']
                        # XtsIntegrationAcAgarwal.Sellorderplacement(lotsize=params['Target3Lotsize'],
                        #                                            expiery=params["Expiery"],
                        #                                            strike=params["strike"],
                        #                                            basesymbol=params['BaseSymbol'], contract=4)
                        orderlog = (f"{timestamp} Target 3 executed BUY PUT  @ {ltp}, partial qty exit = {params['Target3Lotsize']}")
                        write_to_order_logs(orderlog)
                        print(orderlog)
                    if params["optionSymbolltp"]<=params["tgt4"] and params["tgt4"]>0:
                        params["tgt4"] = 0
                        params["remaining"] =0
                        params["targetexecuted"] = True
                        params["TradeExecuted"] = False
                        # XtsIntegrationAcAgarwal.Sellorderplacement(lotsize=params['Target4Lotsize'],
                        #                                            expiery=params["Expiery"],
                        #                                            strike=params["strike"],
                        #                                            basesymbol=params['BaseSymbol'], contract=4)
                        orderlog = (f"{timestamp} Target 4 executed BUY PUT  @ {ltp}, partial qty exit = {params['Target4Lotsize']}")
                        write_to_order_logs(orderlog)
                        print(orderlog)
                    if params["optionSymbolltp"]<=params["brkevn"] and params["brkevn"]>0:
                        params["sl"]=params["tradeltp"]
                        params["brkevn"] = 0
                        orderlog = (f"{timestamp} Breakeven executed BUY PUT  @ {ltp}, Sl moved to cost= {params['sl']}")
                        write_to_order_logs(orderlog)
                        print(orderlog)
                    if params["optionSymbolltp"]>=params["sl"] and params["sl"]>0:
                        params["sl"]=0

                        params["slexecuted"] = True
                        params["TradeExecuted"] = False
                        # XtsIntegrationAcAgarwal.Sellorderplacement(lotsize=params['remaining'],
                        #                                            expiery=params["Expiery"],
                        #                                            strike=params["strike"],
                        #                                            basesymbol=params['BaseSymbol'], contract=4)
                        orderlog = (f"{timestamp} stoploss executed BUY put  @{ltp}")
                        write_to_order_logs(orderlog)
                        print(orderlog)
                        params["remaining"] = 0


    except Exception as e:
        print("Error happened in Main strategy loop: ", str(e))
        traceback.print_exc()

while True:
    main_strategy()
    time.sleep(1)
