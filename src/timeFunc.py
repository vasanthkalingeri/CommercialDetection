"""
    This file contains time related operations, helpful for reading and writing the output.
"""

def get_time_string(tsecs):
    
    """
        Given time in seconds, converts it to string
        Returns: string of the form hh:mm:ss
    """
    
    if type(tsecs) != int:
        return INVALID_TYPE_OF_TIME_ERROR
        
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
    
    """
        Converts a given time string to seconds.
        The time string has to be of the form in hh:mm:ss
        Returns: int, the value of time in seconds
    """
    
    form = tstring.count(":")# to check if h:m:s format or m:s format
    
    if form == 0:
        return INVALID_TIME_FORMAT_ERROR
    
    tstring = tstring.strip()
    time = tstring.split(":")
    time = [int(i) for i in time]
    secs = 0
    for i in range(form + 1):
        secs += time[i] * (60 ** (form - i))
    return secs

def get_delta_string(t1str, t2str):

    """
        Given two time strings of the form hh:mm:ss, finds the difference in seconds between the two.
        Returns: int, difference in seconds of t2str - t1str
    """
    
    t1str = t1str.strip(" ")
    t2str = t2str.strip(" ")
    s1 = get_seconds(t1str)
    s2 = get_seconds(t2str)
    delta = s2 - s1
    
    if delta < 0:
        return INVALID_TIME_DIFFERENCE_ORDER_ERROR
    
    return get_time_string(delta)

