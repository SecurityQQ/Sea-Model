import random
from random import choice
from enum import Enum
from copy import copy

class Clock(object):
    def __init__(self, start_time=0):
        self._time = start_time

    def tick(self):
        self._time += 1

    @property
    def time(self):
        return self._time


class SeaObject(object):

    def __init__(self, table, x, y):
        """
        :param table: reference to table, where SeaObject inhabits
        :param x: 0 axis coordinate on the table
        :param y: 1 axis coordinate on the table
        """

        self._table = table
        self._x = x
        self._y = y
        self._type = type
        self.alive = True

    @property
    def table(self):
        return self._table

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def thumbnail(self):
        return 'X'


class SeaAssignError(Exception):

    def __init__(self, x, y):
        self.coords = (x, y)

    def __str__(self):
        return repr(self.coords)

class Sea(object):

    def __init__(self, size, clock=Clock(), predator_death_interval=15, logging=True):
        self._buffer = [[None for i in range(size[0])] for j in range(size[1])]
        self._clock = clock
        self.creatures = []
        self.predator_death_interval = predator_death_interval
        self.logging = logging
        self.__dead_creatures = []

    @property
    def clock(self):
        return self._clock

    def adjecent_objects(self, x, y):
        possible_offsets = [(-1, 0), (1, 0), (0, 1), (0, -1)]
        objects = {'empty': [],
                    'victims': [] }
        for i, j in possible_offsets:
            try:
                if self._buffer[x + i][y + j] is None or not self._buffer[x + i][y + j].alive:
                    objects['empty'].append((x + i, y + j))
                elif isinstance(self._buffer[x + i][y + i], SeaVictim) and self._buffer[x + i][y + j].alive:
                    objects['victims'].append((x + i, y + j))
            except IndexError:
                pass
        return objects



    def is_spawn_time(self, time, spawn_param):
        return time % spawn_param == 0

    def begin_simulation(self, time_period, spawn_param=3):
        finish_time = self.clock.time + time_period
        while (self.clock.time < finish_time):
            if self.logging:
                print('Time: %d' % self.clock.time)
                print('Victims: %d, Predators: %d' % self.info)
                print(self)
                print()

            creatures_copy = copy(self.creatures)
            for item in creatures_copy:
                x = item.x
                y = item.y
                if isinstance(self._buffer[x][y], SeaPredator):
                    if self._buffer[x][y].death_time <= self.clock.time:
                        print("DEATH TIME: ", self._buffer[x][y].x, self._buffer[x][y].y)
                        self._buffer[x][y].alive = False
                if not self._buffer[x][y].alive:
                    continue
                if self.is_spawn_time(self.clock.time, spawn_param):
                    self._spawn_simulation(self._buffer[x][y])
                else:
                    print("prepare for move")
                    print(self._buffer[x][y].x, self._buffer[x][y].y)
                    self._move_simulation(self._buffer[x][y])

            for cr in self.creatures:
                if cr.alive == False:
                    self._buffer[cr.x][cr.y] = None
            self.creatures = list(filter(lambda x: x is not None, self.creatures))


            self.clock.tick()


        if self.logging:
            print('Predators: %d, Victims: %d' % self.info)
            print(self)
            print()
            print('Successfully finished')



    def _move_simulation(self, creature):
        print("move Simulation: ", creature.x, creature.y)
        x, y = creature.x, creature.y
        adj_objects = self.adjecent_objects(x, y)

        if isinstance(creature, SeaPredator):
            if len(adj_objects['victims']) > 0:
                x_victim, y_victim = choice(adj_objects['victims'])
                creature.kill(x_victim, y_victim)
                return

        if len(adj_objects['empty']) == 0:
            return

        if isinstance(creature, SeaCreature):
            x_next, y_next = choice(adj_objects['empty'])
            creature.move(x_next, y_next)

    def _spawn_simulation(self, creature):
        x, y = creature.x, creature.y
        adj_objects = self.adjecent_objects(x, y)

        if isinstance(creature, SeaCreature) and len(adj_objects['empty']) > 0:
            x_child, y_child = choice(adj_objects['empty'])
            self.__add_object(x_child, y_child, creature.spawn_new(x_child, y_child))

    def __str__(self):
        return '\n'.join([str(list(map(lambda obj: ' ' if (obj is None or not obj.alive) else obj.thumbnail, row))) for row in self._buffer])

    def empty_at(self, x, y):
        return self._buffer[x][y] is None or (self._buffer[x][y].alive == False)

    def add_object(self, x, y, creature_class):
        self.__add_object(x, y, creature_class(self, x, y))

    def __add_object(self, x, y, creature):
        if self.empty_at(x, y):
            self._buffer[x][y] = creature
            self.creature_spawned_at(x, y)
        else:
            raise SeaAssignError(x, y)

    @property
    def number_of_victims(self):
        return len(list(filter(lambda obj: isinstance(obj, SeaVictim), self.creatures)))

    @property
    def number_of_predators(self):
        return len(list(filter(lambda obj: isinstance(obj, SeaPredator), self.creatures)))

    @property
    def info(self):
        return self.number_of_victims, self.number_of_predators

    def creature_died_at(self, x, y):
        if self.logging:
            print('Died object at: %d, %d' % (x, y))
        self._buffer[x][y].alive = False

    def creature_spawned_at(self, x, y):
        if self.logging:
            print('Spawned object at: %d, %d' % (x, y))

        if isinstance(self._buffer[x][y], SeaCreature):
            self.creatures.append(self._buffer[x][y])

    def creature_was_moved(self, x_from, y_from, x_to, y_to):
        if self.logging:
            print('Object moved from %d, %d to %d, %d' % (x_from, y_from, x_to, y_to))
        if isinstance(self._buffer[x_from][y_from], SeaCreature):
            if self.empty_at(x_to, y_to):
                self._buffer[x_to][y_to] = self._buffer[x_from][y_from]
            else:
                raise SeaAssignError(x_to, y_to)
        else:
            raise SeaAssignError(x_from, y_from)
        self._buffer[x_from][y_from] = None



class SeaCreature(SeaObject):

    def spawn_new(self, x, y):
        return SeaCreature(self.table, x, y)

    def move(self, x, y):
        old_x = self.x
        old_y = self.y
        self._x = x
        self._y = y
        self.table.creature_was_moved(old_x, old_y, x, y)


class SeaVictim(SeaCreature):

    def spawn_new(self, x, y):
        return SeaVictim(self.table, x, y)

    @property
    def thumbnail(self):
        return 'V'


class SeaPredator(SeaCreature):

    def __init__(self, table, x, y):
        super(SeaCreature, self).__init__(table, x, y)
        self.death_time = self.table.clock.time + self.table.predator_death_interval

    def spawn_new(self, x, y):
        return SeaPredator(self.table, x, y)

    def kill(self, x, y):
        print("Predator %d %d kills %d %d" %(self.x, self.y, x, y))
        self.death_time = self.table.clock.time + self.table.predator_death_interval
        self.table.creature_died_at(x, y)
        self.move(x, y)

    @property
    def thumbnail(self):
        return 'P' + str(self.death_time - self.table.clock.time)
#

random.seed(41)
sea = Sea((10, 10), predator_death_interval=4, logging=True)
sea.add_object(2, 2, SeaPredator)
sea.add_object(3, 2, SeaVictim)
sea.begin_simulation(time_period=6, spawn_param=4)