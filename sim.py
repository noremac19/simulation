import pandas as pd
import random as r
import math
import datetime
from datetime import date
import requests
import cryptocompare as cc


# THEY WANT TO BUY A FIXED AMOUNT OF HEGIC WHICH IS 100 TOKENS FOR RN
# NEED A SPECIFIC DATE
# CHOOSE A SANDOM START POINT AND DISTINGUISH A DURATION/EXPIRY TIME


###############
#Scenario #1##
#############
class Option:
	def __init__(self, price, strike, premium, period, amount, otype):
	    self.price = price
	    self.strike = strike
	    self.premium = premium
	    self.period = period
	    self.amount = amount
	    self.type = otype
    

settlementFeeShare = 20
IVDecimals = pow(10,18)
base = 3011
IVbase = get_ActualIVRate(127)
const = 0.02043605

types = ["Call", "Put"]    

# Track the difference of a strike price and actual hegic token price across
# the time of expiry period
# Figure out
# Maybe try to see when the optimal time would be to carryout the call option


def percent(c,e):
    sub = c - e
    sub = sub / e
    return sub

def run_query(query):  # A simple function to use requests.post to make the API call.
    headers = {'X-API-KEY': 'BQYYquuv9iE4tUkIy1vo381YcGGrK5y2'}
    request = requests.post('https://graphql.bitquery.io/',
                            json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception('Query failed and return code is {}.      {}'.format(request.status_code,
                                                                             query))


def getHistoricalETH():
    part1 = """{
      ethereum {
        dexTrades(
        protocol: {is: "Uniswap v2"}
        baseCurrency: {is: "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"} 
        quoteCurrency: {is: "0x6b175474e89094c44da98b954eedeac495271d0f"}
        date: {since: "2022-01-01"}
        ) {

          quotePrice
          timeInterval {
            hour(count: 1)
          }
          
        }
      }
    }
    
    """
        

    query = part1 
    result = run_query(query)
    temp = pd.json_normalize(result['data']['ethereum']['dexTrades'])
    temp.columns = ['Price', 'Date.Time']
    return temp


def get_eth_price():
    cc.cryptocompare._set_api_key_parameter('a44fde92b0792cb721cdf11fdb772c92ba529257d9a7a73688d0a87dc10fb4f7')
    p = cc.get_price('ETH',currency='USD')
    return p['ETH']['USD']
 

def get_ActualIVRate(premium):
    p1 = math.sqrt(604800) / (IVDecimals)
    p2 = (20 * math.sqrt(604800)) / (IVDecimals*100)
    p = p1 - p2
    IVRate = premium / p
    # adjust iv rate
    return IVRate
    
def get_IVRate(ethPrice):
    pr = percent(base, ethPrice) * 100
    if ethPrice < base:
        diff = (const * pr) * IVbase
        IVRate = IVbase - diff
        return IVRate
    elif ethPrice > base:
        add = (const * pr) * IVbase
        IVRate = IVbase + add
        return IVRate
    else:   
        return base


def premiumATM(amount,period):
    period = period * 24 * 60 * 60
    period = math.sqrt(period)
    eth = get_eth_price()
    v = get_IVRate(eth)
    premium = (amount * v * period) / IVDecimals
    settlement = (settlementFeeShare * amount * v * period) / (IVDecimals * 100)
    total = premium - settlement
    #total = math.ceil(total)
    return total
    

def optionGeneratorATM(p):
    price = p
    strike = p
    # amount = r.randint(1, 10)
    # period = r.randint(7, 45)
    amount = 1
    period = 7
    pre = premiumATM(amount,period)
    x = r.randint(0,1)
    otype = types[x]
    return Option(p,p,pre,period,amount,otype)
    

def tracker():
    i = r.randint(2600,len(getHistoricalETH())-168)
    p = data.iloc[[i]]['Price'].values[0]
    option = optionGeneratorATM(p)
    b = breakeven(option)
    
    print("ETH Price: ", option.price)
    print("Strike Price: ", option.strike)
    print("Option Type: ", option.type)
    print("Period: ", option.period)
    print("Premium: ", option.premium)
    print("Breakeven: ", b)
    
    # gets prices during the period
    t = data.iloc[[i]].values[0]
    start = t[1].split(" ")[1].split(":")[0]
    rows = int(start) + (24 * option.period)
    j = i + rows
    
    term = data.iloc[i:j,:]
    #term = term.reset_index(drop=True)
    term['Difference'] = term['Price'].apply(lambda x: x - b)
    
    return term


def breakeven(option):
    if option.type == "Call":
        return option.strike + option.premium
    else:
        return option.strike - option.premium



int main():
	results = tracker()
	print(results.where(results.loc[:,'Difference'] > 0).dropna())
	