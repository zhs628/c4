from typing import Any, Callable
from site_packages.tabulate import tabulate
import time
from site_packages.my_itertools import zip_longest

class GridLines():

    def __init__(
        self,
        x_screen_coordinates: dict[Any, tuple[float, Callable]] = None,
        y_screen_coordinates: dict[Any, tuple[float, Callable]] = None,
        title: str = "GridLines",
        debug: bool = False,
        tablefmt: str = 'grid'):
        
        """
        screen_coordinates 指的是这个线所处位置与屏幕长度的比值, 处于0~1
        """
        self.x_screen_coordinates = x_screen_coordinates or {}
        self.y_screen_coordinates = y_screen_coordinates or {}
        self.x_pixel_coordinates = {}
        self.y_pixel_coordinates = {}
        self.title = title
        self.debug = debug
        self._width = None
        self._height = None
        self.tablefmt = tablefmt
        self.update_size(0,0)


    '''
    每当外部调用它, 就会自动更新刻度并触发绑定的函数
    '''
    def update_size(self, width, height):
        self._width = width
        self._height = height
        self._update_x_pixel_coordinates()
        self._update_y_pixel_coordinates()
        if self.debug:
            print(self)

    def _update_x_pixel_coordinates(self):
        """
        实际的像素刻度
        """
        for key in self.x_screen_coordinates.keys():
            pixel = int(self.x_screen_coordinates[key][0] * self._width)
            func = self.x_screen_coordinates[key][1]
            self.x_pixel_coordinates[key] = (pixel, func)
            func(pixel)

    def _update_y_pixel_coordinates(self):
        """
        实际的像素刻度
        """
        for key in self.y_screen_coordinates.keys():
            pixel = int(self.y_screen_coordinates[key][0] * self._height)
            func = self.y_screen_coordinates[key][1]
            self.y_pixel_coordinates[key] = (pixel, func)
            func(pixel)

    def __str__(self):

        table = [["x_key", "%*100", "px"]]
        
        keys = set(self.x_screen_coordinates.keys())

        for key in keys:
            screen_coord_x = self.x_screen_coordinates[key][0]
            pixel_coord_x = (str(self.x_pixel_coordinates[key][0]) + " / " + str(self._width))
            table.append([key, screen_coord_x, pixel_coord_x])

        x_str = tabulate(table, headers="firstrow", tablefmt=self.tablefmt)

        table = [["y_key", "%*100", "px"]]

        keys = set(self.y_screen_coordinates.keys())

        for key in keys:
            screen_coord_y = self.y_screen_coordinates[key][0]
            pixel_coord_y = (
                self.y_pixel_coordinates[key][0].__str__() + " / " + str(self._height)
            )
            table.append([key, screen_coord_y, pixel_coord_y])

        y_str = tabulate(table, headers="firstrow", tablefmt=self.tablefmt)

        ret: list[str] = []
        max_line_len = max([len(x) for x in x_str.split("\n")])
        for x_line, y_line in list(zip_longest(x_str.split("\n"), y_str.split("\n"), fillvalue="")):
            ret.append(x_line.ljust(max_line_len + 3, " ") + " " * 3 + y_line)

        content = "\n".join(ret)
        
        

        return tabulate(
            [[self.title + "\n    time: " + str(time.time())], [content]],
            headers="firstrow",
            tablefmt=self.tablefmt,
        )

