# This code adds the path to the sys which allows it to be run from the console outside the IDE.
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ConferenceScraperApp import app
if __name__ == '__main__':
    app.run(sys.argv[1:])
