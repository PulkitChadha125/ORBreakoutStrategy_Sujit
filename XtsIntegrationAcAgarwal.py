import pandas as pd
from datetime import datetime, timedelta
from Connect import XTSConnect
import time
import traceback


#======= xts integration ===================
xtskey="42fcf9710a97b2e7e05944"
xtssecret="Ykxs172$I9"
xtssource="WEBAPI"
clientid="KJS58"

xt=None

def login():
    global xt
    xt=XTSConnect(xtskey,xtssecret,xtssource)
    responce= xt.interactive_login()




def get_mastercontract_xts():
    global xt
    # Define the expected column names
    column_names = [
        "ExchangeSegment","ExchangeInstrumentID","InstrumentType","Name","Description","Series","NameWithSeries",
        "InstrumentID","PriceBand.High","PriceBand.Low","FreezeQty","TickSize", "LotSize","Multiplier","UnderlyingInstrumentId", "UnderlyingIndexName","ContractExpiration", "StrikePrice", "OptionType","DisplayName",
        "PriceNumerator", "PriceDenominator","DetailedDescription"
    ]
    exchangesegment = [xt.EXCHANGE_NSEFO]
    res = xt.get_master(exchangeSegmentList=exchangesegment)
    if 'result' not in res:
        raise ValueError("The response does not contain the 'result' key")
    with open("master.txt", "w") as file1:
        file1.write(res['result'])
    try:
        masterdf = pd.read_csv(
            'master.txt',
            sep='|',
            low_memory=True,
            names=column_names,
            skiprows=1,  # Skip the header row if it exists
            on_bad_lines='skip'
        )
    except pd.errors.ParserError as e:
        print(f"Error parsing data: {e}")
        return
    masterdf['ContractExpiration'] = pd.to_datetime(masterdf['ContractExpiration'], errors='coerce')
    masterdf['ContractExpiration'] = masterdf['ContractExpiration'].apply(lambda x: x.date() if pd.notnull(x) else None)
    masterdf.to_csv('master.csv', index=False)
    print("Master contract data has been saved to 'master.csv'")

def get_symbol_orderdetail(expiery,strike,basesymbol,contract=3):
    global xt
    masterdf=pd.read_csv("master.csv")
    contact=masterdf[(masterdf.Name == basesymbol) &
             (masterdf.StrikePrice == strike) &
             (masterdf.ContractExpiration == expiery) &
             (masterdf.Series == "OPTIDX") &
             (masterdf.OptionType == contract)]
    exchange_instrument_id = contact['ExchangeInstrumentID'].values[0]
    return exchange_instrument_id


def Buyorderplacement(lotsize=10,expiery="2024-05-30",strike=25050,basesymbol="NIFTY",contract=3):
    global clientid, xt
    response=xt.place_order(
        exchangeSegment=xt.EXCHANGE_NSEFO,
        exchangeInstrumentID=int(get_symbol_orderdetail(expiery=expiery,strike=strike,basesymbol=basesymbol,contract=contract)),
        productType=xt.PRODUCT_MIS,
        orderType=xt.ORDER_TYPE_MARKET,
        orderSide=xt.TRANSACTION_TYPE_BUY,
        timeInForce=xt.VALIDITY_DAY,
        disclosedQuantity=0,
        orderQuantity=lotsize,
        limitPrice=0,
        stopPrice=0,
        orderUniqueIdentifier="454845",
        clientID=clientid)
    print("Place Order: ", response)

def Sellorderplacement(lotsize=10,expiery="2024-05-30",strike=25050,basesymbol="NIFTY",contract=3):
    global clientid, xt
    response=xt.place_order(
        exchangeSegment=xt.EXCHANGE_NSEFO,
        exchangeInstrumentID=int(get_symbol_orderdetail(expiery=expiery,strike=strike,basesymbol=basesymbol,contract=contract)),
        productType=xt.PRODUCT_MIS,
        orderType=xt.ORDER_TYPE_MARKET,
        orderSide=xt.TRANSACTION_TYPE_SELL,
        timeInForce=xt.VALIDITY_DAY,
        disclosedQuantity=0,
        orderQuantity=lotsize,
        limitPrice=0,
        stopPrice=0,
        orderUniqueIdentifier="454845",
        clientID=clientid)
    print("Place Order: ", response)



def Shortorderplacement(lotsize=10,expiery="2024-05-30",strike=25050,basesymbol="NIFTY",contract=3):
    global clientid, xt
    response=xt.place_order(
        exchangeSegment=xt.EXCHANGE_NSEFO,
        exchangeInstrumentID=int(get_symbol_orderdetail(expiery=expiery,strike=strike,basesymbol=basesymbol,contract=contract)),
        productType=xt.PRODUCT_MIS,
        orderType=xt.ORDER_TYPE_MARKET,
        orderSide=xt.TRANSACTION_TYPE_SELL,
        timeInForce=xt.VALIDITY_DAY,
        disclosedQuantity=0,
        orderQuantity=lotsize,
        limitPrice=0,
        stopPrice=0,
        orderUniqueIdentifier="454845",
        clientID=clientid)
    print("Place Order: ", response)
def Coverorderplacement(lotsize=10,expiery="2024-05-30",strike=25050,basesymbol="NIFTY",contract=3):
    global clientid, xt
    response=xt.place_order(
        exchangeSegment=xt.EXCHANGE_NSEFO,
        exchangeInstrumentID=int(get_symbol_orderdetail(expiery=expiery,strike=strike,basesymbol=basesymbol,contract=contract)),
        productType=xt.PRODUCT_MIS,
        orderType=xt.ORDER_TYPE_MARKET,
        orderSide=xt.TRANSACTION_TYPE_BUY,
        timeInForce=xt.VALIDITY_DAY,
        disclosedQuantity=0,
        orderQuantity=lotsize,
        limitPrice=0,
        stopPrice=0,
        orderUniqueIdentifier="454845",
        clientID=clientid)
    print("Place Order: ", response)
