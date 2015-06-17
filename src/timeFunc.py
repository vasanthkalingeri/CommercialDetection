def get_time_string(tsecs):
    
    m, s = divmod(tsecs, 60)
    h, m = divmod(m, 60)
    h = str(int(h))
    m = str(int(m))
    s = str(int(s))
    h = "0"*(2 - len(h)) + h
    s = "0"*(2 - len(s)) + s
    m = "0"*(2 - len(m)) + m
    time_string = h + ":" + m + ":" + s
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
    """Finds s2 - s1 """
    t1str = t1str.strip(" ")
    t2str = t2str.strip(" ")
    s1 = get_seconds(t1str)
    s2 = get_seconds(t2str)
    delta = s2 - s1
    return get_time_string(delta)

