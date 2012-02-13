#!/usr/bin/env python
# - coding: utf-8 -
# Copyright (C) 2012 Toms Bauģis <toms.baugis at gmail.com>

"""Potential edit activities replacement"""


import gtk
from lib import graphics
import hamster.client
import datetime as dt

colors = ["#A9C2AA", "#9DA1DD", "#DDA59D"]
connector_colors = ["#839684", "#797CAB", "#B88982"]
entry_colors = ["#A9C2AA", "#9DA1DD", "#DDA59D"]

fact_names = []



def delta_minutes(start, end):
    end = end or dt.datetime.now()
    return (end - start).days * 24 * 60 + (end - start).seconds / 60

class Container(graphics.Sprite):
    def __init__(self, width = 100, **kwargs):
        graphics.Sprite.__init__(self, **kwargs)
        self.width = width

        self.connect("on-render", self.on_render)

    def on_render(self, sprite):
        self.graphics.rectangle(0, 0, self.width, 500)
        self.graphics.fill("#fff")


class Entry(graphics.Sprite):
    def __init__(self, width, fact, color, **kwargs):
        graphics.Sprite.__init__(self, **kwargs)
        self.width = width
        self.height = 27
        self.fact = fact
        self.color = color

        time_label = graphics.Label("", color="#000", size=11, x=15, y = 5)
        time_label.text = "%s - " % fact.start_time.strftime("%H:%M")
        if fact.end_time:
            time_label.text += fact.end_time.strftime("%H:%M")
        self.add_child(time_label)

        self.add_child(graphics.Label(fact.activity, color="#000", size=11, x=140, y = 5))


        self.connect("on-render", self.on_render)

    def on_render(self, sprite):
        self.graphics.fill_area(0, 0, self.width, self.height, self.color)




class Scene(graphics.Scene):
    def __init__(self):
        graphics.Scene.__init__(self)

        self.total_hours = 24
        self.height = 500
        self.pixels_in_minute =  float(self.height) / (self.total_hours * 60)

        self.spacing = 1

        self.fact_list = graphics.Sprite(x=40, y=50)
        self.add_child(self.fact_list)

        self.fragments = Container(70)
        self.connectors = graphics.Sprite(x=self.fragments.x + self.fragments.width)
        self.connectors.width = 30

        self.entries = Container(500, x=self.connectors.x + self.connectors.width)

        self.fact_list.add_child(self.fragments, self.connectors, self.entries)

        self.storage = hamster.client.Storage()
        self.date = dt.datetime.combine(dt.date.today(), dt.time()) - dt.timedelta(days=1) + dt.timedelta(hours=5)

        self.date_label = graphics.Label("", size=18, y = 10, color="#444")
        self.add_child(self.date_label)

        self.render_facts()

        self.connect("on-enter-frame", self.on_enter_frame)


    def render_facts(self):
        facts = self.storage.get_facts(self.date)

        self.fragments.sprites = []
        self.connectors.sprites = []
        self.entries.sprites = []

        entry_y = 0

        self.date_label.text = self.date.strftime("%d. %b %Y")

        for i, fact in enumerate(facts):
            if fact.activity not in fact_names:
                fact_names.append(fact.activity)

            color_index = fact_names.index(fact.activity) % len(colors)
            color = colors[color_index]

            #fragments are simple
            fragment_y = int(delta_minutes(self.date, fact.start_time) * self.pixels_in_minute)
            fragment_height = int(delta_minutes(fact.start_time, fact.end_time) * self.pixels_in_minute)
            self.fragments.add_child(graphics.Rectangle(self.fragments.width, fragment_height, fill=color, y=fragment_y))


            entry = Entry(self.entries.width, fact, entry_colors[color_index], y=entry_y)
            self.entries.add_child(entry)
            entry_y += entry.height


        # now order out entries - move them down as much as possible
        for i, entry in reversed(list(enumerate(self.entries.sprites))):
            fragment = self.fragments.sprites[i]

            min_y = 0
            if i > 0:
                prev_sprite = self.entries.sprites[i-1]
                min_y = prev_sprite.y + prev_sprite.height

            entry.y = fragment.y + (fragment.height - entry.height) / 2
            entry.y = max(entry.y, min_y)

            if i < len(self.entries.sprites) - 1:
                next_sprite = self.entries.sprites[i+1]
                max_y = next_sprite.y - entry.height - self.spacing

                entry.y = min(entry.y, max_y)

        # draw connectors
        g = self.connectors.graphics
        g.clear()
        g.set_line_style(width=1)
        self.connectors._sprite_dirty = True

        for fragment, entry in zip(self.fragments.sprites, self.entries.sprites):
            x2 = self.connectors.width


            g.move_to(0, fragment.y)
            g.line_to([(x2, entry.y),
                       (x2, entry.y + entry.height),
                       (0, fragment.y + fragment.height),
                       (0, fragment.y)])
            g.fill(connector_colors[colors.index(fragment.fill)])

        self.connectors.redraw()


    def on_enter_frame(self, scene, context):
        g = graphics.Graphics(context)
        for i in range (self.total_hours):
            hour = self.date + dt.timedelta(hours=i)
            y = delta_minutes(self.date, hour) * self.pixels_in_minute
            g.move_to(0, self.fact_list.y + y)
            g.show_label(hour.strftime("%H:%M"), 10, "#666")




class BasicWindow:
    def __init__(self):
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_default_size(700, 650)
        window.connect("delete_event", lambda *args: gtk.main_quit())

        vbox = gtk.VBox(spacing=10)
        vbox.set_border_width(12)
        self.scene = Scene()
        vbox.pack_start(self.scene)

        button_box = gtk.HBox(spacing=5)
        vbox.pack_start(button_box, False)
        window.add(vbox)

        prev_day = gtk.Button("Previous day")
        next_day = gtk.Button("Next day")
        button_box.pack_start(gtk.HBox())
        button_box.pack_start(prev_day, False)
        button_box.pack_start(next_day, False)

        prev_day.connect("clicked", self.on_prev_day_click)
        next_day.connect("clicked", self.on_next_day_click)

        window.show_all()

    def on_prev_day_click(self, button):
        self.scene.date -= dt.timedelta(days=1)
        self.scene.render_facts()

    def on_next_day_click(self, button):
        self.scene.date += dt.timedelta(days=1)
        self.scene.render_facts()

if __name__ == '__main__':
    window = BasicWindow()
    gtk.main()