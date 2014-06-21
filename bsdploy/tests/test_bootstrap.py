from mock import patch
from bsdploy import bootstrap_utils as bu


def test_get_realmem():
    with patch('bsdploy.bootstrap_utils.run') as mocked_run:
        mocked_run.return_value = '536805376'
        assert bu.get_realmem() == 512
