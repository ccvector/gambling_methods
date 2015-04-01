from __future__ import print_function, division
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import random
import os

def color():
    return ['b', 'r', 'g', 'y', 'b', 'c', 'm']

def plot(output_name):
    plt.show()
    plt.ylabel('Account Value')
    plt.xlabel('Wager Count')
    plt.axhline(color='r')
    plt.savefig(output_name)
    plt.clf()

def float_range(start, stop, step):
    r = start
    while r < stop:
        yield r
        r += step

def roll_dice():
    roll = random.randint(1, 100)
    if roll == 100:
        return False
    elif roll <= 50:
        return False
    elif 50 < roll < 100:
        return True

def save(initial_funds, funds, saving):
    if funds > initial_funds:
        saving += funds - initial_funds
        funds = initial_funds
    return funds, saving

def refill(initial_funds, funds, saving):
    if funds < initial_funds:
        diff = initial_funds - funds
        if saving >= diff:
            funds = initial_funds
            saving -= diff
        else:
            funds += saving
            saving = 0
    return funds, saving

def bettor(strategy, initial_wager, plays, n, pcolor=None):
    funds = 100
    wager = initial_wager
    x_wager = []
    y_funds = []
    initial_funds = funds
    is_broke = False
    saving = 0
    straight_loss = 0
    worst = 0
    result = '*' * 70 + '\n'
    result += 'strategy: {}\n\n'.format(strategy)
    result += '{:>10}{:>10}{:>10}{:>10}\n'.format('round', 'wager', 'funds', 'saving')
    for i in range(plays):
        if funds < wager:
            wager = funds
        result += '{:>10}{:>10.3f}{:>10.3f}{:>10.3f}{:>10d}\n'.format(i + 1, wager, funds, saving, straight_loss)
        if roll_dice():
            funds += wager

            straight_loss = 0
            if strategy == 'martingale' or strategy == 'martingale_safe':
                wager = initial_wager
            elif strategy == 'dalembert':
                if wager > initial_wager:
                    wager -= initial_wager * n
        else:
            funds -= wager
            straight_loss += 1
            worst = max(worst, straight_loss)
            if strategy == 'martingale' or strategy == 'martingale_safe':
                wager *= n
            elif strategy == 'dalembert':
                wager += initial_wager * n

        x_wager.append(i)
        if strategy == 'martingale_safe':
            y_funds.append(funds + saving)
            if (i + 1) % 100 == 0:
                t = save(initial_funds, funds, saving)
                funds, saving = t
        else:
            y_funds.append(funds)
        if funds == 0:
            if strategy == 'martingale_safe':
                if saving == 0:
                    is_broke = True
            else:
                is_broke = True
            break
    plt.plot(x_wager, y_funds, pcolor)
    if strategy == 'martingale_safe':
        funds += saving
    is_profit = True if funds > initial_funds else False
    profit_percent = (funds - initial_funds) / initial_funds
    result += '\nprofit_percent: {}\n\n'.format(profit_percent)
    print(worst, profit_percent)
    return is_broke, is_profit, profit_percent, result

def bettor_pool(strategy, sample_size, initial_wager, plays, n, pcolor=None):
    broke_count = 0
    profit_count = 0
    total_profit = 0
    for i in range(sample_size):
        t = bettor(strategy, initial_wager, plays, n, pcolor)
        is_broke, is_profit, profit_percent = t[0], t[1], t[2]
        if is_broke:
            broke_count += 1
        if is_profit:
            profit_count += 1
        total_profit += profit_percent
    broke_count_percent = broke_count / sample_size * 100
    profit_count_percent = profit_count / sample_size * 100
    total_profit_percent = total_profit / sample_size * 100
    print(n, end='\t')
    print(initial_wager, end='\t')
    print(plays, end='\t')
    print(broke_count_percent, end='\t')
    print(profit_count_percent, end='\t')
    print('{:.2f}'.format(total_profit_percent))
    return broke_count_percent, profit_count_percent

def sampling(sample_size, initial_wager, plays):
    if os.path.isfile('result.txt'):
        os.remove('result.txt')
    # result = bettor('martingale', initial_wager, plays, 2, color()[0])[3]
    # result += bettor('martingale_safe', initial_wager, plays, 2, color()[1])[3]
    # plot('sampling.jpg')
    # with open('result.txt', 'a') as doc:
    #   doc.write(result)
    bettor_pool('martingale', sample_size, initial_wager, plays, 2, color()[0])
    plot('sampling1.jpg')
    # bettor_pool('martingale_safe', sample_size, initial_wager, plays, 2, color()[1])
    # plot('sampling2.jpg')

def find_best_query(query, strategy, sample_size, initial_wager, plays, n, start, stop, step):
    """
    n = 1.9 for martingale strategy
    n = 1.0 for dalembert strategy
    plays = 20 - 100 for martingale strategy
    plays = 20 - 100 for dalembert strategy
    initial_wager = 0.1 for martingale strategy
    initial_wager = 0.4 for dalembert strategy
    """
    best_broke_count_percent = 100
    best_profit_count_percent = 0
    print('*' * 72)
    print('strategy:', strategy)
    print('query:', query)
    print('n\tinitial\tplays\tbroke\trich\tprofit')
    for i in float_range(start, stop, step):
        if query == 'initial_wager':
            t = bettor_pool(strategy, sample_size, i, plays, n)
        elif query == 'plays':
            t = bettor_pool(strategy, sample_size, initial_wager, i, n)
        elif query == 'n':
            t = bettor_pool(strategy, sample_size, initial_wager, plays, i)
        curr_broke_count_percent, curr_profit_count_percent = t
        if curr_broke_count_percent < best_broke_count_percent:
            best_broke_count_percent = curr_broke_count_percent
            best_broke_query = i
        if curr_profit_count_percent > best_profit_count_percent:
            best_profit_count_percent = curr_profit_count_percent
            best_profit_query = i
    print('best_broke_query', best_broke_query, end='\t')
    print('best_profit_query', best_profit_query)

def main():
    sample_size = 1000
    initial_wager = 0.1
    plays = 10000
    #find_best_query('initial_wager', 'martingale', sample_size, initial_wager, plays, 2, 0.1, 2.0, 0.1)
    #find_best_query('initial_wager', 'dalembert', sample_size, initial_wager, plays, 1, 0.1, 2.0, 0.1)
    #find_best_query('plays', 'martingale', sample_size, initial_wager, plays, 2, 10, 100, 10)
    #find_best_query('plays', 'dalembert', sample_size, initial_wager, plays, 1, 10, 100, 10)
    #find_best_query('n', 'martingale', sample_size, initial_wager, plays, 2, 0.5, 2.0, 0.1)
    #find_best_query('n', 'dalembert', sample_size, initial_wager, plays, 1, 0.5, 2.0, 0.1)
    sampling(sample_size, initial_wager, plays)

if __name__ == '__main__':
    main()