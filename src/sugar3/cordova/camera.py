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
import gi
gi.require_version('Gst','1.0')
from gi.repository import Gtk
from gi.repository import GObject,Gdk, Gst
from gi.repository import GdkX11, GstVideo
from gi.repository import GdkPixbuf
import base64
import pygame
import pygame.camera
from pygame.locals import *
from jarabe.journal.objectchooser import ObjectChooser
from gettext import gettext as _

from sugar3.datastore import datastore


GObject.threads_init()
Gst.init(None)


class Camera:

    def image_chooser(self, args, parent, request):
        chooser = ChooseImage(parent, request)
        chooser.show_image_chooser()

    def webcam(self, args, parent, request):
        webcam = Webcam()
        webcam.run(parent,request)
        #filename = webcam.run()
        #fh = open(filename)
        #string = fh.read()
        #fh.close()
        #encoded_string = base64.b64encode(string)
        #parent._client.send_result(request, encoded_string)


class Webcam:
    def __init__(self):
        self.parent=""
        self.request=""
        self.window = Gtk.Window(title="click a photo")
        self.window.connect('destroy', self.quit)
        self.window.set_default_size(800, 450)

        self.drawingarea = Gtk.DrawingArea()
        #self.window.add(self.drawingarea)

        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.window.add(self.vbox)
        self.vbox.pack_start(self.drawingarea, True, True, 0)

        self.button1 = Gtk.Button(label="Click Here")

        self.button1.connect("clicked", self.on_button1_clicked)
        #self.window.add(self.button1)
        self.vbox.pack_start(self.button1, False,True,0)
        # Create GStreamer pipeline
        self.pipeline = Gst.Pipeline()

        # Create bus to get events from GStreamer pipeline
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message::error', self.on_error)

        # This is needed to make the video output in our DrawingArea:
        self.bus.enable_sync_message_emission()
        self.bus.connect('sync-message::element', self.on_sync_message)

        # Create GStreamer elements
        self.src = Gst.ElementFactory.make('autovideosrc', None)
        self.sink = Gst.ElementFactory.make('autovideosink', None)

        # Add elements to the pipeline
        self.pipeline.add(self.src)
        self.pipeline.add(self.sink)

        self.src.link(self.sink)

    def on_button1_clicked(self,widget):
        #xwininfo=0x6004f0
        #GdkPixbuf.Pixbuf.get_formats()
        """
        drawable = self.drawingarea.get_property('window')
        colormap = drawable.get_colormap()
        pixbuf = GdkPixbuf.Pixbuf(Gtk.Gdk.COLORSPACE_RGB, 0, 8, *drawable.get_size())
        pixbuf = pixbuf.get_from_drawable(drawable, colormap, 0,0,0,0, *drawable.get_size()) 
        pixbuf = pixbuf.scale_simple(800,450, Gtk.Gdk.INTERP_HYPER) # resize
        filename = snapshot_name() + '.jpeg'
        pixbuf.save('/home/broot/Documents/image'+filename, 'jpeg')
        fh = open(filename)
        string = fh.read()
        fh.close()
        encoded_string = base64.b64encode(string)
        """
        #self.parent._client.send_result(self.request, encoded_string)

        """	
        self.image1=self.drawingarea.window.get_image(0, 0, 500, 400)
	encoded_string = base64.b64encode(self.image1)
        self.parent._client.send_result(self.request, encoded_string)
        """
        """
        win=self.window
        width, height = win.get_size()
        pixbuf = Gdk.pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, width, height)

        # Retrieve the pixel data from the gdk.window attribute (win.window)
        # of the gtk.window object
        screenshot = pixbuf.get_from_drawable(win.window, win.get_colormap(), 
                                          0, 0, 0, 0, width, height)
        screenshot.save('screenshot.png', 'png')

        #drawable = self.window.get_window()
        #logging.error("drawable: %s : ",drawable)
        """
        
        # Fetch what we rendered on the drawing area into a pixbuf
        drawable = self.drawingarea.get_property('window')
        pixbuf = Gdk.pixbuf_get_from_window(self.drawingarea.get_property('window'),0,0,800,450)
        # Write the pixbuf as a PNG image to disk
        pixbuf.savev('/home/broot/Documents/testimage.jpeg', 'jpeg', [], [])
        filename = '/home/broot/Documents/testimage.jpeg'
        self.pipeline.set_state(Gst.State.NULL)
        Gtk.main_quit() 

        fh = open(filename)
        string = fh.read()
        fh.close()
        encoded_string = base64.b64encode(string)
        self.parent._client.send_result(self.request, encoded_string)       
        #return filename  

    def run(self,parent,request):
        self.parent=parent
        self.request=request
        self.window.show_all()
        # You need to get the XID after window.show_all().  You shouldn't get it
        # in the on_sync_message() handler because threading issues will cause
        # segfaults there.
        self.xid = self.drawingarea.get_property('window').get_xid()
        self.pipeline.set_state(Gst.State.PLAYING)
        Gtk.main()

    def quit(self, window):
        self.pipeline.set_state(Gst.State.NULL)
        Gtk.main_quit()

    def on_sync_message(self, bus, msg):
        if msg.get_structure().get_name() == 'prepare-window-handle':
            print('prepare-window-handle')
            msg.src.set_property('force-aspect-ratio', True)
            msg.src.set_window_handle(self.xid)

    def on_error(self, bus, msg):
        print('on_error():', msg.parse_error())


#webcam = Webcam()
#webcam.run()

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
