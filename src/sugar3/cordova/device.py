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
import logging

from gi.repository import Gio
import jarabe.config
from gettext import gettext as _

_OFW_TREE = '/ofw'
_PROC_TREE = '/proc/device-tree'
_DMI_DIRECTORY = '/sys/class/dmi/id'
_SN = 'serial-number'
_MODEL = 'openprom/model'
_NOT_AVALIABLE = _('Not available')


class Device:
    def sugar_version(self, args, parent, request):
        parent.send_result(request, jarabe.config.version)

    def sugar_model(self, args, parent, request):
        settings = Gio.Settings('org.sugarlabs.extensions.aboutcomputer')
        hardware_model = settings.get_string('hardware-model')
        parent.send_result(request, hardware_model)

    def sugar_uuid(self, args, parent, request):
        uuid = get_serial_number()
        parent.send_result(request, uuid)


def get_serial_number():
    if os.path.exists(os.path.join(_OFW_TREE, _SN)):
        return _read_file(os.path.join(_OFW_TREE, _SN))

    if os.path.exists(os.path.join(_PROC_TREE, _SN)):
        return _read_file(os.path.join(_PROC_TREE, _SN))

    return _NOT_AVAILABLE


def _read_file(path):
    if os.access(path, os.R_OK) == 0:
        return None

    with open(path, 'r') as f:
        value = f.read()

    if value:
        value = value.strip('\n')
        return value
    else:
        _logger.debug('No information in file or directory: %s', path)
        return None
