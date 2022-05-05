import pandas as pd
import random as r
import math
import datetime
from datetime import date
import requests
import cryptocompare as cc


class Option:
	def __init__(self, price, strike, premium, period, amount, otype):
	    self.price = price
	    self.strike = strike
	    self.premium = premium
	    self.period = period
	    self.amount = amount
	    self.type = otype
    
# settlementFeeShare is the percent of the premium that is subtracted from the total premium price. The settlementFee is the part of the premium that is distributed among the HEGIC staking participants. The value is currently 20% but is possibly subject to change between versions.
settlementFeeShare = 20

# IVDecimals is representative of the token decimals
IVDecimals = pow(10,18)

# base is used in the calculation of IVRate. In order to find the variables base and constant I went under the assumption that the price of ETH had an impact on the implied volatility rate. When ETH price was higher the implied volatility rate was higher. I then found the percent difference in ETH price between the two different times and it came out to being that a 10.25% difference in eth price 

# base is used in the calculation of IVRate. It is the price of eth that we use to calculate the IVbase.
base = 3011

# IVBase is the implied volatility rate when the price of ETH is 3011. At price 3011, the premium for a 1 ETH option was 127. Which is why 127 is a parameter in the function.
IVbase = get_ActualIVRate(127)

# const represents the percent change in implied volatility rate generated by a 1% change in 
const = 0.02043605

# types holds the two different types of options
types = ["Call", "Put"]    





  
# @notice Used for calculating the percentage difference between two elements
# @param the bigger element
# @param the smaller element
# @return (c-e)/e

def percent(c,e):
    sub = c - e
    sub = sub / e
    return sub

# @notice A simple function to use requests.post to make the API call.
# @param input parameters for the API
# @return a json object that contains all the ETH info
def run_query(query):  # A simple function to use requests.post to make the API call.
    headers = {'X-API-KEY': 'BQYYquuv9iE4tUkIy1vo381YcGGrK5y2'}
    request = requests.post('https://graphql.bitquery.io/',
                            json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception('Query failed and return code is {}.      {}'.format(request.status_code,
                                                                             query))

# @return historical ETH prices and date times
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

# @return the current ETH price
def get_eth_price():
    cc.cryptocompare._set_api_key_parameter('#')
    p = cc.get_price('ETH',currency='USD')
    return p['ETH']['USD']
 
# @notice get the current actual Implied volatility rate
# @param the current premium we need to pay for one ETH call option
# @return the current actual implied volatility rate
def get_ActualIVRate(premium):
    p1 = math.sqrt(604800) / (IVDecimals)
    p2 = (20 * math.sqrt(604800)) / (IVDecimals*100)
    p = p1 - p2
    IVRate = premium / p
    # adjust iv rate
    return IVRate
    
# @notice get the Implied volatility rate on a specific date
# @param the price of eth on a specific date
# @return the implied volatility rate on a specific date
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

# @notice calculate the premium for an option
# @param amount: amount of eth you would like to buy or sell 
# @param period: period of the option
# @return the premium of an option
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
    
# @notice generates an option based on the input price
# @param strike price / current price for the option
# @return an Option object with fields: price,  strike price, premium, period, amount, option type
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
    

# @notice tracks the profit and loss for the given period
# @param none
# @return a dataframe with eth price, date, and breakeven differences
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
    if option.type == "Call":
        term['Difference'] = term['Price'].apply(lambda x: x - b)
        return term
    else:
        term['Difference'] = term['Price'].apply(lambda x: b - x)
        return term

# @notice calculate the breakeven of an option
# @param option object
# @return breakeven 
def breakeven(option):
    if option.type == "Call":
        return option.strike + (option.premium/option.amount)
    else:
        return option.strike - (option.premium/option.amount)



int main():
	results = tracker()
	print(results.where(results.loc[:,'Difference'] > 0).dropna())
	

