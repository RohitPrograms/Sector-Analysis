import matplotlib.pyplot as plt

# Creates a Bar Chart to depict the YTD Performance of Each of the 11 Sectors
def CreateBarChart(sector_performances):

    copy = dict.copy(sector_performances)
    sector_names = list(copy.keys())
    Y_Axis = list(copy.values())

    X_Axis = list()

    for sector in sector_names:

        temp = sector.replace(" ", "\n")
        X_Axis.append(temp)

    plt.figure(figsize=(16,8))
    plt.bar(X_Axis, Y_Axis, color ='maroon', width = 0.4)
 
    plt.xlabel("Sectors")
    plt.ylabel("YTD Performance")
    plt.axhline(y = 0, color = 'black')
    plt.title("YTD Performance of Each Major Sector")
    plt.show()

# Creates a Box and Whisker plot to show the distribution of P/E ratios for a given sector.
def CreateBoxPlot(name, data):
    
    plt.boxplot(data, vert = False)
    title_str = "PE Ratios for SP500 Stocks in the " + name + " Sector" 
    plt.title(title_str)
    plt.yticks(color='w')
    plt.show()
    
