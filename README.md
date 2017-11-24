# CommercialDetection
Google Summer of Code 2015 for Red Hen Labs.

## Running the code

comdet.py contains code to generate fingerprint and detect ads.

A dictionary containing database configuarations has to be passed to ComDet() object, the object can then be used to recognize or fingerprint any media file that ffmpeg can access.

Please check comdet.test_generate() and comdet.test_recognize() for more details. 

*Ensure you pass a dictionary with your configurations, although the tests use default config*

# A lot of the ideas are borrowed from https://github.com/worldveil/dejavu
