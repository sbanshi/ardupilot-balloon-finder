import cherrypy
import json
import os
import cv2
import tempfile
from cherrypy.lib.static import serve_file



class Config(object):

    exposed = True

    def __init__(self, config_parser):
        self.config = config_parser

    @cherrypy.expose
    def image(self, blah):
        print "handling image"
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return serve_file(os.path.join(current_dir, 'raw.py'), content_type='text/text')

    def get_config(self):
        """ Return a config as a dictionary"""
        dict = {}
        for section in self.config.sections():
            for option in self.config.options(section):
                dict[section + '.' + option] = self.config.get(section, option)

        return dict

    def handle_set(self, id, newval):
        split = id.split('.')
        section = split[0]
        option = split[1]
        self.config.set(section, option, newval)
        return "%s has been set to %s" % (id, newval)

    def GET(self, id=None, set=None):
        if id == None:
            return json.dumps(self.get_config())
        else:
            # We allow the user to do 'sets' via a query param of the form ?set=value
            #setparam = cherrypy.request.params.get('set')
            if set != None:
                return self.handle_set(id, set)
            else:
                return self.get_config()[id]    

class Image(object):

    exposed = True

    def __init__(self, image_callback):
        self.image_file = tempfile.mktemp(suffix=".jpg")
        self.image_callback = image_callback

    def GET(self, id=None):
        """Write our image to a temp file, then give it back to the user"""
        cv2.imwrite(self.image_file, self.image_callback())
        return serve_file(self.image_file, content_type='image/jpeg')

class Static:
    exposed = True

class Webserver(object):
    def __init__(self, config_parser, image_callback):
        cherrypy.tree.mount(
            Config(config_parser), '/config',
            {'/': {'request.dispatch': cherrypy.dispatch.MethodDispatcher()} } )
        cherrypy.tree.mount(
            Image(image_callback), '/image',
            {'/': {'request.dispatch': cherrypy.dispatch.MethodDispatcher()} } )


        cherrypy.config.update({
                         'server.socket_port': 8081 
                        }) 

        cherrypy.engine.start()
        # cherrypy.engine.block()

    def close(self):
        cherrypy.engine.stop()

if __name__ == '__main__':

    Webserver()
    cherrypy.engine.block()