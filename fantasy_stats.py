# Team Rocket Fantasy Sports Statistics Module
# Team Rocket: Gleb, Alex, Bill
import pandas
from matplotlib import pyplot


def plot_bar_graph():
    data_frame = pandas.DataFrame({'wins': [7, 11, 3, 2],
                                   'losses': [5, 1, 9, 10]},
                                  index=['Seahawks', 'Rams', 'Cardinals', '49ers'])
    data_frame.plot.bar()
    pyplot.show()
    return


def main():
    plot_bar_graph()
    return


if __name__ == '__main__':
    main()
