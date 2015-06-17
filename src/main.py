from recognize import Recognize
import sys

if sys.argv[1] == "-recognize":
    recog = Recognize(sys.argv[2])
    recog.recognize()

elif sys.argv[1] == "-generate":
    gen = Generate(sys.argv[2], sys.argv[3])
    gen.run()
