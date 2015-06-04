def get_time_string(tsecs):
    
    m, s = divmod(tsecs, 60)
    h, m = divmod(m, 60)
    h = str(int(h))
    m = str(int(m))
    s = str(int(s))
    h = "0"*(len(h) - 2) + h
    s = "0"*(len(s) - 2) + s
    m = "0"*(len(m) - 2) + m
    time_string = str(int(h)) + ":" + str(int(m)) + ":" + str(int(s))
    return time_string

def get_seconds(tstring):
    
    form = tstring.count(":")# to check if h:m:s format or m:s format
    tstring = tstring.strip()
    time = tstring.split(":")
    time = [int(i) for i in time]
    secs = 0
    for i in range(form + 1):
        secs += time[i] * (60 ** (form - i))
    return secs

def get_delta_string(t1str, t2str):
    
    t1str = t1str.strip(" ")
    t2str = t2str.strip(" ")
    s1 = get_seconds(t1str)
    s2 = get_seconds(t2str)
    delta = s2 - s1
    return get_time_string(delta)
