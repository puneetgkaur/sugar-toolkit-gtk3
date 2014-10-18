# Copyright (C) 2014, Puneet Kaur
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
import time

ACCELEROMETER_DEVICE = '/sys/devices/platform/lis3lv02d/position'


class Accelerometer(object):

    def get_current_acceleration(self, args, parent, request):
        timestamp = time.time()

        if not os.path.isfile(ACCELEROMETER_DEVICE):
            parent.send_error(request, 'No Accelerometer')

        try:
            with open(ACCELEROMETER_DEVICE) as f:
                string = f.read()
            x, y, z = string[1:-2].split(',')
            accelerometer_obj = {'x': int(x), 'y': int(y),
                                 'z': int(z), 'timestamp': timestamp,
                                 'keepCallback': True}
            parent.send_result(request, accelerometer_obj)
        except ValueError, IndexError:
            parent.send_error(request, 'Error reading from the Accelerometer')
