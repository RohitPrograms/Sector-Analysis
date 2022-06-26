from alpha_vantage.fundamentaldata import FundamentalData
from alpha_vantage.sectorperformance import SectorPerformances
import pandas as pd
import numpy as np
import time
import GraphHelpers as gh

# Variables Needed to interact with the AlphaVantage Stock Data API
API_KEY = "YEM6SLKLWMUGJQB6"
fd = FundamentalData(API_KEY, "pandas")
sp = SectorPerformances(API_KEY, "pandas")

# A CSV file containing the ticker symbols for each equity in the S&P 500, and their respective sector.
SP500_Stocks = pd.read_csv("SP500Stocks.csv")


def GetSectorPerformances():

# Returns a dictionary where the keys are the names of the different sectors, and the associated value
    # is their YTD Performance expressed as a decimal.

    data, metadata = sp.get_sector()
    ytd_performances = data['Rank F: Year-to-Date (YTD) Performance']
    sectors = ytd_performances.index

    sector_performances_dict = dict()
    for i in range(len(sectors)):
        sector_performances_dict.update({sectors[i] : ytd_performances[i]})
    
    return sector_performances_dict

def GetSectorStocks():

# Returns a dictionary where the keys are the names of the different sectors, and the associated value 
    # is a list of S&P 500 equities within that sector.

    sector_stocks_dict = dict()

    for index, stock in SP500_Stocks.iterrows():
        
        if(stock['Sector'] not in sector_stocks_dict.keys()):
            sector_stocks_dict.update({stock['Sector'] : [stock['Symbol']]})
        
        else:
            temp = sector_stocks_dict[stock['Sector']]
            temp.append(stock['Symbol'])
            sector_stocks_dict.update({stock['Sector'] : temp})
        
    return sector_stocks_dict


def EvaluateSectors(sector_performances, n):

# Returns a list of lists in the following format:
    # [GrowingSectors, CollapsingSectors]

    # Growing Sectors is a list of the top n growing sectors
        # Growing Sector: A sector with a YTD performance above 0

    # CollapsingSectors is a list of the top n collapsing sectors
        # Collapsing Sector: A sector with a YTD performance below 0

    copy = dict.copy(sector_performances)
    key_list = list(copy.keys())
    val_list = list(copy.values())

    sorted_vals = val_list.copy()
    sorted_vals.sort()

    TopVals = sorted_vals[len(sorted_vals) - n : len(sorted_vals)]
    BottomVals = sorted_vals[0 : n]

    GrowingSectors = list()
    CollapsingSectors = list()

    for val in TopVals:
        if val > 0:
            sector = key_list[val_list.index(val)]
            GrowingSectors.append(sector)
    
    for val in BottomVals:
        if val < 0:
            sector = key_list[val_list.index(val)]
            CollapsingSectors.append(sector)


    return [GrowingSectors, CollapsingSectors]



def EvaluateStocks(sector_evaluation, sector_stocks):

# Examines the P/E Ratios for a given set equities within a sector, and constructs a box-and-whisker plot

    # If the equities were part of a growing sector, we would be looking for stocks with unusually low P/E ratios
        # (The low outliers of the given box-and-Whisker plot).

    # If the equities were part of a collapsing Sector, we would be looking for stocks with unusually high P/E ratios
        # (The high outliers of the given box-and-whisker plot).

# Returns a set of dictionaries, which has the following format:
    # [All_Overvalued_Stocks, All_Undervalued_Stocks]

    # the dictionary All_Overvalued_Stocks has the following format:
        # {sector name : overvalued stocks within said sector} 

    # the dictionary All_Undervalued_Stocks has the following format:
        # {sector name : undervalued stocks within said sector} 

    GrowingSectors = sector_evaluation[0]
    CollapsingSectors = sector_evaluation[1]
    sector_stocks_copy = dict.copy(sector_stocks)

    All_Undervalued_Stocks = dict()
    All_Overvalued_Stocks = dict()

    for sector in GrowingSectors:

        print("\nChecking for Undervalued Stocks in the", sector, "Sector")
        stock_list = list(sector_stocks_copy[sector])
        PERatios = list()
        
        for stock in stock_list:

            try:
                data, metadata = fd.get_company_overview(stock)
                PERatio = data['PERatio'][0]
                print("Adding", PERatio, "for", stock)

                if PERatio != 'None':
                    PERatios.append(float(PERatio))
                
                else:
                    PERatios.append(PERatio)
                
            except:
                print("Adding None for", stock)
                PERatios.append('None')
            
            time.sleep(15)

        PERatios_Copy = list()

        for PERatio in PERatios:

            if PERatio != "None":

                PERatios_Copy.append(PERatio)
        
        gh.CreateBoxPlot(sector, PERatios_Copy)

        q1 = np.percentile(PERatios_Copy, 25)
        q3 = np.percentile(PERatios_Copy, 75)

        Undervalued_Stocks = list()

        for PERatio in PERatios_Copy:

            if PERatio < (q1 - (1.5 * (q3 - q1))):
                index = PERatios.index(PERatio)
                stock = stock_list[index]
                Undervalued_Stocks.append(stock)
        
        All_Undervalued_Stocks.update({sector : Undervalued_Stocks})

    for sector in CollapsingSectors:

        print("Checking for Overvalued Stocks in the", sector, "Sector")
        stock_list = list(sector_stocks_copy[sector])
        PERatios = list()
        
        for stock in stock_list:

            try:
                data, metadata = fd.get_company_overview(stock)
                PERatio = data['PERatio'][0]
                print("Adding", PERatio, "for", stock)

                if PERatio != 'None':
                    PERatios.append(float(PERatio))
                
                else:
                    PERatios.append(PERatio)
                
            except:
                print("Adding None for", stock)
                PERatios.append('None')
            
            time.sleep(15)

        PERatios_Copy = list()

        for PERatio in PERatios:

            if PERatio != "None":

                PERatios_Copy.append(PERatio)
            
        gh.CreateBoxPlot(sector, PERatios_Copy)
        
        q1 = np.percentile(PERatios_Copy, 25)
        q3 = np.percentile(PERatios_Copy, 75)

        Overvalued_Stocks = list()

        for PERatio in PERatios_Copy:

            if PERatio > (q3 + (1.5 * (q3 - q1))):
                index = PERatios.index(PERatio)
                stock = stock_list[index]
                Overvalued_Stocks.append(stock)
        
        All_Overvalued_Stocks.update({sector : Overvalued_Stocks})
    
    return [All_Overvalued_Stocks, All_Undervalued_Stocks]



# Main 
sector_performances = GetSectorPerformances()
gh.CreateBarChart(sector_performances)

sector_stocks = GetSectorStocks()

sector_evaluation = EvaluateSectors(sector_performances, 3)
GrowingSectors = sector_evaluation[0]
CollapsingSectors = sector_evaluation[1]
print("Growing Sectors:", GrowingSectors)
print("Collapsing Sectors:", CollapsingSectors)


Stock_Basket = EvaluateStocks(sector_evaluation, sector_stocks)
All_Overvalued_Stocks = Stock_Basket[0]
All_Undervalued_Stocks = Stock_Basket[1]
print("Overvalued:", All_Overvalued_Stocks)
print("Undervalued:", All_Undervalued_Stocks)

