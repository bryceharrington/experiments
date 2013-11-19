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

    def set(self, i, j, e):
        self.__elements[i][j] = e

    def on_render(self, widget):
        x = 0
        y = 0
        self.graphics.clear()
        self.sprites = []
        for column in self.__elements.values():
            for e in column.values():
                e.set_origin(x, y)
                if type(e) == TriangularGridElement:
                    e.on_render(e.graphic)
                else:
                    e.graphic.on_render(widget)
                self.add_child(e.graphic)
                y += self.y_spacing
            y = 0
            x += self.x_spacing

    # TODO: Maybe change this to an __iter__ and yield?
    def elements(self):
        for row in self.__elements.values():
            for col in row.values():
                yield col


class Triangle(graphics.Sprite):
    def __init__(self, i, j, width=100, height=100, color_foreground="#333", color_stroke="#000", stroke_width=2, on_click=None):
        graphics.Sprite.__init__(self)
        self.i = i
        self.j = j
        self.width = width
        self.height = height
        self.stroke_width = stroke_width
        self.color_foreground = color_foreground
        self.color_stroke = color_stroke
        #self.connect('on-render', self.on_render)
        #if on_click is not None:
        #    self.connect('on-click', on_click)

class TriangularGridElement(GridElement):
    x_spacing_factor = 0.5
    y_spacing_factor = 1
    def __init__(self, i,j, height,width, **args):
        GridElement.__init__(self, i,j)
        self.height = height
        self.width = width
        self.stroke_width = 2
        self.color_foreground = args['color_foreground']
        self.color_stroke = "#000"
        self.args = args
        self.args['stroke_width'] = 2
        self.args['color_stroke'] = "#000"

    def set_origin(self, x,y):
        if self.i % 2 == 0:
            GridElement.set_origin(self, x, y)
        else:
            GridElement.set_origin(self, x, y+self.height)

    def on_render(self, sprite):
        sprite.graphics.clear()
        if self.i % 2 == 1:
            sprite.graphics.triangle(0,0, self.width,-1 * self.height)
        else:
            sprite.graphics.triangle(0,0, self.width,self.height)
        sprite.graphics.set_line_style(self.stroke_width)
        sprite.graphics.fill_preserve(self.color_foreground)
        sprite.graphics.stroke(self.color_stroke)

    def on_over(self, sprite):
        if not sprite: return # ignore blank clicks
        tmp = self.color_foreground
        self.color_foreground = self.color_stroke
        self.color_stroke = tmp
        print sprite.i, sprite.j, type(sprite)

    def on_out(self, sprite):
        if not sprite: return # ignore blank clicks
        tmp = self.color_foreground
        self.color_foreground = self.color_stroke
        self.color_stroke = tmp

    def draw(self):
        t = Triangle(self.i, self.j, self.width, self.height, **self.args)
        t.interactive = True
        t.connect('on-render', self.on_render)
        t.connect('on-mouse-over', self.on_over)
        t.connect('on-mouse-out', self.on_out)
        if 'on_click' in self.args.keys():
            t.connect('on-click', self.args['on_click'])
        if self.i % 2 == 1:
            t.height = -1 * t.height
        return t


class Rectangle(graphics.Sprite):
    def __init__(self, i, j, width=100, height=100, color_foreground="#333", color_stroke="#000", stroke_width=2, on_click=None):
        graphics.Sprite.__init__(self)
        self.i = i
        self.j = j
        self.width = width
        self.height = height
        self.stroke_width = stroke_width
        self.color_foreground = color_foreground
        self.color_stroke = color_stroke
        self.connect('on-render', self.on_render)
        if on_click is not None:
            self.connect('on-click', on_click)

    def on_render(self, sprite):
        self.graphics.clear()
        self.graphics.rectangle(0, 0, self.width, self.height)
        self.graphics.set_line_style(self.stroke_width)
        self.graphics.fill_preserve(self.color_foreground)
        self.graphics.stroke(self.color_stroke)


class RectangularGridElement(GridElement):
    x_spacing_factor = 1
    y_spacing_factor = 1
    def __init__(self, i,j, height,width, **args):
        GridElement.__init__(self, i,j)
        self.height = height
        self.width = width
        self.args = args

    def set_origin(self, x,y):
        GridElement.set_origin(self, x, y)

    def draw(self):
        t = Rectangle(self.i, self.j, self.width, self.height, **self.args)
        t.interactive = True
        return t


class Hexagon(graphics.Sprite):
    def __init__(self, i, j, width=100, height=100, color_foreground="#333", color_stroke="#000", stroke_width=2, on_click=None):
        graphics.Sprite.__init__(self)
        self.i = i
        self.j = j
        self.width = width
        self.height = height
        self.stroke_width = stroke_width
        self.color_foreground = color_foreground
        self.color_stroke = color_stroke
        self.connect('on-render', self.on_render)
        if on_click is not None:
            self.connect('on-click', on_click)

    def on_render(self, sprite):
        self.graphics.clear()
        self.graphics.hexagon(0,0, self.height)
        self.graphics.set_line_style(self.stroke_width)
        self.graphics.fill_preserve(self.color_foreground)
        self.graphics.stroke(self.color_stroke)


class HexagonalGridElement(GridElement):
    x_spacing_factor = 0.75
    y_spacing_factor = 0.866
    def __init__(self, i,j, height,width, **args):
        GridElement.__init__(self, i,j)
        self.height = height
        self.width = width
        self.args = args

    def set_origin(self, x,y):
        if self.i % 2 == 1:
            GridElement.set_origin(self, x, y + self.height/2 * 0.866)
        else:
            GridElement.set_origin(self, x, y)

    def draw(self):
        t = Hexagon(self.i, self.j, self.width, self.height, **self.args)
        t.interactive = True
        return t


class Scene(graphics.Scene):
    ELEMENT_CLASSES = [
        RectangularGridElement,
        HexagonalGridElement,
        TriangularGridElement,
        ]

    def __init__(self, width, height):
        graphics.Scene.__init__(self)
        self.background_color = "#000"
        self.element_number = 0
        self.size = 60

        self.connect('on-mouse-over', self.on_mouse_over)
        self.connect('on-mouse-out', self.on_mouse_out)
        self.create_grid(width, height)

    def create_grid(self, width, height):
        self.grid = Grid(x=40, y=40, x_spacing=self.size, y_spacing=self.size)
        self.add_child(self.grid)

        cols = (width - 2 * self.grid.x) / self.size
        rows = (height - 4 *self.grid.y) / self.size
        cls = self.ELEMENT_CLASSES[0]
        for i in range(0,cols):
            for j in range(0,rows):
                if j % 2 == i % 2:
                    color = "#060"
                else:
                    color = "#666"
                e = cls(i,j, height=self.size, width=self.size,
                        color_foreground=color)
                self.grid.add(e)

        self.grid.x_spacing = self.size * e.x_spacing_factor
        self.grid.y_spacing = self.size * e.y_spacing_factor

        # Add next and forward links
        e = self.grid.get(0, 0)
        if e:
            e.args['color_foreground'] = "#0a0"
            e.args['on_click'] = self.prev_grid_type
        e = self.grid.get(cols-1, 0)
        if e:
            e.args['color_foreground'] = "#0a0"
            e.args['on_click'] = self.next_grid_type

    def _set_grid_type(self, element_number):
        self.element_number = element_number
        cls = self.ELEMENT_CLASSES[self.element_number]
        for e in self.grid.elements():
            new_e = cls(e.i, e.j, self.size, self.size, **e.args)
            self.grid.set(e.i, e.j, new_e)
        self.grid.x_spacing = self.size * new_e.x_spacing_factor
        self.grid.y_spacing = self.size * new_e.y_spacing_factor
        self.grid.on_render(new_e)

    def prev_grid_type(self, widget, event):
        self._set_grid_type( (self.element_number - 1) % len(self.ELEMENT_CLASSES))

    def next_grid_type(self, widget, event):
        self._set_grid_type( (self.element_number + 1) % len(self.ELEMENT_CLASSES))

    def on_mouse_over(self, scene, sprite):
        if not sprite: return # ignore blank clicks
        if self.tweener.get_tweens(sprite): return
        tmp = sprite.color_foreground
        sprite.color_foreground = sprite.color_stroke
        sprite.color_stroke = tmp
        print sprite.i, sprite.j, type(sprite)

    def on_mouse_out(self, scene, sprite):
        if not sprite: return # ignore blank clicks
        tmp = sprite.color_foreground
        sprite.color_foreground = sprite.color_stroke
        sprite.color_stroke = tmp


if __name__ == '__main__':
    import gtk

    class BasicWindow:
        def __init__(self):
            window = gtk.Window(gtk.WINDOW_TOPLEVEL)
            window.set_default_size(800, 800)
            window.connect("delete_event", lambda *args: gtk.main_quit())
            window.add(Scene(800, 800))
            window.show_all()

    window = BasicWindow()
    gtk.main()
