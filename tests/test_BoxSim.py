from unittest import TestCase
import numpy as np

from BoxSim import (
   Box,
   Room,
   BoxAlreadyOpened,
   PrisonerStrategy,
   World
)


class Boxtest(TestCase):

    def test_create_box(self):
        """
        tests whether a created box has the correct value stored,
        and whether correct error messages are returned when invalid
        parameters are passed to the box creator. tests that a new box is sealed.
        """

        # correct value stored, try 100 times with random numbers
        # also tests that the new box is sealed
        for _ in range(100):
            random_number = np.random.randint(1, 1000)
            my_box = Box(random_number)
            self.assertEqual(random_number, my_box.value, 'box creation failed')
            self.assertFalse(my_box.opened, 'box is not sealed')

        # error if invalid type passed
        self.assertRaises(ValueError, Box, 2.5)
        self.assertRaises(ValueError, Box, 'bunnies')

    def test_open_box(self):
        """
        tests whether a created box returns the right value when opened.
        tests that the box is properly opened
        """

        for _ in range(100):
            random_value = np.random.randint(1, 1000)
            my_box = Box(random_value)
            self.assertEqual(random_value, my_box.open_box(), msg='box value garbled')


class Roomtest(TestCase):

    def setUp(self) -> None:
        """
        creates a default, repeatable room
        """

        np.random.seed(42)
        self.my_room = Room()

    def test_room_creation(self):
        """
        tests whether 100 boxes have been created
        tests whether the numbers are all unique
        tests whether the numbers match all the values from 1 to 100
        runs each test 100 times to be sure of the results
        """

        truevals = np.arange(1, 101)
        for _ in range(100):
            my_room = Room()
            self.assertEqual(len(my_room.boxes), 100, 'incorrect number of rooms created')
            box_values = [box.open_box() for box in my_room.boxes]
            self.assertEqual(len(np.unique(box_values)), 100, 'non-unique boxes created')
            evals = np.sort(box_values) == truevals
            self.assertEqual(np.min(evals), 1, 'incorrect box values stored')

    def test_open_box_count(self):
        """
        ensures that opened boxes are correctly counted
        """

        my_room = Room()
        test_boxes = [1, 34, 78]
        for box_index in test_boxes:
            _ = my_room.boxes[box_index].open_box()
        self.assertEqual(my_room.count_boxes_opened(), 3, 'incorrect number of boxes counted')

    def test_reseal_boxes(self):
        """
        tests that all boxes are resealed correctly when close_boxes is called
        by randomly opening 60 boxes, then resealing them and verifying their
        sealed status
        """

        my_room = Room()
        box_array = np.arange(0, 100)
        box_choices = np.random.choice(box_array, 60, replace=False)
        for box_index in box_choices:
            _ = my_room.boxes[box_index].open_box()
        self.assertEqual(my_room.count_boxes_opened(), 60, 'boxes not opened appropriately')
        my_room.close_boxes()
        self.assertEqual(my_room.count_boxes_opened(), 0, 'boxes not correctly sealed')

    def test_get_unopened_boxes(self):
        """
        tests whether the unopened box count is returned correctly
        """

        my_room = Room()
        testing_indices = [1, 33, 75, 99]
        remaining_indices = np.arange(1, 101)
        for removal_index in testing_indices:
            remaining_indices = remaining_indices[remaining_indices != removal_index]
        for index in testing_indices:
            _ = my_room.boxes[index-1].open_box()

        self.assertTrue(np.all(remaining_indices == my_room.get_unopened_boxes()), "incorrect unopened boxes returned")

    def test_open_box_in_room(self):
        """
        tests whether opening an already_opened box returns an error
        tests whether opening a specific box returns the correct ticket
        """

        test_index = 34
        test_value = self.my_room.boxes[test_index-1].open_box()
        self.assertEqual(test_value, 29, 'incorrect ticket drawn')
        self.assertRaises(BoxAlreadyOpened, self.my_room.open_box, test_index)


class PrisonerTest(TestCase):

    def setUp(self) -> None:
        """
        create a dummy room to be used in the test
        """

        np.random.seed(42)
        self.room = Room()

    def test_random_strategy(self):

        np.random.seed(42)
        prisoners = PrisonerStrategy(PrisonerStrategy.Strategy.RANDOM)
        drawn_tickets = [prisoners.strat(self.room) for _ in range(5)]
        target_tickets = [4, 83, 91, 49, 55]
        self.assertEqual(drawn_tickets, target_tickets, f"incorrect tickets drawn: {drawn_tickets}")

    def test_follower_strategy(self):

        np.random.seed(42)
        prisoners = PrisonerStrategy(PrisonerStrategy.Strategy.FOLLOWER)
        prisoner_number = 42
        drawn_tickets = []
        current_value = prisoner_number
        for _ in range(5):
            drawn_tickets.append(prisoners.strat(self.room, current_value=current_value))
            current_value = drawn_tickets[-1]
        target_tickets = [35, 94, 83, 38, 66]
        self.assertEqual(drawn_tickets, target_tickets, f"incorrect tickets drawn: {drawn_tickets}")


class WorldTest(TestCase):

    def setUp(self) -> None:

        np.random.seed(42)
        self.world = World(PrisonerStrategy.Strategy.RANDOM)
        # self.random_prisoner = PrisonerStrategy(PrisonerStrategy.Strategy.RANDOM)
        # self.follower_prisoner = PrisonerStrategy(PrisonerStrategy.Strategy.RANDOM)

    def test_reset(self) -> None:

        for _ in range(5):
            self.world.prisoner_strategy.strat(self.world.room)
        self.assertEqual(len(self.world.room.get_unopened_boxes()), 95, "world boxes not opened correctly")
        self.world.reset()
        self.assertEqual(len(self.world.room.get_unopened_boxes()), 100, "world boxes not reset correctly")
