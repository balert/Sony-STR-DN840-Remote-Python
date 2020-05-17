# Sony-STR-DN840-Remote-Python
Control your STR-DN840 or STR-DN1040 receiver via the network interface.

The application has been written for python3
depending on your system - you may want to edit the sony-str-dn840-controller.py and 
change "#!/usr/bin/env python" to "#!/usr/bin/env python3"

To install on a default Ubuntu 18.04 requires the following steps:
-  apt install python3-requests
-  apt install python3-pip
-  pip3 install paho-mqtt

Check that you have all the required requirements:
-  pip3 check requirements.txt

You need to copy the config.sample.py to config.py
and edit this file to your settings
