from unittest import TestCase

import os

from app.poller import Poller


class TestFilePoller(TestCase):

    def test_that_poller_can_be_created(self):
        p = Poller()
        self.assertIsInstance(p, Poller)

    def test_that_source_file_does_not_exist(self):
        p = Poller()
        p.filename = 'no_exist.txt'
        self.assertEqual(p.poll(), Poller.FILE_DOES_NOT_EXIST)

    def test_that_source_file_has_invalid_content(self):
        p = Poller()
        test_file = os.path.join('test', 'invalid_content.txt')
        p.filename = test_file
        self.assertEqual(p.poll(), Poller.FILES_NOT_READY)

    def test_that_file_upload_is_complete(self):
        p = Poller()
        test_file = os.path.join('test', 'complete.txt')
        p.filename = test_file
        self.assertEqual(p.poll(), Poller.FILES_COMPLETE)

    def test_poller_process(self):
        p = Poller()
        test_file = os.path.join('test', 'complete.txt')
        p.filename = test_file
        p.run()
