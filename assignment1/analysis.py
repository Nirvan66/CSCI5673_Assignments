import sys
from statistics import mean, stdev
import matplotlib.pyplot as plt

'''compute_roundtrip_latencies

PARAMS:
    timestamps: list of timestamps of the form (t0, t1, t2, t3)
RETURNS:
    latencies, avg, stdev
        latencies: list of latencies (in u_seconds)
        avg: float average roundtrip latency
        stdev: float standard deviation of the latencies
'''
def compute_roundtrip_latencies(timestamps):
    '''
        formula used:   latency = t3 - t0
    '''
    latency = lambda t: t[3] - t[0]
    ls = [latency(ts) for ts in timestamps]
    ave = mean(ls)
    std = stdev(ls)
    return ls, ave, std




'''compute_offset

PARAMS:
    timestamps: list of timestamps of the form (t0, t1, t2, t3)
RETURNS:
    offsets
        offsets: list of floats of calculated offsets for all increments of time
'''
def compute_offset(timestamps):
    '''
        formula used:   offset = ((t1 - t0) + (t2 - t3))/2
    '''
    offset = lambda t: ((t[1] - t[0]) + (t[2] - t[3]))/2.0
    return [offset(ts) for ts in timestamps]




'''compute_delay

PARAMS:
    timestamps: list of timestamps of the form (t0, t1, t2, t3)
RETURNS:
    delays
        delays: list of floats of calculated delays for all increments of time
'''
def compute_delay(timestamps):
    '''
        formula used:   delay = (t3 - t0) - (t2 - t1)
    '''
    delay = lambda t: (t[3] - t[0]) - (t[2] - t[1])
    return [delay(ts) for ts in timestamps]




'''compute_cristians_server_clock

PARAMS:
    timestamps: list of timestamps of the form (t0, t1, t2, t3)
RETURNS:
    server_times, time_diff, error_bounds
        server_times: list of floats of estimated server time 
        time_diff: list of floats estimated time difference between local clock and servertime
        error_bounds: list of floats of esitmated error bounds
'''
def compute_cristians_server_clock(timestamps):
    '''
        formulas used: 
            t_server = t2 + t1 / 2 (estimated)
            t_new = t_server + (t3 - t0)/2
            diff = abs(t_new - t[3])
            error_bound = (t3 - t0)/ 2
    '''
    server_time = lambda t: (t[2] + t[1]) / 2
    new_time = lambda t, t_server: t_server + (t[3] - t[0])/2
    diff = lambda t, t_new: abs(t_new - t[3])
    error_bound = lambda t: (t[3] - t[0])/2
    
    server_times, time_diffs, error_bounds = [], [], []

    for t in timestamps:
        st = server_time(t)
        nt = new_time(t, st)
        d = diff(t, nt)
        eb = error_bound(t)

        server_times.append(st)
        time_diffs.append(d)
        error_bounds.append(eb)
    return server_times, time_diffs, error_bounds




'''load_timestamps

load in the csv file and convert timestamps to ints

PARAMS:
    csv_file: str file to analyze
RETURNS:
    timestamps
        timestamps: [(int, int, int, int)]
        timesteps are ints in terms of micro seconds
'''
def load_timestamps(csv_file):
    h_to_us = lambda h: h * 3600000000
    m_to_us = lambda m: m * 60000000
    s_to_us = lambda s: s * 1000000
    str_to_t = lambda s: h_to_us(int(s.split(':')[0])) + m_to_us(int(s.split(':')[1])) + s_to_us(int((s.split(':')[2]).split('.')[0])) + int((s.split(':')[2]).split('.')[1])

    timestamps = []
    read_header = False
    with open(csv_file, 'r') as o:
        for line in o:
            if not read_header: 
                read_header = True
                continue
            l = line.split(',')
            ts = (str_to_t(l[0]), str_to_t(l[1]), str_to_t(l[2]), str_to_t(l[3]))
            timestamps.append(ts)
    
    return timestamps 




'''question1

Compute roundtrip latencies along with average and standard deviation for
each scenario, and plot them in a graph
'''
def question1(timestamps):
    ls, avg, std = compute_roundtrip_latencies(timestamps)
    x = [i for i in range(len(ls))]
    plt.plot(x, ls, label='latencies')
    plt.plot(x, [avg for _ in range(len(ls))], 'r-', label='average latency')
    plt.plot(x, [std for _ in range(len(ls))], 'g-', label='standard deviation')
    plt.xticks([0, len(ls)/2, len(ls)], ['0', '1', '2'])
    plt.xlabel('time (hours)')
    plt.ylabel('latency (micro seconds)')
    plt.legend()
    plt.show()
     



'''question3

Compute the offset (oi) and delay (di) for each of the measurements for
each scenario using the NTP formula and plot them in a graph (x-axis: measurement #;
y-axis: oi or di)
'''
def question3(timestamps):
    offsets = compute_offset(timestamps)
    delays = compute_delay(timestamps)
    x = [i for i in range(len(timestamps))]
    plt.plot(x, offsets, label='offsets')
    plt.plot(x, delays, 'r-', label='delays')
    plt.xlabel('measurement number')
    plt.ylabel('micro seconds')
    plt.legend()
    plt.show() 




'''question4

Compute server clock time estimate using the Cristian’s clock
synchronization algorithm, and plot the difference between the local clock and the
estimated server clock values for each scenario

Using this estimate, calculate the error bounds
for the synchronized time.
'''
def question4(timestamps):
    server_times, time_diff, error_bounds = compute_cristians_server_clock(timestamps)
    x = [i for i in range(len(timestamps))]
    plt.plot(x, time_diff, label='estimated time diff')
    plt.plot(x, error_bounds, 'r-', label='error bounds')
    plt.xlabel('measurement nunber')
    plt.ylabel('micro seconds')
    plt.legend()
    plt.show() 




'''analyze

main function used in programming assignment 1 to perform
desired analysis

PARAMS:
    csv_file: str file to analyze
RETURNS:
    None
'''
def analyze(csv_file):
    timestamps = load_timestamps(csv_file)
    question1(timestamps)
    question3(timestamps)
    question4(timestamps)

if __name__ == '__main__':
    args = sys.argv
    if len(sys.argv) < 2:
        print('usage: python3 analysis.py <name of csv file to analyze>')
        sys.exit()
    csv_file = sys.argv[1]
    analyze(csv_file)
