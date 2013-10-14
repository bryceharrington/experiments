#!/usr/bin/env python
# - coding: utf-8 -

# Copyright 2013 Bryce W. Harrington <bryce@bryceharrington.org>
# Dual licensed under the MIT or GPL Version 2 licenses.
# See http://github.com/tbaugis/hamster_experiments/blob/master/README.textile

from lib import graphics

class GridElement(object):
    def __init__(self, i, j):
        self.__graphic = None
        self.i = i
        self.j = j

    def set_origin(self, x, y):
        self.graphic.x = x
        self.graphic.y = y

    def draw(self):
        '''Instantiate a graphical object for this element

        Override this routine to provide your own grid
        drawing functionality.
        '''
        return graphics.Rectangle(40, 40, 3, fill='#a3a')

    @property
    def graphic(self):
        if self.__graphic is None:
            self.__graphic = self.draw()
        assert(self.__graphic is not None)
        return self.__graphic


class Grid(graphics.Sprite):
    '''Infinite 2D array of grid elements'''
    def __init__(self, x=0, y=0, x_spacing=50, y_spacing=50):
        '''
        The x,y coordinates is the canvas location for the top left
        origin of the grid.  The x_spacing and y_spacing are the offsets
        of each subsequent grid element's location.  The spacings should
        be equal to the grid element dimensions to make a regular packed grid.
        '''
        graphics.Sprite.__init__(self, x=x, y=y)
        self.x_spacing = x_spacing
        self.y_spacing = y_spacing
        self.__elements = {}
        self.connect("on-render", self.on_render)

    def add(self, e):
        '''Adds an element to the grid at the element's i,j coordinate'''
        if e.i not in self.__elements.keys():
            self.__elements[e.i] = {}
        self.__elements[e.i][e.j] = e

    def get(self, i, j):
        '''Returns the element at the given i,j coordinate'''
        if (i not in self.__elements.keys() or
            j not in self.__elements[i].keys()):
            return None
        return self.__elements[i][j]

    def on_render(self, widget):
        x = 0
        y = 0
        self.graphics.clear()
        self.sprites = []
        for column in self.__elements.values():
            for e in column.values():
                e.set_origin(x, y)
                self.add_child(e.graphic)
                e.graphic.on_render(widget)
                y += self.y_spacing

            # For an offset grid (hexagons, triangles, etc.)
            # TODO: Is this needed for a square grid?
            if e.i % 2 == 0:
                y = 0
            else:
                y -= self.y_spacing/2
            y = 0
            x += self.x_spacing


class Triangle(graphics.Sprite):
    def __init__(self, width=100, height=100, color_foreground="#333", color_stroke="#000", stroke_width=2):
        graphics.Sprite.__init__(self)
        self.width = width
        self.height = height
        self.stroke_width = stroke_width
        self.color_foreground = color_foreground
        self.color_stroke = color_stroke
        self.connect('on-render', self.on_render)

    def on_render(self, sprite):
        self.graphics.clear()
        self.graphics.move_to(0,0)
        self.graphics.line_to(self.width/2, self.height)
        self.graphics.line_to(self.width, 0)
        self.graphics.line_to(0,0)
        self.graphics.set_line_style(self.stroke_width)
        self.graphics.close_path()
        self.graphics.fill_preserve(self.color_foreground)
        self.graphics.stroke(self.color_stroke)


class TriangularGridElement(GridElement):
    def __init__(self, i,j, height,width, **args):
        GridElement.__init__(self, i,j)
        self.height = height
        self.width = width
        self.args = args

    def set_origin(self, x,y):
        if self.i % 2 == 1:
            GridElement.set_origin(self, x, y-self.height)
        else:
            GridElement.set_origin(self, x, y)

    def draw(self):
        t = Triangle(self.width, self.height, **self.args)
        t.interactive = True
        if self.i % 2 == 0:
            t.height = - t.height
        return t


class Scene(graphics.Scene):
    def __init__(self, width, height):
        graphics.Scene.__init__(self)
        bg = graphics.Rectangle(
            width, height, 0, fill="#000")
        self.add_child(bg)

        self.connect('on-mouse-over', self.on_mouse_over)
        self.connect('on-mouse-out', self.on_mouse_out)
        self.create_grid(width, height)

    def create_grid(self, width, height):
        self.size = 60
        self.grid = Grid(x=80, y=80, x_spacing=self.size/2, y_spacing=self.size)
        self.add_child(self.grid)

        cols = 2 * (width - 2 * self.grid.x) / self.size
        rows = 2 * (height - 4 *self.grid.y) / self.size
        for i in range(0,cols):
            for j in range(0,rows):
                if j % 2 == i % 2:
                    e = TriangularGridElement(
                        i,j, height=self.size, width=self.size,
                        color_foreground="#060")
                else:
                    e = TriangularGridElement(
                        i,j, height=self.size, width=self.size,
                        color_foreground="#666")
                self.grid.add(e)

    def on_mouse_over(self, scene, sprite):
        if not sprite: return # ignore blank clicks
        if self.tweener.get_tweens(sprite): return

    def on_mouse_out(self, scene, sprite):
        if not sprite: return # ignore blank clicks


if __name__ == '__main__':
    import gtk

    class BasicWindow:
        def __init__(self):
            window = gtk.Window(gtk.WINDOW_TOPLEVEL)
            window.set_default_size(800, 600)
            window.connect("delete_event", lambda *args: gtk.main_quit())
            window.add(Scene(800, 600))
            window.show_all()

    window = BasicWindow()
    gtk.main()

