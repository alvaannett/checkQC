from unittest import TestCase

import os

from checkQC.exceptions import RunModeUnknown, ReagentVersionUnknown
from checkQC.run_type_recognizer import RunTypeRecognizer, HiSeq2500, MiSeq, NovaSeq
class TestRunTypeRecognizer(TestCase):

    CONFIG = {"instrument_type_mappings":{"M": "miseq","D": "hiseq2500"}}

    def setUp(self):
        self.runtype_recognizer = RunTypeRecognizer(runfolder=os.path.join(os.path.dirname(__file__),
                                                                           "resources", "Rapid"),
                                                    config=self.CONFIG)

    def test_instrument_type(self):
        expected = "hiseq2500"
        actual = self.runtype_recognizer.instrument_type()
        self.assertEqual(expected, actual.name())

    def test_read_length(self):
        expected = "51"
        actual = self.runtype_recognizer.read_length()
        self.assertEqual(expected, actual)

    def test_run_mode(self):
        expected = "hiseq2500_rapidrun_v2"
        actual = self.runtype_recognizer.instrument_and_reagent_version()
        self.assertEqual(expected, actual)


class TestIlluminaInstrument(TestCase):

    class MockRunTypeRecognizer():
        def __init__(self, run_parameters):
            self.run_parameters = run_parameters

    def setUp(self):
        self.hiseq2500 = HiSeq2500()
        self.miseq = MiSeq()
        self.novaseq = NovaSeq()

    def test_all_is_well(self):
        runtype_dict = {"RunParameters": {"Setup": {"RunMode": "RapidHighOutput", "Sbs": "HiSeq SBS Kit v4"}}}
        mock_runtype_recognizer = self.MockRunTypeRecognizer(run_parameters=runtype_dict)

        actual = self.hiseq2500.reagent_version(mock_runtype_recognizer)

        expected = "rapidhighoutput_v4"

        self.assertEqual(actual, expected)

    def test_wrong_runmode(self):
        runtype_dict = {"RunParameters": {"Setup": {"Sbs": "HiSeq SBS Kit v4"}}}
        mock_runtype_recognizer = self.MockRunTypeRecognizer(run_parameters=runtype_dict)

        with self.assertRaises(RunModeUnknown):
            self.hiseq2500.reagent_version(mock_runtype_recognizer)

    def test_wrong_reagent(self):
        runtype_dict = {"RunParameters": {"Setup": {"RunMode": "RapidHighOutput"}}}
        mock_runtype_recognizer = self.MockRunTypeRecognizer(run_parameters=runtype_dict)

        with self.assertRaises(ReagentVersionUnknown):
            self.hiseq2500.reagent_version(mock_runtype_recognizer)

    def test_miseq_reagent_version(self):
        runtype_dict = {"RunParameters": {"ReagentKitVersion": "Version2"}}
        mock_runtype_recognizer = self.MockRunTypeRecognizer(run_parameters=runtype_dict)

        actual = self.miseq.reagent_version(mock_runtype_recognizer)

        expected = "v2"

        self.assertEqual(actual, expected)

    def test_miseq_unknown_reagent_version(self):
        runtype_dict = {"RunParameters": {"foo": "bar"}}
        mock_runtype_recognizer = self.MockRunTypeRecognizer(run_parameters=runtype_dict)

        with self.assertRaises(ReagentVersionUnknown):
            self.miseq.reagent_version(mock_runtype_recognizer)

    def test_novaseq_reagent_version_S1(self):
        runtype_dict = {"RunParameters": {"RfidsInfo": {"FlowCellMode": "S1"}}}
        mock_runtype_recognizer = self.MockRunTypeRecognizer(run_parameters=runtype_dict)

        actual = self.novaseq.reagent_version(mock_runtype_recognizer)
        expected = "S1"

        self.assertEqual(actual, expected)

    def test_novaseq_reagent_version_raises(self):
        runtype_dict = {"RunParameters": {"RfidsInfo": {"NoFlowCellMode": "S1"}}}
        mock_runtype_recognizer = self.MockRunTypeRecognizer(run_parameters=runtype_dict)

        with self.assertRaises(ReagentVersionUnknown):
            self.novaseq.reagent_version(mock_runtype_recognizer)
