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
from base64 import b64encode
from datetime import datetime

from gi.repository import Gtk
import pygame
import pygame.camera
from pygame.locals import *
from jarabe.journal.objectchooser import ObjectChooser
from gettext import gettext as _

from sugar3.datastore import datastore


class Camera(object):

    def image_chooser(self, args, parent, request):
        chooser = ChooseImage(parent, request)
        chooser.show_image_chooser()

    def webcam(self, args, parent, request):
        img = pygame_camera()
        if img:
            parent.send_result(request, img)
        parent.send_error(request, 'Error')


class ChooseImage(object):

    def __init__(self, parent, request):
        self._parent = parent
        self._request = request

    def __chooser_response_cb(self, chooser, response_id):
        if response_id == Gtk.ResponseType.ACCEPT:
            object_id = chooser.get_selected_object_id()
            selected_object = datastore.get(object_id)
            image_path = selected_object.file_path

            with open(image_path) as f:
                string = f.read()

            encoded_string = b64encode(string)

            chooser.destroy()
            self._parent._client.send_result(self.request, encoded_string)
        else:
            chooser.destroy()
            self._parent._client.send_result(self.request, '')

    def show_image_chooser(self, parent):
        chooser = ObjectChooser(self._parent._activity, what_filter='Image')
        chooser.connect('response', self.__chooser_response_cb)
        chooser.show()


def pygame_camera():
    os.environ['SDL_VIDEO_CENTERED'] = '1'

    pygame.init()
    pygame.camera.init()

    screen = pygame.display.set_mode((640, 480), pygame.NOFRAME)

    pygame.display.set_caption(_('Click anywhere to take a photograph'))

    camlist = pygame.camera.list_cameras()
    if not camlist:
        return ''

    cam = pygame.camera.Camera(camlist[0], (640, 480))
    cam.start()

    while True:
        cam_image = cam.get_image()
        screen.blit(cam_image, (0, 0))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT \
               or (event.type == KEYDOWN and event.key == K_ESCAPE) \
               or (event.type == MOUSEBUTTONDOWN):
                cam.stop()
                pygame.display.quit()
                break

    # FIXME: Have to save to file to get it as a jpg
    filename = '/tmp/{}_{}.jpg'.format(_('Webcam_Image'), snapshot_name())
    pygame.image.save(cam_image, filename)

    with open(filename, 'rb') as f:
        b = f.read()
        return b64encode(b)


def snapshot_name():
    # Return a string of the form yyyy-mm-dd-hms
    today = datetime.today()
    y = str(today.year)
    m = str(today.month)
    d = str(today.day)
    h = str(today.hour)
    mi = str(today.minute)
    s = str(today.second)
    return '%s-%s-%s-%s%s%s' % (y, m, d, h, mi, s)
