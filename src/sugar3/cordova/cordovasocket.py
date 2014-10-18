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

import sys
import logging

import device as cordova_Device
import accelerometer as cordova_Accelerometer
import camera as cordova_Camera
import network as cordova_Network
import dialog as cordova_Dialog
import globalization as cordova_Globalization


def call_cordova(plugin_name, function_name, args, parent,request):
    try:
        filecode = getattr(sys.modules[__name__], "cordova_" + plugin_name)

        # The class name for the plugin must be same as the plugin name
        class_ = getattr(filecode, plugin_name)()

        # The service method same as that described for the given class
        service_method = getattr(class_, function_name)

        result = service_method(args, parent, request)
        return result
    except:
        parent._client.send_error(request, "The native func doesn't exist")
