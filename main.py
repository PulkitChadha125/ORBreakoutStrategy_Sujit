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
                'Symbol': row['Symbol'],
                'Stoploss':float(row['Stoploss']),
                'EntryBuffer': float(row['EntryBuffer']),
                "lotsize": int(row['lotsize']),
                "Target1": float(row['Target1']),
                "Target2": float(row['Target2']),
                "Target3": float(row['Target3']),
                "Target4": float(row['Target4']),
                "Target1Lotsize": int(row['Target1Lotsize']),
                "Target2Lotsize": int(row['Target2Lotsize']),
                "Target3Lotsize": int(row['Target3Lotsize']),
                "Target4Lotsize": int(row['Target4Lotsize']),
                "BreakEven": float(row['BreakEven']),
                "ReEntry": int(row['ReEntry']),
                "Expiery": row['Expiery'],
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
                "remaining":None,
            }
            result_dict[row['Symbol']] = symbol_dict
        print("result_dict: ", result_dict)
    except Exception as e:
        print("Error happened in fetching symbol", str(e))

def get_api_credentials():
    credentials = {}
    delete_file_contents("OrderLogs.txt")
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
                    bigdata=AngelIntegration.get_historical_data(symbol=params['Symbol'],
                                                                          timeframe="FIFTEEN_MINUTE",
                                                                       token=get_token(params['Symbol']),segment="NFO")
                    Big_last_three_rows = bigdata.tail(3)
                    Bigrow1 = Big_last_three_rows.iloc[2]
                    fifteenclose=Bigrow1['close']
                    print("Bigrow1: ",Bigrow1)
                    smalldata=AngelIntegration.get_historical_data(symbol=params['Symbol'],
                                                                          timeframe="FIVE_MINUTE",
                                                                       token=get_token(params['Symbol']),segment="NFO")

                    Small_last_three_rows = smalldata.tail(3)
                    Smallrow1 = Small_last_three_rows.iloc[1]
                    fiveclose = Smallrow1['close']
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

                ltp=AngelIntegration.get_ltp(segment="NFO",symbol=params['Symbol'],token=get_token(params['Symbol']))
                if ltp>=params["BuyPrice"]  and params["BuyPrice"] >0 and ltp>0 and (params["TradeType"] is None or params["TradeType"] == "BUYPE") :

                    if params["TradeType"] == "BUYPE":
                        orderlog = (
                            f"{timestamp} Signal Switch to BUY CALL  @ {ltp}, remaining qty exit = {params['remaining']}")
                        write_to_order_logs(orderlog)
                        print(orderlog)

                    params["TradeType"]= "BUYCE"
                    params["underlyinfltp"]=ltp
                    params["tgt1"] = ltp+ params["Target1"]
                    params["tgt2"] = ltp + params["Target2"]
                    params["tgt3"] = ltp + params["Target3"]
                    params["tgt4"] = ltp + params["Target4"]
                    params["sl"] = ltp - params["Stoploss"]
                    params["brkevn"] = ltp + params["BreakEven"]
                    if params["StrikeSelectionType"] == "ATM":
                        strike = custom_round(int(float(ltp)), params['BaseSymbol'])
                        callstrike = strike
                    if params["StrikeSelectionType"] == "ITM":
                        strike = custom_round(int(float(ltp)), params['BaseSymbol'])
                        callstrike = int(strike) - int(params["StrikeDistance"])
                    if params["StrikeSelectionType"] == "OTM":
                        strike = custom_round(int(float(ltp)), params['BaseSymbol'])
                        callstrike = int(strike) + int(params["StrikeDistance"])
                    params["remaining"]=params['lotsize']
                    orderlog=(f"{timestamp} Buy order executed call side @ {callstrike} @ {ltp} @ lotsize={params['lotsize']}, tp1={params['tgt1']},"
                              f"tp2={params['tgt2']},tp3={params['tgt3']},tp4={params['tgt4']},sl={params['sl']},brkeven={params['brkevn']}")
                    write_to_order_logs(orderlog)
                    print(orderlog)

                if ltp<=params["SellPrice"]  and params["SellPrice"] >0 and ltp>0 and (params["TradeType"] is None or params["TradeType"] == "BUYCE"):
                    if params["TradeType"] == "BUYCE":
                        orderlog = (
                            f"{timestamp} Signal Switch to BUY PUT  @ {ltp}, remaining qty exit = {params['remaining']}")
                        write_to_order_logs(orderlog)
                        print(orderlog)

                    params["TradeType"]= "BUYPE"
                    params["underlyinfltp"] = ltp
                    params["tgt1"] = ltp - params["Target1"]
                    params["tgt2"] = ltp - params["Target2"]
                    params["tgt3"] = ltp - params["Target3"]
                    params["tgt4"] = ltp - params["Target4"]
                    params["sl"] = ltp + params["Stoploss"]
                    params["brkevn"] = ltp - params["BreakEven"]
                    if params["StrikeSelectionType"] == "ATM":
                        strike = custom_round(int(float(ltp)), params['BaseSymbol'])
                        putstrike = strike
                    if params["StrikeSelectionType"] == "ITM":
                        strike = custom_round(int(float(ltp)), params['BaseSymbol'])
                        putstrike = int(strike) + int(params["StrikeDistance"])
                    if params["StrikeSelectionType"] == "OTM":
                        strike = custom_round(int(float(ltp)), params['BaseSymbol'])
                        putstrike = int(strike) - int(params["StrikeDistance"])
                    params["remaining"]=params['lotsize']
                    orderlog = (
                        f"{timestamp} Buy order executed put side @ {putstrike} @ {ltp} @ lotsize={params['lotsize']}, tp1={params['tgt1']},"
                        f"tp2={params['tgt2']},tp3={params['tgt3']},tp4={params['tgt4']},sl={params['sl']},brkeven={params['brkevn']}")
                    write_to_order_logs(orderlog)
                    print(orderlog)

                if params["TradeType"]== "BUYCE":
                    if ltp>=params["tgt1"] and params["tgt1"]>0:
                        params["tgt1"]=0
                        params["remaining"]= params['remaining']-params['Target1Lotsize']
                        orderlog = (f"{timestamp} Target 1 executed BUY CALL @ {ltp}, partial qty exit = {params['Target1Lotsize']}")
                        write_to_order_logs(orderlog)
                        print(orderlog)
                    if ltp>=params["tgt2"] and params["tgt2"]>0:
                        params["tgt2"] = 0
                        params["remaining"] = params['remaining'] - params['Target2Lotsize']
                        orderlog = (f"{timestamp} Target 2 executed BUY CALL  @ {ltp}, partial qty exit = {params['Target2Lotsize']}")
                        write_to_order_logs(orderlog)
                        print(orderlog)
                    if ltp>=params["tgt3"] and params["tgt3"]>0:
                        params["tgt3"] = 0
                        params["remaining"] = params['remaining'] - params['Target3Lotsize']
                        orderlog = (f"{timestamp} Target 3 executed BUY CALL  @ {ltp}, partial qty exit = {params['Target3Lotsize']}")
                        write_to_order_logs(orderlog)
                        print(orderlog)
                    if ltp>=params["tgt4"] and params["tgt4"]>0:
                        params["tgt4"] = 0
                        params["remaining"] = 0
                        orderlog = (f"{timestamp} Target 4 executed BUY CALL  @ {ltp}, partial qty exit = {params['Target4Lotsize']}")
                        write_to_order_logs(orderlog)
                        print(orderlog)
                    if ltp>=params["brkevn"] and params["brkevn"]>0:
                        params["sl"]=params["underlyinfltp"]
                        params["brkevn"] = 0
                        orderlog = (f"{timestamp} Breakeven executed BUY CALL  @ {ltp}, Sl moved to cost= {params['sl']}")
                        write_to_order_logs(orderlog)
                        print(orderlog)

                if params["TradeType"]== "BUYPE":
                    if ltp<=params["tgt1"] and params["tgt1"]>0:
                        params["tgt1"]=0
                        params["remaining"] = params['remaining'] - params['Target1Lotsize']
                        orderlog = (f"{timestamp} Target 1 executed BUY PUT@ {ltp}, partial qty exit = {params['Target1Lotsize']}")
                        write_to_order_logs(orderlog)
                        print(orderlog)
                    if ltp<=params["tgt2"] and params["tgt2"]>0:
                        params["tgt2"] = 0
                        params["remaining"] = params['remaining'] - params['Target2Lotsize']
                        orderlog = (f"{timestamp} Target 2 executed BUY PUT  @ {ltp}, partial qty exit = {params['Target2Lotsize']}")
                        write_to_order_logs(orderlog)
                        print(orderlog)
                    if ltp<=params["tgt3"] and params["tgt3"]>0:
                        params["tgt3"] = 0
                        params["remaining"] = params['remaining'] - params['Target3Lotsize']
                        orderlog = (f"{timestamp} Target 3 executed BUY PUT  @ {ltp}, partial qty exit = {params['Target3Lotsize']}")
                        write_to_order_logs(orderlog)
                        print(orderlog)
                    if ltp<=params["tgt4"] and params["tgt4"]>0:
                        params["tgt4"] = 0
                        params["remaining"] =0
                        orderlog = (f"{timestamp} Target 4 executed BUY PUT  @ {ltp}, partial qty exit = {params['Target4Lotsize']}")
                        write_to_order_logs(orderlog)
                        print(orderlog)
                    if ltp<=params["brkevn"] and params["brkevn"]>0:
                        params["sl"]=params["underlyinfltp"]
                        params["brkevn"] = 0
                        orderlog = (f"{timestamp} Breakeven executed BUY PUT  @ {ltp}, Sl moved to cost= {params['sl']}")
                        write_to_order_logs(orderlog)
                        print(orderlog)


    except Exception as e:
        print("Error happened in Main strategy loop: ", str(e))
        traceback.print_exc()

while True:
    main_strategy()
    time.sleep(1)
